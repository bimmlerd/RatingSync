from mutagen.id3 import ID3
import os
import Ratings
import time

class Song:
    def __init__(self, path, ratingPlugin):
        self.__path = path
        id3 = ID3(path)
        self.__attrs = {"artist": id3.get("TPE1"), "title": id3.get("TIT2"), "album": id3.get("TALB")}
        self.__key = Song.makeKey(path=self.path(), **self.getAttributes())
        self.loadRating(ratingPlugin)
        self.__lastModified = ratingPlugin.getLastChanged(path=self.path(), key=self.key(), **self.getAttributes())
            
    def path(self):
        return self.__path
    
    def filename(self):
        return os.path.basename(self.path())
    
    def rating(self):
        return self.__rating
    
    def saveRating(self, ratingPlugin, rating):
        """Save rating according to ratingPlugin either to file, or to some database or whatever. Then update last changed attribute."""
        self.__rating = rating
        self.__lastModified = ratingPlugin.saveRating(rating, path=self.path(), key=self.key(), **self.getAttributes())
    
    def loadRating(self, ratingPlugin):
        """Load rating using ratingPlugin"""
        self.__rating = ratingPlugin.loadRating(path=self.path(), key=self.key())
        assert self.rating() != None
        
    def lastChanged(self):
        return self.__lastModified
    
    def touch(self, ratingPlugin=None):
        """Set last modified time of object to now. Doesn't change file!"""
        t = time.time()
        self.__lastModified = t
        if ratingPlugin:
            ratingPlugin.touch(t, path=self.path(), key=self.key(), **self.getAttributes())
            
    def getAttributes(self):
        """Return dict with name, artist, album of this song."""
        return self.__attrs
        
    def key(self):
        """
        Return song key.
        """
        return self.__key
    
    @staticmethod
    def makeKey(**attrs):
        """
        Make a song key using the attributes (title, artist, album).
        If there is insufficent information, make it with the path in which the song is located.
        This is non-preferrred because on different hard drives song might not be found.
        """
        artist = attrs["artist"]
        album = attrs["album"]
        title = attrs["title"]
        if not attrs["artist"] or not attrs["title"]:
            # TODO support id3v1 ?
            # TODO if there is no data, pick relative path, to make sure the key stays the same on multiple libraries!
            key = attrs["path"]
        elif not attrs["album"]:
            key = "{ar} - {t}".format(ar=attrs["artist"], t=attrs["title"]) # (distant) TODO: maybe consider the other entries in the artist/title tags aswell?
        else:
            key = "{ar} - {al} - {t}".format(ar=artist, al=album, t=title)
        if isinstance(key, unicode): key = key.encode("utf8")
        return key
        