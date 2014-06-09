from bintrees import FastAVLTree
import jsonpickle
import time


class SongDatabase():
    '''
    #was reinschreiben##
    '''
    __tree = None # globale variablen wuerde bedeuten dass du ausserhalb der klasse SongDatabase nach ihnen suchst. das ist nicht das was wir hier brauchen
    __created = None
    __finished = None
    
    def __init__(self, params):
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
        self.__tree.setdefault(song.LastChange, song)
       
       
    def serialize(self, path):
        if not self.__finished:
            raise Exception("not yet finished")
        serializing_file = open(path, 'w') # 'file' is reserved
        json_obj = jsonpickle.encode(self)
        serializing_file.write(json_obj)
        serializing_file.close()
        return path
        
    def deserialize(self, path):
        serializing_file = open(path, 'r')
        db = jsonpickle.decode(serializing_file.read())
        serializing_file.close()
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
        if not self.__finished:
            raise Exception("not yet finished")
        if not self.__tree.is_empty():
            return self.__tree.pop_max()
            return None
