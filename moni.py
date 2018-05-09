# -*- coding: utf-8 -*-
import getpass
import os
from datetime import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def share(path):
    sharename = path.split('\\')[-1]
    os.system("runas /user:%userdomain%\%username% net share " + sharename + "=" + path + " /GRANT:everyone,FULL")


class Watcher:
    def __init__(self, path):
        self.observer = Observer()
        self.path = path
        print self.path

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print "Error"

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            if event.event_type == 'created':
                action = ' created '
            elif event.event_type == 'deleted':
                action = ' deleted '
            else:
                action = ''
            with open("msgs.txt", "a") as log_file:
                log_file.write((getpass.getuser()) + action + ' in ' + os.getcwd() + ' on ' + \
                               str(datetime.now()) + '\n')
        elif event.event_type == 'created':
            action = ' created '
        elif event.event_type == 'deleted':
            action = ' deleted '
        elif event.event_type == 'modified':
            action = ' modified '


def monitor(patg):
    w = Watcher(path)
    w.run()
