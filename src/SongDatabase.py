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
    __created = None
    __finished = None
    #__lastSynchronized = None
    # Optimize the algorithm by only sending the songs changed since this time to the server
    # (this needs to be implemented first obviously)
    
    def __init__(self):
        self.__tree = FastAVLTree()
        self.__finished = False
       
    def created(self):
        return self.__created
    
    def finish(self):
        self.__finished = True
        self.__created = time.time
     
    def insertSong(self, song):
        if self.__finished:
            raise Exception("already finished")
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
        if not self.__finished:
            raise Exception("not yet finished")
        serializing_file = open(path, 'w')
        #json_obj = jsonpickle.encode(self.__tree)
        json_obj = json.dumps(base64.b64encode(cPickle.dumps(self.__tree)))
        serializing_file.write(json_obj)
        serializing_file.close()
        
    def load(self, path):
        """Try to load the database from a file. Return if it worked/if database is now initialized."""
        try:
            serializing_file = open(path, 'r')
            #tree = jsonpickle.decode(serializing_file.read())
            self.__tree = cPickle.loads(base64.b64decode(json.loads(serializing_file.read())))
            serializing_file.close()
        except:
            return False
        return True
    
    def loadFromString(self, str):
        """Try to load the database from a string. Return if it worked/if database is now initialized."""
        try:
            self.__tree = cPickle.loads(base64.b64decode(json.loads(str)))
        except:
            return False
        return True
    
    def foreachInDatabase(self, func, order=0):
        """For each item in the tree apply the function. Order: 0: Inorder, -1: Preorder, +1: Postorder."""
        self.__tree.foreach(func, order)
        
    '''
    def popAsNewDatabase(self, limit):
        if not __finished:
            raise Exception("not yet finished")
        if not __tree.is_empty():
            item = __tree.pop_max()
            if item.LastModified >= limit: # oder nur > ?
                return item
        return None
    '''
        
    def pop(self):
        if not self.__finished:
            raise Exception("not yet finished")
        if not self.__tree.is_empty():
            return self.__tree.pop_max()
            return None
    
    def _for_each_mp3(self, path, verbose, song_action):
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
                    song = Song(item, False)
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
    
        self.finish()
    
    def update(self, path, verbose):
        """
        Update music database.
        """
        def update_song(s):
            self.updateSong(s)
        self._for_each_mp3(path, verbose, update_song)
                    
