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
from shared import *
from daemon import Daemon

class srv_prefs:
    def __init__(self):
        prefs.__init__(self, srv_config_path)
        if self.prefs == None:
            self.prefs = {"pref0": None} # Default preferences
    
    def setup(self):
        pass

class srv_daemon(Daemon):
    def __init__(self, pidfile, server, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):   
        self.server = server
        Daemon.__init__(self, pidfile, stdin, stdout, stderr)
        
    server = None
    
    def run(self):
        self.server.start()
    
class Server:
    """This time, I will structure my code better (or so I hope)"""
    
    def __init__(self):
        self.parse_args()
    
    def parse_args(self):
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
    
    def start(self):
        """the process of syncing comes here"""
        print "Starting server..."
        if self.args.verbose:
            print "Not yet implemented" # TODO
    
    def run(self):
        """either starts a daemon or starts the server in the current window"""
        
        daemon = srv_daemon(srv_daemon_pid_path, self)
       
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
    srv.run()