'''
Created on 07.06.2014

@author: phisch
'''
from mutagen.id3 import ID3
import os

class Song:
    global __id3
    global __ratings
    global __lastModified
    global __path
    
    def __init__(self, path, openInstantly):
        __lastModified = os.path.getmtime(path)
        __path = path
        if openInstantly:
            __id3 = ID3(path)
            __ratings = __id3.getall('POPM')
    
    def path(self):
        return __path
    
    def GetRatings(self):
        return __ratings
    
    def SetRatings(self, ratings):
        if not __ratings == ratings:
            __id3.setall('POPM', ratings)
            __id3.save(__path)
    
    def LastChange(self):
        return __lastModified
    
    def OpenAfterwards(self):
        __id3 = ID3(__path)
        __ratings = __id3.getall('POPM')