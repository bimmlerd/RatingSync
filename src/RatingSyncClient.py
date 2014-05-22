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
import sys
import os

# variables n shit
# TODO add default values
music_dir = None # maybe add cureent directory as default value?
server_ip = None
sync_interval_minutes = 60 # Sync once per hour (default value)
config_file = "RatingSync.conf" # Default config file

print_help = False
error = False # Error flag
error_message = None
verbose = False # Verbose flag

def print_info():
    """print info about the usage and arguments of this program and, if specified, an error message."""
    print("Usage: [--config <path-to-config-file>] [--dir <path-to-music-directory>] [--server <server-ip>] [--time <sync time interval>]")
    print("If no options were specified, RatingSync will try to load the default config file RatingSync.conf\n")
    # TODO implement that
    # TODO continuously extend info to be printed about the arguments
    
def read_config(path):
    """Loads settings from the file specified in path."""
    pass
    # TODO implement

# parse arguments
for i in range(1, len(sys.argv)):
    #print(sys.argv[i])
    if sys.argv[i] == "--help":
        print_help = True
        error = False
        break
    elif sys.argv[i] == "--config":
        print("Loading config file...")
        try:
            config_file = sys.argv[i+1]
            i += 1 # skip the next argument as we already processed it
        except:
            error = True
            error_message = "Invalid config file."
        break
    elif sys.argv[i] == "--path":
        print("Loading music directory...")
        try:
            music_dir = sys.argv[i+1] # skip the next argument as we already processed it
            os.chdir(music_dir)
        except:
            error = True
            error_message = "Invalid music directory."
    elif sys.argv[i] == "--server":
        print("(set default server)")
        try:
            server_ip = sys.argv[i+1]
            i += 1 # skip the next argument as we processed it already
        except: 
            # for instance if there is no argument at index i+1 
            # TODO handle stupid arguments not matching an ip address. use regex to do that.
            error = True
            error_message = "Invalid server IP."
    elif sys.argv[i] == "--time":
        try:
            sync_interval_minutes = sys.argv[i+1]
            i += 1 # skip the next argument as we processed it already
        except:
            error = True
            error_message = "No sync time interval specified."
    elif sys.argv[i] == "-v":
        verbose = True
        
# implementation
if error:
    print(error_message)
    print("Exiting...")
elif print_help:
    print_info()
else:
    music_files = []
    # Perform a DFS and put all the ( TODO (regex) music) files in the list music_files
    dfs_stack = [os.curdir]
    while len(dfs_stack) > 0:
        item = dfs_stack.pop()
        if os.path.isdir(item):
            if verbose:
                print("adding directory %s to searching list" % item)
            # push all child files to the stack
            dfs_stack.extend([item + os.sep + c for c in os.listdir(path=item)])
        elif os.path.isfile(item):
            if verbose:
                print("adding file %s to music list (will filter soon)" % item)
            # TODO filter only the mp3 files!
            music_files.append(item)
        else:
            print("error, %s is neither a file nor a directory. exiting." % item)
            break
    print("dfs stack len", len(dfs_stack))
    print("music files len", len(music_files))
    # first I will try a naive implementation using a dict, once that works I will optimize it and find a good data structure

    # TODO implement
#def build_structure():