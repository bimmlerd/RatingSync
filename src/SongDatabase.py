import os, re, jsonpickle, time
from bintrees import FastAVLTree
from Song import Song

class SongDatabase():
    '''
    Music library database
    '''
    __tree = None
    __created = None
    __finished = None
    
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
        self.__tree.setdefault(song.lastChanged, song)
       
       
    def save(self, path):
        if not self.__finished:
            raise Exception("not yet finished")
        serializing_file = open(path, 'w')
        json_obj = jsonpickle.encode(self.__tree)
        serializing_file.write(json_obj)
        serializing_file.close()
        
    def load(self, path):
        """Try to load the database from a file. Return if it worked/if database is now initalized."""
        try:
            serializing_file = open(path, 'r')
            tree = jsonpickle.decode(serializing_file.read())
            serializing_file.close()
            self.__tree = tree
        except:
            return False
        return True
    
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
    
    def build(self, path, verbose):
        """
        Search music directory and add songs to the database
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
                    if verbose: print("adding to music list ({}*): {}".format(song.lastChanged(), song.path()))
                    self.insertSong(song)
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
        Search music directory and update database
        """
        pass
