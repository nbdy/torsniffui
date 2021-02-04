from podb import DB, DBEntry
from torrent_parser import TorrentFileParser, InvalidTorrentDataException
import glob
from loguru import logger as log
from os.path import isdir
from os import rename, sep
from io import UnsupportedOperation


def move_faulty_file(path: str, ext: str = ".faulty"):
    rename(path, path + ext)


def get_torrent_name(path: str):
    return path.split(sep)[-1].split(".")[0]


class Torrent(DBEntry):
    def __init__(self, path: str):
        DBEntry.__init__(self)
        self.uuid = get_torrent_name(path)
        try:
            with open(path, 'rb') as fp:
                self.data = TorrentFileParser(fp, encoding="auto").parse()
                self.set_value("name")
                self.set_value("length", func=int)
                self.set_value("piece length", "piece_length", int)
                self.set_value("pieces", "piece_count", len)
                self.set_value("files", "file_count", len)
                self.set_value("publisher")
                self.set_value("publisher-url", "publisher_url")
        except (UnsupportedOperation, UnicodeEncodeError, InvalidTorrentDataException, TypeError) as e:
            log.warning("Could not parse '{}'.", path)
            log.error(e)
            pass

    def set_value(self, k: str, n=None, func=None):
        if not n:
            n = k
        if not func:
            func = str

        i = "info"
        if k in self.data[i].keys():
            setattr(self, n, func(self.data[i][k]))


class Database(DB):
    def __init__(self, name="torsniff"):
        DB.__init__(self, name)

    def index_directory(self, directory: str, force=False):
        if not isdir(directory):
            return False
        if not directory.endswith("/"):
            directory += "/"

        log.info("Indexing '{}'.", directory)
        tbl = "torrents"
        for fp in glob.iglob(directory + "/**/**/*.torrent", recursive=True):
            tn = get_torrent_name(fp)
            if not self.contains(tbl, "uuid", tn) or force:
                self.upsert(tbl, Torrent(fp))
