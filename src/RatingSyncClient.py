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
import os, argparse
import time as timemodule
import socket
import Ratings
import cPickle
import base64
import importlib
from shared import *
from SongDatabase import *
from daemon import Daemon

class client_prefs(prefs):
    def __init__(self):
        prefs.__init__(self, client_config_path)
        if self.prefs == None:
            self.prefs = {"server": None, "time": None, "path": None, "ratingPlugin": None} # Default preferences
        if not "server" in self.prefs:
            self.prefs["server"] = None
        if not "time" in self.prefs:
            self.prefs["time"] = None
        if not "path" in self.prefs:
            self.prefs["path"] = None
        if not "ratingPlugin" in self.prefs:
            self.prefs["ratingPlugin"] = None
    
    def setup(self):
        while not self.check_server(self.prefs["server"]):
            self.prefs["server"] = raw_input("Enter server ip [{}]: ".format(default_server))
            if self.prefs["server"] == "":
                self.prefs["server"] = default_server
                
        while self.prefs["path"] == None:
            self.prefs["path"] = raw_input("Enter path of music library [.]: ")
            if self.prefs["path"] == "":
                self.prefs["path"] = os.path.realpath(os.curdir)
        
        while not self.check_time(self.prefs["time"]):
            self.prefs["time"] = raw_input("Enter sync interval in minutes (min. 1)[{}]: ".format(default_time))
            if self.prefs["time"] == "": # default value
                self.prefs["time"] = default_time
            else:
                self.prefs["time"] = eval(self.prefs["time"])
                
        while not self.check_rating_plugin(self.prefs["ratingPlugin"]):
            self.prefs["ratingPlugin"] = raw_input("Enter rating plugin to be used [{}]: ".format(default_rating_plugin))
            if self.prefs["ratingPlugin"] == "":
                self.prefs["ratingPlugin"] = default_rating_plugin

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
    conf_parser.add_argument("--setup", action="store_true", help="Get asked for and set all parameters.")
    conf_parser.add_argument("--path", help="The path to the directory of your music collection.", type=str)
    conf_parser.add_argument("--server", help="The server to connect to.")
    conf_parser.add_argument("--time", help="The time interval in seconds for syncing the database.", type=int)
    conf_parser.add_argument("--plugin", help="The plugin for reading/saving ratings to use.", type=str)
    conf_parser.add_argument("--setup-plugin", action="store_true", help="Get asked for and set parameters for the rating plugin used.")
    conf_parser.add_argument("--list", action="store_true", help="List the current configuration.")
    #arg_parser.add_argument("--ratings-format", help="the format for ratings to be saved in files.", type=str)
    #arg_parser.add_argument("--create-playlists", help="automatically create or update playlists for every star rating")
    
    # run
    run_parser = subparser.add_parser("run", help="Start syncing client.")
    run_parser.set_defaults(which="run")
    
    # sync now
    sync_parser = subparser.add_parser("sync", help="Sync database now and exit.")
    sync_parser.set_defaults(which="sync")
    sync_parser.add_argument("--override-srv", action="store_true", help="Override all server ratings with local ratings.")
    sync_parser.add_argument("--override-local", action="store_true", help="Override all local ratings with server ratings.")
    
    # run in background
    daemon_parser = subparser.add_parser("daemon", help="Run in background.")
    daemon_parser.set_defaults(which="daemon")
   
    # stop the process in background
    stop_parser = subparser.add_parser("stop", help="Stop the process running in background.")
    stop_parser.set_defaults(which="stop")
    
    # restart the process in background
    res_parser = subparser.add_parser("restart", help="Restart the process running in background.")
    res_parser.set_defaults(which="restart")
    
    # parse args
    return parser.parse_args()

def init(args):
    config = client_prefs()
    
    static.verbose = args.verbose
    
    if args.which == "config":
        if args.setup:
            config.clear() # if we are going to re-set everything, clear it first.
            
        # do not proceed with setting up immediately though, there might be some arguments provided.
        if not args.path == None:
            if config.check_path(os.path.abspath(args.path)):
                config.prefs["path"] = os.path.abspath(args.path)
            
        if not args.server == None:
            if config.check_server(args.server):
                config.prefs["server"] = args.server
            
        if not args.time == None:
            if config.check_time(args.time):
                config.prefs["time"] = args.time
                
        if not args.plugin == None:
            if config.check_rating_plugin(args.plugin):
                config.prefs["ratingPlugin"] = args.plugin

        if args.setup:
            config.setup()
        
        
        if args.list:
            for l in config.list(): print l
            
        config.save()
        
    # rating plugin
    # initialize it after the prefs - might have been changed.
    global ratingPlugin
    try:
        ratingPlugin = importlib.import_module("rating_plugins." + config.prefs["ratingPlugin"])
    except:
        print "Failed to load rating plugin '{}'! Exiting.".format(config.prefs["ratingPlugin"])
        raise
    if args.which == "config" and args.setup_plugin:
        # FIXME
        ratingPlugin.setup()
        
    elif args.which in ["run", "sync", "daemon"]:
        config.setup() # make sure everything is set
    
    elif args.which in ["stop", "restart"]:
        pass
       
    else:
        sys.exit(1)
    
    return config

# TODO running in background

def start(args, config):
    """Start syncing"""
    programpath = os.path.abspath(os.curdir)
    databasepath = programpath + os.path.sep + CLIENT_DATABASE_PATH
    # check path
    musicpath = config.prefs["path"]
    if not os.path.exists(musicpath):
        print "Invalid path: {0}".format(musicpath)
        config.prefs["path"] = None
        config.setup()
    if args.which == "sync":
        if args.override_srv and args.override_local:
            print "You cannot override both local and server ratings."
            return
    
    database = SongDatabase()
    if args.verbose: print "Loading database..."
    if not database.load(databasepath):
        print "No local database found, creating new."
    
    firstrun = True
    while True:
        if not firstrun:
            if args.which == "sync":
                break
        
            if args.verbose:
                print "Next synchronization in {0} minutes. Press ctrl+c to exit.".format(config.prefs["time"])
            timemodule.sleep(config.prefs['time']*60)
        firstrun = False
        
        print "Checking availabilty of {0}...".format(config.prefs["server"])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # connect
        try:
            if args.verbose: print "Connecting..."
            s.connect((config.prefs["server"], default_tcp_port))
                
            if args.verbose: print "Sending ping..."
            ping = Net_message(Net_message.MESSAGE_PING)
            ping.send(s)
        
            if args.verbose: print "Waiting for an answer..."
            pong = Net_message()
            pong.receive(s)
            
            if pong.type == Net_message.MESSAGE_PONG:
                if args.verbose: print "Server available."
            else:
                raise Exception("Server not ready!")
        except:
            print "Server unavailable!"
            continue
        
        # update db
        try:            
            print "Updating database..."
            global ratingPlugin
            summary = database.update(musicpath, ratingPlugin)
            database.save(databasepath)
        except:
            print "IO error!"
            raise
            continue
            
        # set override type
        if static.verbose: 
            synctype = "equal"
            if args.override_srv: synctype = "overriding server ratings"
            if args.override_local: synctype = "overriding local ratings"
            print "Setting sync type to {0}.".format(synctype)
        synctype = "ovrequal"
        if args.override_srv: synctype = "ovrsrv"
        if args.override_local: synctype = "ovrlocal"
        synctype = Net_message(Net_message.MESSAGE_SYNC_TYPE, synctype)
        try:
            synctype.send(s)
        except:
            print "Network error!"
            continue
        
        # upload local db and let the server compare it
        print "Sending database to server..."
        databasefile = open(databasepath)
        try:
            datamsg = Net_message(Net_message.MESSAGE_DATABASE, databasefile.read())
            datamsg.send(s)
        except:
            print "Network error!"
            continue
        finally:
            databasefile.close()
        
        # await response
        response = Net_message()
        try:
            if static.verbose: print "Waiting for an answer..."
            response.receive(s)
            if response.type != Net_message.MESSAGE_LOCAL_CHANGES:
                raise Exception()
        except:
            print "Response error!"
            continue
        
        if args.verbose: print "Closing connection/socket..."
        s.close()
        
        # commit local changes
        if static.verbose: print "Updating local files..."
        local_changes_count = 0
        changes = cPickle.loads(base64.b64decode(json.loads(response.data)))
        for key, rating in changes.iteritems():
            dbsong = database.getSong(key, None)
            if dbsong:
                print "Changing rating for: {}".format(key)
                dbsong.saveRating(ratingPlugin, rating)
                local_changes_count += 1
            else:
                if static.verbose: print "Song doesn't exist locally, ignoring change request: {}".format(key)
        database.save(databasepath)
        
        # summary
        summary = summary + "\nRatings changed locally: {}".format(local_changes_count)
        print "\n" + summary + "\n"
        
        print "Syncronized. You might have to update your winamp media library. Working on this..."
        
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
        print "\b\bExiting..."