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

# variables n shit
# maybe add some default values?
music_dir = None
server_ip = None
sync_interval = None

def print_info():
    # TODO config datei einlesen mit --import argument
    # Set
    print("Usage: [--path <path>] [--server <server-ip>] [--time <sync time interval>]")
    print("If no options were specified, RatingSync will try to load the default config file RatingSync.conf")
    # TODO implement that
    # TODO print some more info about the arguments
    
# parse arguments
for i in range(1, len(sys.argv)):
    #print(sys.argv[i])
    if sys.argv[i] == "--help":
        print_info()
        break
    elif sys.argv[i] == "--config":
        print("(load config file and connect)")
        # TODO implement
        #read_config(sys.argv[i+1])
        # skip the next argument as we already processed it
        # i += 1
    elif sys.argv[i] ==  "--server":
        print("(set default server and connect)")
        try:
            server_ip = sys.argv[i+1]
            # skip the next argument as we processed it already
            i += 1
        except: 
            # for instance if there is no argument at index i+1 
            # TODO handle stupid arguments not matching an ip address. use regex to do that.
            print_info()
        # TODO implemenet
    elif sys.argv[i] == "--time":
        print("(set default file monitoring and sync time interval, and connect)")
        sync_interval = sys.argv[i+1]
        i += 1
        # TODO implement
#else: # if there was no break, start the client and sync
    # TODO implement
    
#def read_config(path):