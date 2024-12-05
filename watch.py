import os
import time
from enum import Enum
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeType(Enum):
    ADD = 'add'
    DELETE = 'delete'
    MODIFY = 'modify'
    MOVE = 'move'

class ChangeHandler(FileSystemEventHandler):
    """Logs all the events captured."""
    change_cb: Callable[[str, ChangeType], None]

    def __init__(self, change_cb: Callable[[str, ChangeType], None]):
        self.change_cb = change_cb

    def on_modified(self, event):
        if not event.is_directory:
            self.change_cb(event.src_path, ChangeType.MODIFY)

    def on_created(self, event):
        if not event.is_directory:
            self.change_cb(event.src_path, ChangeType.ADD)

    def on_deleted(self, event):
        if not event.is_directory:
            self.change_cb(event.src_path, ChangeType.DELETE)

    def on_moved(self, event):
        if not event.is_directory:
            self.change_cb(f'{event.src_path}|{event.dest_path}', ChangeType.MOVE)

def watch_folder(path_to_watch: str, change_cb: Callable[[str, ChangeType], None]):
    event_handler = ChangeHandler(change_cb)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    print(f"Watching changes in: {path_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
