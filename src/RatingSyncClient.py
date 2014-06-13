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
import os, sys
import argparse
from shared import *
import LocalDatabase
import time as timemodule
from daemon import Daemon

""" # I dont see where we are using this in this file.
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

class client_prefs(prefs):
    def __init__(self):
        prefs.__init__(self, client_config_path)
        if self.prefs == None:
            self.prefs = {"server": None, "time": None, "path": None} # Default preferences
    
    def setup(self):
        while not self.check_server(self.prefs["server"]):
            self.prefs["server"] = raw_input("Enter server ip [127.0.0.1]: ")
            if self.prefs["server"] == "":
                self.prefs["server"] = default_server
                
        while self.prefs["path"] == None:
            self.prefs["path"] = raw_input("Enter path of music library [.]: ")
            if self.prefs["path"] == "":
                self.prefs["path"] = os.path.realpath(os.curdir)
        
        while not self.check_time(self.prefs["time"]):
            self.prefs["time"] = raw_input("Enter sync interval in minutes (min. 1)[20]: ")
            if self.prefs["time"] == "": # default value
                self.prefs["time"] = default_time
            else:
                self.prefs["time"] = eval(self.prefs["time"])

def parse_args():
    """Parse arguments passed to the script."""
    
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
    daemon_parser = subparser.add_parser("daemon", help="run in background")
    daemon_parser.set_defaults(which="daemon")
   
    # stop the process in background
    stop_parser = subparser.add_parser("stop", help="stop the process running in background")
    stop_parser.set_defaults(which="stop")
    
    # restart the process in background
    res_parser = subparser.add_parser("restart", help="restart the process running in background")
    res_parser.set_defaults(which="restart")
    
    # parse args
    return parser.parse_args()

def init(args):
    config = client_prefs()
    
    if args.which == "config":
        if args.setup:
            config.clear()
            
        if not args.path == None:
            if config.check_path(os.path.abspath(args.path)):
                config.prefs["path"] = os.path.abspath(args.path)
            
        if not args.server == None:
            if config.check_server(args.server):
                config.prefs["server"] = args.server
            
        if not args.time == None:
            if config.check_time(args.time):
                config.prefs["time"] = args.time

        if args.setup:
            config.setup()
        config.save()
        sys.exit(0)
        
    elif args.which in ["run", "sync", "daemon"]:
        config.setup() # make sure everything is set
    
    elif args.which in ["stop", "restart"]:
        pass
    
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

class rating_daemon(Daemon):
    def __init__(self, pidfile, args, config, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):   
        self.args, self.config = args, config
        Daemon.__init__(self, pidfile, stdin, stdout, stderr)
        
    args = None
    config = None
    
    def run(self):
        start(self.args, self.config)
    
def run():
    """run the program according to the preferences/arguments"""
    args = parse_args()
    config = init(args)
    daemon = rating_daemon(client_daemon_pid_path, args, config)
    
    if args.which in ["run", "sync"]:
        start(args, config)
    elif args.which == "daemon":
        print "RatingSync will now be run in background."
        daemon.start()
    elif args.which == "stop":
        print "If a daemon is running in background, it will now be stopped."
        daemon.stop()
    elif args.which == "restart":
        print "If a daemon is running in background, it will be restarted now."
        daemon.restart()
    else:
        pass

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print "Exiting..."