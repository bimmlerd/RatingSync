#!/usr/bin/env python

"""
Server Code
Tasks:
The server has a local database of songs, their ratings and last-change-date.
On request, compares the received list with the local database. Changes are synchronized in both direcitons:
If the received change is newer, update the local database.
Otherwise, send back a list of changes to be made in the clients music library.
"""

import os, sys, argparse
import socket
import json
import Ratings
import cPickle
import base64
from shared import *
from daemon import Daemon
from SongDatabase import *

class srv_prefs:
    def __init__(self):
        prefs.__init__(self, srv_config_path)
        if self.prefs == None:
            self.prefs = {"pref0": None} # Default preferences
    
    def setup(self):
        pass
    
class Server:
    """This time, I will structure my code better (or so I hope)"""
    
    def __init__(self):
        self._parse_args()
        static.verbose = self.args.verbose
    
    def _parse_args(self):
        """Parse arguments passed to the script."""
        
        # parse arguments
        # top-level parser
        parser = argparse.ArgumentParser(description="Start the Rating syncing server.")
        parser.add_argument("-v", "--verbose", action="store_true", help="verbosity (print more about what is done)")
        subparser = parser.add_subparsers()

        """# configuration
        conf_parser = subparser.add_parser("config", help="set preferences")
        conf_parser.set_defaults(which="config")
        conf_parser.add_argument("--setup", action="store_true", help="Set all parameters")
        conf_parser.add_argument("--path", help="the path to the database?", type=str)"""
        # put the playlist stuff here maybe, with subparsers and everything.
        
        # We dont really need subparsers here, but to stay consistent in the syntax of the usage of this program I will add them here as well.
        run_parser = subparser.add_parser("run", help="start server")
        run_parser.set_defaults(which="run")
        
        # background process
        daemon_parser = subparser.add_parser("daemon", help="run in background")
        daemon_parser.set_defaults(which="daemon")
        
        # stop the process in background
        stop_parser = subparser.add_parser("stop", help="stop the process running in background")
        stop_parser.set_defaults(which="stop")
        
        # restart the process in background
        res_parser = subparser.add_parser("restart", help="restart the process running in background")
        res_parser.set_defaults(which="restart")
        
        # parse args
        self.args = parser.parse_args()
    
    def _handle_request(self, connection, message):
        """This shall be called when data is received, it then handles the input"""
        # implementation
        if message.type == Net_message.MESSAGE_PING:
            if self.args.verbose: print "Client asks for server availability. answering yes."
            pong = Net_message(type=Net_message.MESSAGE_PONG)
            pong.send(connection)
            
        elif message.type == Net_message.MESSAGE_SYNC_TYPE:
            if message.data == "ovrsrv":
                print "Server ratings will be overridden!"
            elif message.data == "ovrlocal":
                print "Client ratings will be overridden!"
            self.synctype = message.data
        
        elif message.type == Net_message.MESSAGE_DATABASE:
            if self.args.verbose: print "Client sent database. Syncing with local database..."
            client_database = SongDatabase()
            client_database.loadFromString(message.data)
            self.client_changes = {}
            
            self.client_changes_count = 0
            self.server_changes_count = 0
            self.server_added_songs_count = 0
            self.unchanged_count = 0
            
            # this will be called for each song in the client database, sorted by key (inorder).
            def item_func(key, song):
                # comparing implementation here
                server_equivalent = self.srv_database.getSong(key, None)
                if server_equivalent == None:
                    print "Adding to server database: {}".format(song.key())
                    self.srv_database.insertSong(song)
                    self.server_added_songs_count += 1
                else:
                    client_rating = song.getRatingStars(Ratings.RatingProvider.WinAmp)
                    server_rating = server_equivalent.getRatingStars(Ratings.RatingProvider.WinAmp)                    
                    if client_rating == server_rating:
                        if static.verbose: print "Same ratings for {}".format(key)
                        self.unchanged_count += 1
                    elif self.synctype != "ovrsrv" and (self.synctype == "ovrlocal" or server_equivalent.lastChanged() > song.lastChanged()):
                        # server file is up to date
                        print "Will be updated in client database: {}".format(key)
                        self.client_changes[key] = server_rating
                        self.client_changes_count += 1
                    else:
                        # client file is up to date
                        print "Updating in server database: {}".format(key)
                        self.srv_database.removeSong(server_equivalent) # again, I might as well have used "song" since the key is the same.
                        song.touch() # since we override this song, we need to set this as the updated version
                        self.srv_database.insertSong(song)
                        # I could have changed the ratings and last-change-date in the song only, but since I dont know if this is a copy of the song or a reference,
                        # I will go ahead and replace it completely.
                        self.server_changes_count += 1
            
            client_database.foreachInDatabase(item_func, 0)
            
            # save database
            self.srv_database.save(SRV_DATABASE_PATH)
            
            # summary
            print "\nServer changed count: {}".format(self.server_changes_count)
            print "Client will have to change count: {}".format(self.client_changes_count)
            print "Newly added to server db: {}".format(self.server_added_songs_count)
            print "Remain untouched: {}".format(self.unchanged_count)
                
            # reply
            pickled_client_changes = json.dumps(base64.b64encode(cPickle.dumps(self.client_changes)))
            response = Net_message(Net_message.MESSAGE_LOCAL_CHANGES, pickled_client_changes)
            response.send(connection)
            
            # save database
            self.srv_database.save(SRV_DATABASE_PATH)
        else:
            if self.args.verbose: print "Client asks for something unrecognized: {0}. answering error.".format(message.data)
            error = Net_message(type=Net_message.MESSAGE_ERROR, data="Unrecognized request!")
            error.send(connection)
            
    def start(self):
        """the actual implementation of the server. the process of syncing comes here"""
        print "Starting server...\n"
        
        self.srv_database = SongDatabase()
        if static.verbose: print "Loading database..."
        if not self.srv_database.load(SRV_DATABASE_PATH):
            print "No local database found, creating new."
        
        if self.args.verbose: print "Binding socket..."    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        HOST = "" # Symbolic, meaning all available interfaces
        s.bind((HOST, default_tcp_port))
        s.listen(1)
        
        while True: # keep running after connection is closed
            if self.args.verbose: print "Now listening...\n"
            try:
                conn = None
                conn, addr = s.accept()
                print "Connected to {0}:{1}".format(*addr)
                if self.args.verbose: print "Receiving data..."
                
                while True:
                    request = Net_message()
                    try:
                        request.receive(conn)
                    except Exception as e:
                        if e.message == "Connection Lost.":
                            print "Lost connection to {0}:{1}.".format(*addr)
                        else: raise
                        
                    if request.type == Net_message.MESSAGE_END:
                        break
                    self._handle_request(conn, request)
                    
                print "Closing connection to {0}:{1}.\n".format(*addr)                   

            except KeyboardInterrupt:
                print "\b\bInterrupted by user. Exiting."
                raise
                        
            finally:
                # interrupted or not, make sure the connection is closed.
                if not conn == None: conn.close()
        
    class _srv_daemon(Daemon):
        def __init__(self, pidfile, server, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):   
            self.server = server
            Daemon.__init__(self, pidfile, stdin, stdout, stderr)
            
        server = None
        
        def run(self):
            self.server.start()
        
    def run(self):
        """either starts a daemon or starts the server in the current window"""
        
        daemon = self._srv_daemon(srv_daemon_pid_path, self)
       
        if self.args.which == "run":
            self.start()
        elif self.args.which == "daemon":
            print "RatingSync will now be run in background."
            daemon.start()
        elif self.args.which == "stop":
            print "If a daemon is running in background, it will now be stopped."
            daemon.stop()
        elif self.args.which == "restart":
            print "If a daemon is running in background, it will be restarted now."
            daemon.restart()
        else:
            sys.exit(2)

if __name__ == "__main__":
    srv = Server()
    try:
        srv.run()
    except KeyboardInterrupt:
        pass
    