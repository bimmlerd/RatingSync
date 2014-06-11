"""
Global constants and configuration shared across the program shall be added here
"""

import sys, os
import json

# paths to config files
client_config_path = "client.conf"
srv_config_path = "server.conf"
client_daemon_pid_path = "/tmp/ratingsync.pid"
srv_daemon_pid_path = "/tmp/ratingsync_server.pid"

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
        
    def check_server(self, input_srv):
        """checks if input is a valid server ip."""
        return True # TODO implement
    
    def check_time(self, input_time):
        """checks if input is a valid syncing intervall time"""
        evaluated = eval(str(input_time))
        if not isinstance(evaluated, int) or evaluated < 1: # TODO figure out a good default value
            return False
        return True
    