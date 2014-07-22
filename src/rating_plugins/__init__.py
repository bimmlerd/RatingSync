"""
RATING PLUGINS API

Rating plugins shall be used to read and save ratings of different types, eg.
file tags, or to support various music players which do not save their ratings
in files.
Which rating plugin to use can be set up in the client application.

Here is the interface:



(on startup):
plugin should load its preferences and be initialized

loadRating(**kwargs):
return rating of this song

saveRating(rating, **kwargs):
save rating of this song, save last modified time (now), and return last modified time

getLastChanged(**kwargs):
return last modified (saved) time of the song

setup():
ask user for preferences and save them



The kwargs will contain the file path, song key, and probably artist, title, ... (not sure yet) to find the file or the song in databases.

Any other declarations should be private!

I will probably extend this soon..
"""