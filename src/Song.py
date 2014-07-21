from mutagen.id3 import ID3
import os
import Ratings
import time

class Song:
    def __init__(self, path, ratingPlugin):
        self.__path = path
        id3 = ID3(path)
        artist = id3.getall("TPE1")
        title = id3.getall("TIT2")
        album = id3.getall("TALB")
        if not artist or not title:
            # TODO support id3v1 ?
            # TODO if there is no data, pick relative path, to make sure the key stays the same on multiple libraries!
            self.__key = self.__path
        elif not album:
            self.__key = "{a} - {t}".format(a=artist[0], t=title[0]) # (distant) TODO: maybe consider the other entries in the artist/title tags aswell?
        else:
            self.__key = "{ar} - {al} - {t}".format(ar=artist[0], al=album[0], t=title[0])
        self.loadRating(ratingPlugin)
        self.__lastModified = ratingPlugin.getLastChanged(self.path(), self.key())
            
    def path(self):
        return self.__path
    
    def filename(self):
        return os.path.basename(self.path())
    
    def rating(self):
        return self.__rating
    
    def saveRating(self, ratingPlugin, rating):
        """Save rating according to ratingPlugin either to file, or to some database or whatever. Then update last changed attribute."""
        self.__rating = rating
        self.__lastModified = ratingPlugin.saveRating(self.path(), self.key(), rating)
    
    def loadRating(self, ratingPlugin):
        """Load rating using ratingPlugin"""
        self.__rating = ratingPlugin.loadRating(self.path(), self.key())
        
    def lastChanged(self):
        return self.__lastModified
    
    def touch(self):
        """Set last modified time of object to now. Doesn't change file!"""
        self.__lastModified = time.time()
        
    def key(self):
        """
        Return song key.
        """
        return self.__key
        
    # TODO
    # def getArtist
    # def getSongname