"""
Global constants and configuration shared across the program shall be added here
"""

import sys, os
import json
import re
from argparse import ArgumentError

# paths to config files
client_config_path = "client.conf"
srv_config_path = "server.conf"
client_daemon_pid_path = "/tmp/ratingsync.pid"
srv_daemon_pid_path = "/tmp/ratingsync_server.pid"

# default values
default_time = 20
default_server = "127.0.0.1"
default_rating_plugin = "winamp"

# network stuff
default_buffer_size = 1024 # TODO figure out an apropriate size
default_tcp_port = 7979 # TODO add settings in preferences

# paths to databases
SRV_DATABASE_PATH = "ServerDatabase"
CLIENT_DATABASE_PATH = "MusicDatabase"

# verbosity and other shared variables
class static:
    verbose = None # this is so to say a static variable        

# preferences
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
            self.prefs = None # well.. there is no file so we shall save it later.
    
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
        if input_srv == None: return False
        parts = input_srv.split('.')
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            print "Set server to ip {0}.".format(input_srv)
            return True
        if re.search("^([a-z0-9](?:[a-z0-9-]*[a-z0-9]))$", input_srv):
            print "Set server to hostname {0}.".format(input_srv)
            return True
        print "Invalid server ip or hostname: {0}".format(input_srv)
        return False
    
    def check_time(self, input_time):
        """checks if input is a valid syncing intervall time"""
        if input_time == None: return False
        evaluated = eval(str(input_time))
        if isinstance(evaluated, int) and evaluated >= 1: # TODO figure out a good default value
            print "Set syncing interval to {0}.".format(input_time)
            return True
        else:
            print "Invalid syncing interval: {0}".format(input_time)
            return False
    
    def check_rating_plugin(self, input_p):
        """check if input is a valid rating plugin."""
        if input_p == None: return False
        elif os.path.exists("rating_plugins" + os.path.sep + input_p + ".py"):
            print "Set rating plugin to {0}".format(input_p)
            return True
        else:
            print "Plugin not fount: {0}".format(input_p)
            return False
        
# Network stuff
class Net_message:
    """
    Messages to send or receive over TCP.
    Make sure TYPE is a 6 characters long string. Preferably use the flags provided in this class.
    Supports data of up to 99 999 999 bytes. (I could use hex numbers to keep the metadata size if that should not be enough)
    """
    
    def __init__(self, type=None, data=None):
        if type and len(type) != self.__meta_type_size:
            raise Exception("Invalid message type")
        self.type = type
        self.data = data
        self.metadata_size = len(self.__symbol_0 + self.__symbol_1) + self.__meta_len_size + self.__meta_type_size
        # make sure the metadata size is a power of 2

    __symbol_0 = "#" # symbol to mark beginning of the metadata and the message as a whole
    __symbol_1 = "$" # symbol to mark ending of metadata and seperate it from the data
    __meta_type_size = 6
    __meta_len_size = 8
    
    def __to_string(self):
        """Returns a string containing the data and information about its message type and length to it can be re-assembled."""
        if self.data: data = self.data # encode data
        else: data = ""
        length = len(data) # size of the data
        length = str(length)
        length = "0" * (self.__meta_len_size - len(length)) + length # fill length metadata to size of 8
        return self.__symbol_0 + self.type + length + self.__symbol_1 + data
        # Format: "#(6 byte: message type)(8 byte: message data size)$(message data)"
    
    def send(self, socket):
        """Send this message from the specified socket."""
        try:
            socket.sendall(self.__to_string())
        except:
            print "Socket error!"
            raise
    
    def receive(self, conn):
        """Receive this message from specified connection or socket, and assembles it to class members type and data. This is Blocking."""
        total_data = ""
        total_data_size = None # how big is the message?
        data_received = 0 # how much data has already been received?

        # receive metadata
        metadata = conn.recv(self.metadata_size)
        # end message?
        if not metadata:
            self.type = self.MESSAGE_END
            return
        
        # parse metadata
        total_data_size = int(metadata[7:15])
        if len(metadata) != self.metadata_size \
            or metadata[0] != self.__symbol_0 \
            or metadata[15] != self.__symbol_1 \
            or not isinstance(total_data_size, int):
            # check message format
            raise Exception("Unrecognized Message: {0}".format(metadata))
        self.type = metadata[1:7]

        # receive Data
        while self.type != self.MESSAGE_END:
            if total_data_size == data_received:
                # if we are done, finish
                break
            elif total_data_size >= data_received + default_buffer_size:
                # if there is more data left than the default buffer size, go with it
                data = conn.recv(default_buffer_size)
            else:
                # get the last chunk of data without affecting the next package
                # note that at this point we are not necessary finished - we might have received less data than proveded in the argument at recv().
                data = conn.recv(total_data_size - data_received)
            if not data:
                raise Exception("Connection lost.")
            total_data += data
            data_received += len(data)
        
        if total_data: # many messages dont actually carry data, they just symbolize something, like "ping" or so
            self.data = total_data
        
    # Message type flags
    # Dont change these!
    MESSAGE_END = "closed" # connection closed
    MESSAGE_PING = "ping__" # client asking server for availability
    MESSAGE_PONG = "pong__" # server answering that he is available
    MESSAGE_BUSY = "busy__" # server answering that he is busy
    MESSAGE_SYNC_TYPE = "snctyp" # client sets syncing type to server, and if one of the databases shall be overridden
    MESSAGE_DATABASE = "data__" # client sending local database to server for comparison
    MESSAGE_LOCAL_CHANGES = "change" # server sending back changes to be made locally
    MESSAGE_ERROR = "error_" # unrecognized request by server
    #MESSAGE_QUIT = "00quit"
