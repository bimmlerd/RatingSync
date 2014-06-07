#!/usr/bin/env python3

"""
RatingSync synchronizes the ratings of your music collection across multiple platforms.
The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes updated ratings with the server.
Each rating will also contain a change date, so that the synchronization works well.

Author: Valentin Trifonov (and soon maybe some more people aswell).
"""

# imports n shit
import os
import sys
import re
import argparse
import Ratings
import Song
import time as timemodule
import json

#preferences
class prefs:
    
    """Preferences for the program. Will try to open RatingSync.conf and load the config on initialisation."""
    def __init__(self):
        try:
            config_file = open("RatingSync.conf", "r")
            self.prefs = json.load(config_file)
        except:
            # well.. there is no file so we shall save it later.
            pass
    
    # all the preferences:
    prefs = {"server": None, "path": None, "time": None, "sync_intervall": None}
    
    def save(self):
        """write configuration to the default file "RatingSync.conf" """
        try:
            config_file = open("RatingSync.conf", "w")
            json.dump(self.prefs, config_file)
        except:
            print "an error occured when trying to write to RatingSync.conf. exiting."
            sys.exit(2)
        
    def setup(self):
        """ask user for the unset preferences and store them in a file"""
        while self.prefs["server"] == None:
            self.prefs['server'] = input("Enter server ip: ")
            # TODO check ip format!!!
        while self.prefs["path"] == None:
            self.prefs["path"] = input("Enter path of music library: ")
        while self.prefs["time"] == None:
            self.prefs["time"] = input("Enter sync interval in seconds (min. 60): ")
            if not isinstance(self.prefs["time"], int) or self.prefs["time"] < 60: # figure out a good default value
                self.prefs["time"] = None
        
    def clear(self):
        """clear all preferences"""
        self.prefs['server'] = None
        self.prefs["path"] = None
        self.prefs["time"] = None
        self.prefs["sync_intervall"] = None

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
# parse args
args = parser.parse_args()

# init
verbose = args.verbose
config = prefs()
if args.which == "config":
    if args.setup:
        config.clear()
    if not args.path == None:
        config.prefs["path"] = os.path.realpath(args.path)
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
    # TODO implement
elif args.which == "sync":
    config.setup()
elif args.which == "daemon":
    config.setup()
    # TODO implement
else:
    sys.exit(1)

# implementation    
starttime = timemodule.time() # performance measuring

os.chdir(config.prefs["path"])
music_files = {}
# Perform a DFS and put all the mp3 files in the list music_files
dfs_stack = [os.path.realpath(os.curdir)]
visited = []
while dfs_stack: # while not empty
    item = dfs_stack.pop()
    
    if item in visited: # make sure there are no cycles
        if verbose:
            print("searched file already: {}".format(item))
        continue
        
    visited.append(item)
    if os.path.isdir(item):
        if verbose:
            print("adding dir to searching list: {}".format(item))
            # push all child files to the stack
        if not os.path.split(item)[1] == "#":
            new_dirs = [os.path.realpath(item + os.sep + c) for c in os.listdir(item)]
            dfs_stack.extend(new_dirs)
    elif os.path.isfile(item):
        if re.search(r".*\.mp3", item):
            rating = read_tag(item)
            if verbose:
                print("adding to music list ({}*): {}".format(rating, item))
            music_files[item] = rating
        elif verbose:
            print("not an mp3 file: {}".format(item))
    else:
        print("error, {} is neither a file nor a directory. exiting.".format(item))
        sys.exit(2)

elapsed = timemodule.time() - starttime

if verbose:
    print "elapsed time: {:.5f}s".format(elapsed)
    print "music files len", len(music_files)
    print "visited len", len(visited)

# first I will try a naive implementation using a dict, once that works I will optimize it and find a good data structure
