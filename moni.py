# -*- coding: utf-8 -*-
import getpass
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
LOG_FILENAME = 'events.log'


def share(path, password):
    sharename = path.split('\\')[-1]
    os.system("start cmd")
    os.system("runas /user:%userdomain%\%username% " + r'"net share ' + sharename + "=" + path + r' /GRANT:everyone,FULL"')
    #os.system(password)
    

def logi():
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug('debug')

logging.info('This is an info message')

def get_my_ip():
    return getpass.getuser()


class Watcher:
    def __init__(self, path):
        self.observer = Observer()
        self.path = path
        print(self.path)

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):

        if event.event_type == 'created':
            path_event = event.src_path
            time_mow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print time_mow,
            print ": {}: ".format(get_my_ip()),
            print "Received created event - %s." % path_event
            logging.info(time_mow)
            logging.info(get_my_ip() + " ,  " + path_event)
            logging.info("\n")

        elif event.event_type == 'deleted':
            path_event = event.src_path
            time_mow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print time_mow,
            print ": {}: ".format(get_my_ip()),
            print "Received deleted event - %s." % path_event
            logging.info(time_mow)
            logging.info(get_my_ip() + " ,  " + path_event)
            logging.info("\n")

        elif event.event_type == 'modified':
            path_event = event.src_path
            time_mow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print time_mow,
            print ": {}: ".format(get_my_ip()),
            print "Received modified event - %s." % path_event
            logging.info(time_mow)
            logging.info(get_my_ip() + " ,  " + path_event)
            logging.info("\n")

        elif event.event_type == 'moved':
            path_event = event.src_path
            time_mow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print time_mow,
            print ": {}: ".format(get_my_ip()),
            print "Received moved event - "+path_event+" to "+event.dest_path
            logging.info(time_mow)
            logging.info(get_my_ip() + " ,  " + path_event)
            logging.info("\n")

        else:
            return None


if __name__ == "__main__":
    logi()
    #path1 = r"c:\tasm\bin"
    path1 = raw_input("your path Blat: ")
    w = Watcher(path1)
    w.run()
