from mutagen.id3 import ID3
import os

class Song:
    __id3 = None
    __ratings = None
    __lastModified = None
    __path = None
    
    def __init__(self, path, openInstantly):
        self.__lastModified = os.path.getmtime(path)
        self.__path = path
        if openInstantly:
            self.__id3 = ID3(path)
            self.__ratings = self.__id3.getall('POPM')
    
    def path(self):
        return self.__path
    
    def GetRatings(self):
        return self.__ratings
    
    def SetRatings(self, ratings):
        if not self.__ratings == ratings:
            self.__id3.setall('POPM', ratings)
            self.__id3.save(self.__path)
    
    def LastChange(self):
        return self.__lastModified
    
    def OpenAfterwards(self):
        self.__id3 = ID3(self.__path)
        self.__ratings = self.__id3.getall('POPM')