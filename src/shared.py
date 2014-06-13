"""
Global constants and configuration shared across the program shall be added here
"""

import sys, os
import json
import re

# paths to config files
client_config_path = "client.conf"
srv_config_path = "server.conf"
client_daemon_pid_path = "/tmp/ratingsync.pid"
srv_daemon_pid_path = "/tmp/ratingsync_server.pid"

# default values
default_time = 20
default_server = "127.0.0.1"
default_tcp_port = 7979 # TODO add settings in preferences

# network stuff
default_buffer_size = 1024 # TODO figure out an apropriate size

#preferences
class prefs:
    """Preferences for the program. Will try to open the appropriate config file and load it on initialisation."""
    
    def __init__(self, config_path):
        try:
            self.config_path = config_path
            config_file = open(config_path, "r")
            loaded_prefs = json.load(config_file)
            config_file.close()
            if not loaded_prefs == None:
                self.prefs = loaded_prefs
        except:
            pass # well.. there is no file so we shall save it later.
    
    def save(self):
        """write configuration to the default file "client.conf" """
        try:
            config_file = open(self.config_path, "w")
            json.dump(self.prefs, config_file)
            config_file.close()
        except:
            print "an error occured when trying to write to {0}. exiting.".format(self.config_path)
            sys.exit(2)
        
    def setup(self):
        """
        OVERRIDE THIS!
        ask user for the unset preferences and store them in a file
        """
        pass
        
    def clear(self):
        """clear all preferences"""
        for key in self.prefs: self.prefs[key] = None
        
    def list(self):
        """List all preferences."""
        prefs_list = []
        for key in self.prefs: prefs_list.append("{0}: {1}".format(key, self.prefs[key]))
        return prefs_list
        
    def check_path(self, input_path):
        if not input_path == None:
            print "Set path to {0}.".format(input_path)
            return True
        else:
            print "Invalid path: {0}".format(input_path)
            return False
        
    def check_server(self, input_srv):
        """checks if input is a valid server ip."""
        if re.search(r"^([0-9]{1,3}\.){3}[0-9]{1,3}$", str(input_srv)): # regular expression for an ip address. TODO extend this for hostnames!
            print "Set server to {0}.".format(input_srv)
            return True
        else:
            print "Invalid server ip: {0}".format(input_srv)
            return False
    
    def check_time(self, input_time):
        """checks if input is a valid syncing intervall time"""
        evaluated = eval(str(input_time))
        if isinstance(evaluated, int) and evaluated >= 1: # TODO figure out a good default value
            print "Set syncing interval to {0}.".format(input_time)
            return True
        else:
            print "Invalid syncing interval: {0}".format(input_time)
            return False
# TODO
# add message objects here!
