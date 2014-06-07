'''
Created on 07.06.2014

@author: pschi_000
'''

from enum import Enum
from mutagen.id3 import ID3

def getRatingFromItem(item):
    return ID3(item).getall('POPM')

def StarsFromByte(rating, provider):
    if provider == RatingProvider.WinAmp or provider == RatingProvider.WindowsMediaPlayer9:
        if rating == 255:   return 5
        elif rating == 196: return 4
        elif rating == 128: return 3
        elif rating == 64:  return 2
        elif rating == 1:   return 1
        elif rating == 0:   return 0
        else:
            raise Exception("Unknown rating for " + RatingProvider.reverse_mapping(provider))
    else:
        raise Exception("unknown RatingProvider")

def ByteFromStars(stars, provider):
    if provider == RatingProvider.WinAmp or provider == RatingProvider.WindowsMediaPlayer9:
        if stars == 5:      return 255
        elif stars == 4:    return 196
        elif stars == 3:    return 128
        elif stars == 2:    return 64
        elif stars == 1:    return 1
        elif stars == 0:    return 0
        else:
            raise Exception("rating not between 0 and 5")
    else:
        raise Exception("unknown RatingProvider")
    
class RatingProvider(Enum):
    WinAmp = 'rating@winamp.com'
    WindowsMediaPlayer9 = 'Windows Media Player 9 Series'