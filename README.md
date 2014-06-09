## RatingSync

## Synchronizes the ratings of your music collection across multiple platforms.

### Authors
posedge, phishdev, dbimmler

### more info
The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes updated ratings with the server.

This is my first python project so the code might be bad :)

### Dependencies (Python packages)
* mutagen
* jsonpickle
* bintrees

### TODO
* save database if there is none, otherwise only update changes

* figure out the best way for saving ratings in ID3 tags (the POPM frame is kinda complicated) - fake winamp/windows media player/Rhythmbox/...... ratings?
* add option to config for that

* write server code
* connect to server, update database

* run program in background/as a daemon and sync database every now and then
* maybe monitor changes in a folder?

* add option to automatically generate/update playlists by rating and other attributes, according to user-defined rules

* (many little #TODO tasks in the code)

### Changelog
[...]
