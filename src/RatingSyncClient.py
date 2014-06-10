#!/usr/bin/env python

"""
RatingSync synchronizes the ratings of your music collection across multiple platforms.
The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes updated ratings with the server.
Each rating will also contain a change date, so that the synchronization works well.

Author: posedge, phishdev, dbimmler, ...?
"""

# imports n shit
import os
import sys
import argparse
import Ratings
import Song
import json
import LocalDatabase
import time as timemodule

#preferences
class prefs:
    
    """Preferences for the program. Will try to open RatingSync.conf and load the config on initialisation."""
    def __init__(self):
        try:
            config_file = open("RatingSync.conf", "r")
            self.prefs = json.load(config_file)
            config_file.close()
        except:
            pass # well.. there is no file so we shall save it later.
    
    # all the preferences:
    prefs = {"server": None, "path": None, "time": None}
    
    def save(self):
        """write configuration to the default file "RatingSync.conf" """
        try:
            config_file = open("RatingSync.conf", "w")
            json.dump(self.prefs, config_file)
            config_file.close()
        except:
            print "an error occured when trying to write to RatingSync.conf. exiting."
            sys.exit(2)
        
    def setup(self):
        """ask user for the unset preferences and store them in a file"""
        while self.prefs["server"] == None:
            self.prefs['server'] = raw_input("Enter server ip: ")
            # TODO check ip format!!!
        while self.prefs["path"] == None:
            self.prefs["path"] = raw_input("Enter path of music library [.]: ")
            if self.prefs["path"] == "":
                self.prefs["path"] = os.path.realpath(os.curdir)
        while self.prefs["time"] == None:
            self.prefs["time"] = raw_input("Enter sync interval in minutes (min. 1)[20]: ")
            if self.prefs["time"] == "":
                self.prefs["time"] = 20
            else:
                evalinput = eval(self.prefs["time"])
                if not isinstance(evalinput, int) or evalinput < 1: # TODO figure out a good default value
                    self.prefs["time"] = None
        
    def clear(self):
        """clear all preferences"""
        self.prefs = None

"""
# reading tags
def read_tag(item):
    # maybe throw exeption if file is not an mp3 file?
    try:
        song = Song(item)
        ratings = song.Ratings.getRatingsFromItem(item)
        rating = ratings[0].rating
        return Ratings.StarsFromByte(rating, Ratings.RatingProvider.WinAmp)
    except:
        return 0
"""

def parse_args():
    """Initialize the program. Parse arguments and set preferences."""
    # parse arguments
    # top-level parser
    parser = argparse.ArgumentParser(description="Start the Rating syncing client")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbosity (print more about what is done)")
    subparser = parser.add_subparsers()
    # configuration
    conf_parser = subparser.add_parser("config", help="set preferences")
    conf_parser.set_defaults(which="config")
    conf_parser.add_argument("--setup", action="store_true", help="Set all parameters")
    conf_parser.add_argument("--path", help="the path to the directory of your music collection.", type=str)
    conf_parser.add_argument("--server", help="the server to connect to.")
    conf_parser.add_argument("--time", help="the time interval in seconds for syncing the database.", type=int)
    #arg_parser.add_argument("--ratings-format", help="the format for ratings to be saved in files.", type=str)
    #arg_parser.add_argument("--create-playlists", help="automatically create or update playlists for every star rating")
    # run
    run_parser = subparser.add_parser("run", help="start syncing client")
    run_parser.set_defaults(which="run")
    # sync now
    sync_parser = subparser.add_parser("sync", help="sync database now and exit")
    sync_parser.set_defaults(which="sync")
    # run in background
    daemon_parser = subparser.add_parser("daemon", help="run in background") # TODO
    daemon_parser.set_defaults(which="daemon")
    # stop the process in background
    stop_parser = subparser.add_parser("stop", help="stop the process running in background")
    stop_parser.set_defaults(which="stop")
    # parse args
    return parser.parse_args()

def init(args):
    config = prefs()
    if args.which == "config":
        # TODO Check the input of the commands!!!
        if args.setup:
            config.clear()
        if not args.path == None:
            config.prefs["path"] = os.path.abspath(args.path)
        if not args.server == None:
            config.prefs["server"] = args.server
        if not args.time == None:
            config.prefs["time"] = args.time
        if args.setup:
            config.setup()
        config.save()
        sys.exit(0)
    elif args.which == "run":
        config.setup() # make sure everything is set
    elif args.which == "sync":
        config.setup()
    elif args.which == "daemon":
        config.setup()
        # TODO implement
    elif args.which == "stop":
        pass # TODO stop the daemon
    else:
        sys.exit(1)
    return config

# TODO running in background

def start(args, config):
    """start syncing"""
    # check path
    path = config.prefs["path"]
    if not os.path.exists(path):
        print "Invalid path: {0}".format(path)
        config.prefs["path"] = None
        config.setup()
    
    while True:
        # TODO check server avialability first!
        print "Scanning music library..."
        LocalDatabase.collect(config, args.verbose)
        print "Syncing with server..."
        LocalDatabase.upload()
        # TODO await response, commit changes
        
        if args.which == "sync":
            break
        
        if args.verbose:
            print "Next synchronization in {0} minutes. Press ctrl+c to exit.".format(config.prefs["time"])
        timemodule.sleep(config.prefs['time']*60)

def run():
    """run the program according to the preferences/arguments"""
    args = parse_args()
    config = init(args)
    if not args.which == "daemon":
        start(args, config)
    else:
        pass # TODO

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print "Exiting..."