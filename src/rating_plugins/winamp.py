# Plugin for WinAmp ratings saved in files, reads winamp frames in id3 tags.

import os.path
from mutagen.id3 import ID3, POPM

# init
print "WinAmp plugin for ratings in id3 frames in mp3 files loaded."

def loadRating(**kwargs):
    path = kwargs["path"]
    id3 = ID3(path)
    popmframes = id3.getall('POPM')
    return __getRatingStars(popmframes)

def saveRating(rating, **kwargs):
    path = kwargs["path"]
    ratings = [__frameFromRating(rating)]
    if os.path.exists(path):
        id3 = ID3(path)
        id3.setall('POPM', ratings)
        id3.save(path)
        return os.path.getmtime(path)    
    else:
        raise Exception("Song doesnt exist but is in db?: {}".format(key))

def getLastChanged(**kwargs):
    return os.path.getmtime(kwargs["path"])

def touch(time, **kwargs):
    pass

def setup():
    print "No preferences for this plugin."

def __getRatingStars(popmframes):
    """Get song ratings in stars from 1-5, or 0 if not rated."""
    if not popmframes:
        return 0 # means unrated
    for rating in popmframes:
        try:
            return __ratingFromByte(rating)
        except:
            pass
    raise Exception("Getting ratings for song failed: {}".format(self.key()))

def __ratingFromByte(rating):
    if rating == 255:   return 5
    elif rating == 196: return 4
    elif rating == 128: return 3
    elif rating == 64:  return 2
    elif rating == 1:   return 1
    
def __frameFromRating(rating):
    if rating > 5 or rating < 0:
        raise Exception("Rating not between 0 and 5.")
    byte = [0, 1, 64, 128, 196, 255][rating]
    return POPM(email="rating@winamp.com", rating=byte)