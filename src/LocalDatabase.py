import os
import sys
import re
from Song import Song
import time as timemodule
from SongDatabase import SongDatabase


def collect(config, verbose):
    newLocalDatabase = SongDatabase(None)
    
    # implementation    
    starttime = timemodule.time() # performance measuring

    os.chdir(config.prefs["path"])
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
            new_dirs = [os.path.realpath(item + os.sep + c) for c in os.listdir(item)]
            dfs_stack.extend(new_dirs)
        elif os.path.isfile(item):
            if re.search(r".*\.mp3", item):
                song = Song(item, False)
                newLocalDatabase.insertSong(song)
                if verbose:
                    print("adding to music list ({}*): {}".format(song.lastChanged(), song.path()))
            elif verbose:
                print("not an mp3 file: {}".format(item))
        else:
            print("error, {} is neither a file nor a directory. exiting.".format(item))
            sys.exit(2)

    elapsed = timemodule.time() - starttime

    if verbose:
        print "elapsed time: {:.5f}s".format(elapsed)
        print "music files len: ?"
        print "visited len", len(visited)

    newLocalDatabase.finish()
    newLocalDatabase.serialize(os.curdir + os.path.sep + "MusicDatabase")

def upload():
    #Uplaod the File "MusicDatabase"
    pass # TODO
