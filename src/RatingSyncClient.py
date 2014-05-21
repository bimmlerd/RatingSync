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
# TODO add default values
music_dir = None # maybe add cureent directory as default value?
server_ip = None
sync_interval_minutes = 60 # Sync once per hour (default value)
config_file = "RatingSync.conf" # Default config file

print_help = False
error = False # Error flag
error_message = None

def print_info():
    """print info about the usage and arguments of this program and, if specified, an error message."""
    print("Usage: [--path <path>] [--server <server-ip>] [--time <sync time interval>]")
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
            error_message = "No config file specified."
        break
    elif sys.argv[i] ==  "--server":
        print("(set default server)")
        try:
            server_ip = sys.argv[i+1]
            i += 1 # skip the next argument as we processed it already
        except: 
            # for instance if there is no argument at index i+1 
            # TODO handle stupid arguments not matching an ip address. use regex to do that.
            error = True
            error_message = "No server IP specified."
    elif sys.argv[i] == "--time":
        try:
            sync_interval_minutes = sys.argv[i+1]
            i += 1 # skip the next argument as we processed it already
        except:
            error = True
            error_message = "No sync time interval specified."

#        
if error:
    print(error_message)
    print("Exiting...")
elif print_help:
    print_info()
else:
    pass
    # hier kommt die implementation rein
    # zuerst aber muss ich noch ein bisschen rumprobieren. ich versuche erstmal die dateien einzulesen und ein dict/einen baum daraus aufzubauen und auszugeben

    # TODO implement
#def build_structure():