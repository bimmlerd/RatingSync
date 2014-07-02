from mutagen.id3 import ID3
import os
import Ratings

class Song:
    def __init__(self, path, openInstantly):
        self.__lastModified = os.path.getmtime(path)
        self.__path = path
        if openInstantly:
            id3 = ID3(path)
            self.__ratings = id3.getall('POPM')
            artist = id3.getall("TPE1")
            title = id3.getall("TIT2")
            if not artist or not title:
                self.__key = self.__path
            else:
                self.__key = "{a} - {t}".format(a=artist[0], t=title[0]) # (distant) TODO: maybe consider the other entries in the artist/title tags aswell?
    
    def path(self):
        return self.__path
    
    def filename(self):
        return os.path.basename(self.path())
    
    def getRatings(self):
        return self.__ratings
    
    def getRatingStars(self, provider):
        """Get song ratings in stars from 1-5. Provider is the rating provider, meaning which player has been used to rate the song."""
        if not self.getRatings():
            return 0 # means unrated
        for rating in self.getRatings():
            try:
                return Ratings.starsFromByte(rating, Ratings.RatingProvider.WinAmp) # TODO support other ratings than those from winamp.
            except:
                pass
        raise Exception("Getting ratings for song failed: {}".format(self.key()))
    
    def setRatings(self, ratings):
        if not self.__ratings == ratings:
            self.__id3.setall('POPM', ratings)
            self.__id3.save(self.__path)
    
    def setRatingStars(self, stars, provider):
        """
        Set song ratings in stars from 1-5. Provider is the rating provider (see getRatingStars).
        NOTE: this will ERASE all current ratings! Meaning you cannot have different ratings from different providers at the same time (...yet)!
        """
        ratings = [Ratings.byteFromStars(stars, provider)]
        if os.path.exists(self.path()):
            Ratings.setRatingsForItem(ratings, self.path())
        else:
            # TODO
            print "Song doesnt exist but is in db, maybe delete?: {}".format(self.key())
        
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
        return self.__key
        
    # TODO
    # def getArtist
    # def getSongname