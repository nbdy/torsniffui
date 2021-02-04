import pyinotify
from loguru import logger as log
from runnable import Runnable
from torsniffui.libs import Database, Torrent


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, db: Database, table: str):
        pyinotify.ProcessEvent.__init__(self)
        self.db = db
        self.tbl = table

    def process_IN_CREATE(self, event):
        if event.pathname.endswith(".torrent"):
            log.info("File created: '{}'.", event.pathname)
            self.db.upsert(self.tbl, Torrent(event.pathname))


class WatchDog(Runnable):
    def __init__(self, db: Database, directory: str):
        Runnable.__init__(self)
        self.o = pyinotify.WatchManager()
        self.h = EventHandler(db, "torrents")
        self.n = pyinotify.Notifier(self.o, self.h)
        self.w = self.o.add_watch(directory, pyinotify.IN_CREATE, rec=True)
        self.directory = directory

    def run(self) -> None:
        log.info("watching '{}'.", self.directory)
        try:
            self.n.loop()
        except KeyboardInterrupt:
            pass
