"""
Plugin for the rhythmbox database

The db is normally located in ~/.local/share/rhythmbox/rhythmdb.xml
Ratings are stored in the xml file.
I will save the last modified time in the files. They get updated in the rhythmdb.xml automatically.
For good synchronization results, we want the last modified time to be as close as possible to the time,
when the rating has last been changed. This is not as easy since Rhythmbox doesn't save that anywhere -
therefore every time we notice a change in the rating, we have to update it manually.
"""

import os
import xml.etree.ElementTree as ET
from Song import Song
from shared import *
from bintrees import FastAVLTree
from argparse import ArgumentError

# constants
RDB_CONFIG_PATH = "rating_plugins" + os.sep + "rhythmdb.conf"
DEFAULT_RDB_PATH = "~/.local/share/rhythmbox/rhythmdb.xml"

def __init():
    print "Loading rhythmbox database plugin..."
    if static.verbose: print "Rhythmdb: Loading prefs file..."
    config = rhythm_prefs()
    # make sure everything is set
    config.setup()
    if static.verbose: print "Rhythmdb: Loading rhythmdb file..."
    songs = ET.parse(config.prefs["rdbPath"]).getroot().findall("./entry[@type='song']")
    if static.verbose: print "Rhythmdb: Building data structure..."
    global rhythmdb
    rhythmdb = FastAVLTree()
    for song in songs:
        # insert all songs and their ratings in the tree
        artist, album, title = song.find("artist"), song.find("album"), song.find("title")
        location, rating = song.find("location"), song.find("rating")
        if artist != None:
            artist = artist.text
            if isinstance(artist, unicode): artist = artist.encode("utf8")
        if album != None:
            album = album.text
            if isinstance(album, unicode): album = album.encode("utf8")
        if title != None:
            title = title.text
            if isinstance(title, unicode): title = title.encode("utf8")
        rating = 0 if rating == None else int(rating.text)
        location = location.text.replace("%20", " ").replace("file://", "", 1)
        key = Song.makeKey(artist=artist, title=title, album=album, path=location)
        if static.verbose: print "Rhythmdb: adding {}".format(key)
        rhythmdb.insert(key, rating)

def loadRating(**kwargs):
    global rhythmdb
    return rhythmdb.get(kwargs["key"])

def saveRating(rating, **kwargs):
    if rating < 0 or rating > 5:
        raise Exception("Invalid rating!")
    # update in tree
    location = kwargs["path"].replace(" ", "%20")
    global rhythmdb
    rhythmdb[location] = rating
    # update in db
    xmltree = ET.parse(config.prefs["rdbPath"])
    xmlsong = xmltree.getroot().find("./entry[location='{}']".format(location))
    xmlrating = xmlsong.find("rating")
    xmlrating.text = str(rating)
    xmltree.write(config.prefs["rdbPath"])
    # update last modified time
    touch(**kwargs)

def getLastChanged(**kwargs):
    return os.path.getmtime(kwargs["path"])

def setup():
    prefs.clear()
    prefs.setup()
    prefs.save()

def touch(time=None, **kwargs):
    if not time:
        os.utime(kwargs["path"], None)
    else:
        # FIXME
        os.utime(kwargs["path"], None)

class rhythm_prefs(prefs):
    def __init__(self):
        prefs.__init__(self, RDB_CONFIG_PATH)
        if self.prefs == None: # default prefs
            self.prefs = {"rdbPath": DEFAULT_RDB_PATH}
    
    def setup(self):
        while not self.check_file_exists(self.prefs["rdbPath"]):
            self.prefs["rdbPath"] = raw_input("Enter path to rhythmdb.xml [{}]:".format(DEFAULT_RDB_PATH))
            if self.prefs["rdbPath"] == "":
                self.prefs["rdbPath"] = DEFAULT_RDB_PATH
        self.save()
    
__init()
