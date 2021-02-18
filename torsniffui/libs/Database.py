from podb import DB, DBEntry
from torrent_parser import TorrentFileParser, InvalidTorrentDataException
import glob
from loguru import logger as log
from os.path import isdir
from os import rename, sep, stat
from io import UnsupportedOperation
from tqdm import tqdm
from multiprocessing import Pool
import torsniffui


def move_faulty_file(path: str, ext: str = ".faulty"):
    rename(path, path + ext)


def get_torrent_name(path: str):
    return path.split(sep)[-1].split(".")[0]


class Torrent(DBEntry):
    def __init__(self, fp: str):
        DBEntry.__init__(self)
        self.uuid = get_torrent_name(fp)

    def set_value(self, data: dict, k: str, n=None, func=None):
        if not n:
            n = k
        if not func:
            func = str

        i = "info"
        if k in data[i].keys():
            setattr(self, n, func(data[i][k]))

    @staticmethod
    def convert(path: str):
        try:
            r = Torrent(path)
            with open(path, 'rb') as fp:
                d = TorrentFileParser(fp, encoding="auto").parse()
                r.set_value(d, "name")
                r.set_value(d, "length", func=int)
                r.set_value(d, "piece length", "piece_length", int)
                r.set_value(d, "pieces", "piece_count", len)
                r.set_value(d, "files", "file_count", len)
                r.set_value(d, "publisher")
                r.set_value(d, "publisher-url", "publisher_url")
                return r
        except (UnsupportedOperation, UnicodeEncodeError, InvalidTorrentDataException, TypeError) as e:
            if torsniffui.TORRENT_DECODE_WARNINGS:
                log.warning("Could not parse '{}'.", path)
                log.error(e)
            return None


class Database(DB):
    torrent_table = "torrents"
    force_indexing = False

    def __init__(self, name="torsniff"):
        DB.__init__(self, name)

    def index_directory(self, directory: str, force=False):
        if not isdir(directory):
            return False
        if not directory.endswith("/"):
            directory += "/"

        log.info("Indexing '{}'.", directory)

        items = list(glob.iglob(directory + "/**/**/*.torrent", recursive=True))

        def get_new_only():
            r = []
            for i in tqdm(items, total=len(items)):
                if not self.find_by_uuid(get_torrent_name(i)):
                    r.append(i)
            return r

        def sort_valid_file():
            r = []
            for i in tqdm(items, total=len(items)):
                if stat(get_torrent_name(i)).st_size > 0:
                    r.append(i)
            return r

        log.info("Sorting out invalid files.")
        items = sort_valid_file()

        if not force:
            log.info("Sorting out already existing items.")
            items = get_new_only()

        log.info("Converting {} items.", len(items))

        torrents = []

        try:
            with Pool() as pool:
                for _ in tqdm(pool.imap_unordered(Torrent.convert, items), total=len(items)):
                    if _ is not None:
                        torrents.append(_)
        except KeyboardInterrupt:
            log.warning("Conversion interrupted. Only {} elements converted.", len(torrents))
            pass

        log.info("Inserting {} items.", len(torrents))

        for _ in tqdm(torrents, total=len(torrents)):
            self.upsert(_)
