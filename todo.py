#!/usr/bin/env python

################################################################################
# Author: Mike Brown (m8r0wn), Darnell Martin (darneymartin)
# Description:
################################################################################

import os
import re
import argparse
import threading
from time import sleep
from sys import exit, argv, stdout

################################################################################
#
# Class that inherits the threading.Thread class to create a thread that will be
# supplied a filename as an argument to scan and parse.
#
################################################################################
class ParserThread(threading.Thread):

    #-----------------------------------------------
    # Initializes the object
    #-----------------------------------------------
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename
    #-----------------------------------------------
    # This method will be ran whenever the start
    # method is called.
    #-----------------------------------------------
    def run(self):
        self._running = True
        try:
            with open(self.filename) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            line_count = 0
            for line in content:
                if self.match(line):
                    comment = self.parse(line)
                    print(self.filename +"  " + str(line_count) + "  "+ comment)
                line_count += 1
        except UnicodeDecodeError as e:
            pass
        self._running = False

    #-----------------------------------------------
    # Forces the thread to stop by setting the
    # _running flag equal to False
    #-----------------------------------------------
    def stop(self):
        self._running = False

    #-----------------------------------------------
    # Returns the state of the thread
    # True for running and False for stopped
    #-----------------------------------------------
    def isRunning(self):
        return self._running

    #-----------------------------------------------
    # Returns whether the line contains a match
    #-----------------------------------------------
    def match(self,line):
        regex = re.compile('.*@TODO.*')
        if regex.match(line) is not None:
            return True
        else:
            return False

    #-----------------------------------------------
    # Returns the parsed comment when found
    #-----------------------------------------------
    def parse(self, line):
        regex = re.compile('.*@TODO(.+)')
        m = regex.match(line)
        if m is not None:
            comment = m.group(1)
            comment = comment.strip()
            comment = re.sub('^[/:/-]','',comment)
            comment = comment.strip()
            return comment
        else:
            return "No Comment"

################################################################################
#
# Called by single thread, used to get all files within the directory that was
# supplied by the user OR just the file that was supplied
#
################################################################################
class SearchThread(threading.Thread):

    #-----------------------------------------------
    # Initializes the object
    #-----------------------------------------------
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.path = path
        self.file_queue = []

    #-----------------------------------------------
    # This method will be ran whenever the start
    # method is called.
    #-----------------------------------------------
    def run(self):
        self._running = True
        if os.path.isfile(self.path):
            self.file_queue.append(self.path)
        else:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    self.file_queue.append(os.path.join(root, file))
        self._running = False

    #-----------------------------------------------
    # Returns the state of the thread
    # True for running and False for stopped
    #-----------------------------------------------
    def isRunning(self):
        return self._running

    #-----------------------------------------------
    # Returns the file_queue that is built by the
    # thread
    #-----------------------------------------------
    def getFileQueue(self):
        return self.file_queue

################################################################################
#
# The main function that gets ran whenever the program is ran
#
################################################################################

def main(args):
    print("File\tLine#\tComment")
    try:
        # Launch thread to search directory and place in file queue
        search_thread = SearchThread(args.path[0])
        search_thread.daemon = True
        search_thread.start()

        #Wait for the SearchThread to finish running
        while(search_thread.isRunning()):
            sleep(0.01)

        #Get the list of files
        file_queue = search_thread.getFileQueue()

        #Free up the memory
        del search_thread

        #Start file lookup
        active_threads = []
        while file_queue:
            thread = ParserThread(file_queue.pop(0))
            thread.start()
            active_threads.append(thread)
            while(threading.activeCount() == args.max_threads):
                sleep(0.01)
                for thread in reversed(active_threads):
                    if thread.isRunning() == False:
                        active_threads.remove(thread)

        # Wait for threads to close
        while len(active_threads) > 0:
            sleep(0.01)
            for thread in reversed(active_threads):
                if thread.isRunning() == False:
                    active_threads.remove(thread)
    except Exception as e:
        exit(0)
    exit(0)

################################################################################
################################################################################
if __name__ == '__main__':
    version = "1.0 (Alpha)"
    try:
        args = argparse.ArgumentParser(description="""
                {0}   v.{1}
        --------------------------------------------------
Tool to search through files used to identify @TODO tags.

Notes:


Usage:
    todo -t 30 ./dir
    """.format(argv[0], version), formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        action = args.add_mutually_exclusive_group(required=False)
        args.add_argument('-i', dest='ignore', type=str, default='', help='Ignore files with a certain extentsions')
        args.add_argument('-t', dest='max_threads', type=int, default=6, help='Define max threads (Default: 6)')
        args.add_argument('-v', dest="verbose", action='store_true', help="Give Verbose output")
        args.add_argument(dest='path', nargs='+', help='Target path(s)')
        args = args.parse_args()
        #Start Main
        main(args)
    except Exception as e:
        print("\n[!] An Unknown Event Occured, Closing...")
        exit(1)
    except KeyboardInterrupt:
        print("\n[!] Key Event Detected, Closing...")
        exit(0)
    exit(0)
