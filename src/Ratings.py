from enum import Enum
from mutagen.id3 import ID3

def getRatingsFromItem(item):
    return ID3(item).getall('POPM')

def setRatingsForItem(ratings, item):
    ID3(item).setall('POPM', ratings)
    
def starsFromByte(rating, provider):
    if provider == RatingProvider.WinAmp or provider == RatingProvider.WindowsMediaPlayer9:
        if rating == 255:   return 5
        elif rating == 196: return 4
        elif rating == 128: return 3
        elif rating == 64:  return 2
        elif rating == 1:   return 1
        else:
            raise Exception("Unknown rating for " + RatingProvider.reverse_mapping(provider))
    else:
        raise Exception("Unknown RatingProvider.")

def byteFromStars(stars, provider):
    if provider == RatingProvider.WinAmp or provider == RatingProvider.WindowsMediaPlayer9:
        if stars > 5 or stars < 1:
            raise Exception("Rating not between 0 and 5.")
        return {0, 1, 64, 128, 196, 255}[stars]
    else:
        raise Exception("Unknown RatingProvider.")
    
class RatingProvider(Enum):
    WinAmp = 'rating@winamp.com'
    WindowsMediaPlayer9 = 'Windows Media Player 9 Series'