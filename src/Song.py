from mutagen.id3 import ID3
import os

class Song:
    __id3 = None
    __ratings = None
    __lastModified = None
    __path = None
    
    def __init__(self, path, openInstantly):
        self.__lastModified = os.path.getmtime(path)
        self.__path = path # str to convert unicode.
        # note that we lose many characters, so the __path will NOT return the acutal path!!! It will work great as a key though.
        if openInstantly:
            self.__id3 = ID3(path)
            self.__ratings = self.__id3.getall('POPM')
    
    def path(self):
        return self.__path
    
    def filename(self):
        return os.path.basename(self.path())
    
    def getRatings(self):
        return self.__ratings
    
    def setRatings(self, ratings):
        if not self.__ratings == ratings:
            self.__id3.setall('POPM', ratings)
            self.__id3.save(self.__path)
    
    def lastChanged(self):
        return self.__lastModified
    
    def openAfterwards(self):
        self.__id3 = ID3(self.__path)
        self.__ratings = self.__id3.getall('POPM')
        
    def key(self):
        """
        Determines what shall be used as a key.
        The last-changed date is a BAD idea since this has to be unique.
        """
        return self.path() # I guess at some point I had to run into this problem...
        
    # TODO
    # def getArtist
    # def getSongname