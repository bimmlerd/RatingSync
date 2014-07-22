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
from shared import *

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
    db = ET.parse(config.prefs["rdbPath"])    
    root = db.getroot()
    global songs
    songs = root.findall("./entry[@type='song']")

def loadRating(**kwargs):
    # TODO optimize this!!! Use a tree or something
    location = kwargs["path"].replace(" ", "%20")
    global songs
    done = False
    for song in songs:
        cont = False
        for a in song:
            if a.tag == "location":
                if a.text.endswith(location):
                    done = True # done means something more like "found the song"
                else:
                    cont = True
                break
        if cont: continue
        if done: # thats the song.
            for a in song:
                if a.tag == "rating":
                    return int(a.text)
            # song didnt have a rating.
            return 0
    # song is not in db..

def saveRating(rating, **kwargs):
    path = kwargs["path"]
    # TODO implement
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
        os.utime(path, None)
    else:
        os.utime(path, (time, time))

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
