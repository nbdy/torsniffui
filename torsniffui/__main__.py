from argparse import ArgumentParser
import torsniffui
from torsniffui.libs import Server, Database, WatchDog
from os.path import isdir
from loguru import logger as log


def main():
    ap = ArgumentParser()
    ap.add_argument("-d", "--directory", help="torsniff output directory", default="torsniff_data/")
    ap.add_argument("-db", "--database", help="database name", default="torsniff")
    ap.add_argument("-fdbu", "--force-database-update", help="reindex already existing entries", action="store_true")
    ap.add_argument("-sdbi", "--skip-database-indexing", help="skip indexing of items (converting/inserting)",
                    action="store_true")
    ap.add_argument("-wh", "--web-host", help="web ui address", default="127.0.0.1")
    ap.add_argument("-wp", "--web-port", help="web ui port", default=1668)
    ap.add_argument("-wd", "--web-debug", help="enable flask debugging", action="store_true")
    ap.add_argument("-tdw", "--torrent-decode-warnings", action="store_true", help="show decode warnings")
    a = ap.parse_args()

    if not isdir(a.directory):
        log.error("Directory '{}' does not exist.", a.directory)
        exit()

    torsniffui.TORRENT_DECODE_WARNINGS = a.torrent_decode_warnings

    db = Database(a.database)
    if not a.skip_database_indexing:
        db.index_directory(a.directory, a.force_database_update)
    wd = WatchDog(db, a.directory)
    s = Server(db, a.web_host, a.web_port, a.web_debug)

    try:
        log.info("Starting up.")
        wd.start()
        s.start()
    except KeyboardInterrupt:
        log.info("Shutting down")
        wd.stop()
        s.terminate()


if __name__ == '__main__':
    main()
