## RatingSync

### Synchronizes the ratings of your music collection across multiple platforms.

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

### To Do list
* Fix serializing the database
* Figure out the best way for saving ratings in ID3 tags (the POPM frame is kinda complicated) - fake winamp/windows media player/Rhythmbox/...... ratings?
* Add option to config for that
* fix connecting at random ports bug
* write database code for server
* Add daemon/background process support for windows
* (many little #TODO tasks in the code)

### Ideas for additional features
* As an alternative to a server, allow synchronizing by using a common file shared across the network
* Add option to monitor changes in a folder
* Add option to automatically generate/update playlists by rating and other attributes, according to user-defined rules. These should include ratings, genre, play count, folder, ...?

### Changelog
* [...]
