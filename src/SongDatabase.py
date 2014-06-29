import os, re, time
import cPickle
import base64
import json
from bintrees import FastAVLTree
from Song import Song
from shared import static

class SongDatabase():
    '''
    Music library database
    '''
    __tree = None
    #__lastSynchronized = None
    # Optimize the algorithm by only sending the songs changed since this time to the server
    # (this needs to be implemented first obviously)
    
    def __init__(self):
        self.__tree = FastAVLTree()
    
    def insertSong(self, song):
        if not self.__tree.get(song.key()):
            self.__tree.setdefault(song.key(), song)
        else: raise Exception("Tree already contains {}".format(song.key()))
       
    def removeSong(self, song):
        self.__tree.remove(song.key())
        
    def getSong(self, key, default=None):
        return self.__tree.get(key, default)
        
    def updateSong(self, song):
        """
        Update song in the tree.
        Return if it had to be changed.
        """
        tree_song = self.__tree.get(song.key())
        if not tree_song:
            print "Adding new to database: {}".format(song.filename())
            self.insertSong(song)
        else:
            # song is the song provided
            # tree_song is the song as it is saved in the database
            # Synchronize these:
            if song.lastChanged() > tree_song.lastChanged():
                print "Updating modified song: {}".format(song.filename())
                self.removeSong(tree_song) # note that it doesn't matter if we use song or tree_song here - the key is the same.
                self.insertSong(song)
                return True
            return False
                           
    def save(self, path):
        if static.verbose: print "Saving database..."
        serializing_file = open(path, 'w')
        if self.__tree._count == 0:
            if static.verbose: print "Database is empty, therefore it will not be serialized."
            serializing_file.close() # file is now empty
            return
        json_obj = json.dumps(base64.b64encode(cPickle.dumps(self.__tree)))
        serializing_file.write(json_obj)
        serializing_file.close()
        
    def load(self, path):
        """Try to load the database from a file. Return if it worked/if database is now initialized."""
        try:
            serializing_file = open(path, 'r')
            #tree = jsonpickle.decode(serializing_file.read())
            tree = cPickle.loads(base64.b64decode(json.loads(serializing_file.read())))
            serializing_file.close()
            if tree == None: # Loaded database was empty
                return False
            else:
                self.__tree = tree
        except:
            return False
        return True
    
    def loadFromString(self, str):
        """Try to load the database from a string. Return if it worked/if database is now initialized."""
        try:
            tree = cPickle.loads(base64.b64decode(json.loads(str)))
            if tree == None:
                return False
            else:
                self.__tree = tree
        except:
            return False
        return True
    
    def foreachInDatabase(self, func, order=0):
        """For each item in the tree apply the function. Order: 0: Inorder, -1: Preorder, +1: Postorder."""
        if self.__tree._count == 0: # for some reason the count() function doesnt work.
            return
        self.__tree.foreach(func, order)
        
    def pop(self):
        if not self.__tree.is_empty():
            return self.__tree.pop_max()
            return None
    
    def _foreachOnDrive(self, path, verbose, song_action):
        """
        Search music directory and perform action on each song.
        """
        # implementation    
        starttime = time.time() # performance measuring
    
        os.chdir(path)
        dfs_stack = [os.path.realpath(os.curdir)]
        visited = []
        while dfs_stack: # while not empty
            item = dfs_stack.pop()
        
            if item in visited: # make sure there are no cycles
                if verbose: print "searched file already: {}".format(item)
                continue
            
            visited.append(item)
            if os.path.isdir(item):
                if verbose: print "adding dir to searching list: {}".format(item) 
                    # push all child files to the stack
                new_dirs = [os.path.realpath(item + os.sep + c) for c in os.listdir(item)]
                dfs_stack.extend(new_dirs)
            elif os.path.isfile(item):
                if re.search(r".*\.mp3", item):
                    song = Song(item, True)
                    song_action(song)
                elif verbose: print "not an mp3 file: {}".format(item)
            else:
                print "error, {} is neither a file nor a directory. exiting.".format(item) 
                sys.exit(2)
    
        elapsed = time.time() - starttime
    
        if verbose:
            print "elapsed time: {:.5f}s".format(elapsed)
            print "music files len: ?"
            print "visited len", len(visited)
    
    def update(self, path, verbose):
        """
        Update music database.
        """
        self._foreachOnDrive(path, verbose, self.updateSong)
                    
