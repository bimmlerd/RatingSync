from bintrees import FastAVLTree
import jsonpickle
import time


class SongDatabase():
    '''
    #was reinschreiben##
    '''
    global __tree
    global __created
    global __finished
    
    def __init__(self, params):
        __tree = FastAVLTree()
        __finished = False
       
    def created(self):
        return __created
    
    def finish(self):
        __finished = True
        __created = time.time 
     
    def insertSong(self, song):
        if __finished:
            raise Exception("already finished")
        __tree.setdefault(song.LastChange, song)
       
       
    def serialize(self, path):
        if not __finished:
            raise Exception("not yet finished")
        file = open(path, 'w')
        json_obj = jsonpickle.encode(self)
        file.write(json_obj)
        file.closed
        return path
        
    def deserialize(self, path):
        file = open(path, 'r')
        db = jsonpickle.decode(file.read())
        return db
    
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
        if not __finished:
            raise Exception("not yet finished")
        if not __tree.is_empty():
            return __tree.pop_max()
            return None