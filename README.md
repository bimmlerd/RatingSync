## RatingSync

### Synchronizes the ratings of your music collection across multiple platforms.

The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes updated ratings with the server.

This is my first python project so the code might be bad :)

### Authors
posedge, phishdev, dbimmler

### Dependencies (Python packages)
* mutagen
* jsonpickle
* bintrees

### To Do list
* Fix setRatingsForItem bug
* Fix connecting at random ports bug
* Fix files contining ".mp3" instead of ending in ".mp3" matching the RE bug
* Change song key to artist - title instead of path
* Add a timeout to the socket?
* Figure out the best way for saving ratings in ID3 tags (the POPM frame is kinda complicated) - fake winamp/windows media player/Rhythmbox/...... ratings?
* Add option to config for that
* Add option to override all local/server ratings
* Add daemon/background process support for windows
* (many little #TODO/#FIXME tasks in the code)

### Ideas for additional features
* As an alternative to a server, allow synchronizing by using a common file shared across the network
* Add option to monitor changes in a folder
* Add option to automatically generate/update playlists by rating and other attributes, according to user-defined rules. These should include ratings, genre, play count, folder, ...?
* Add option to automatically delete one-star-rated files from your music libraries
* Add messages and options to configure server remotely
* Add possibility for a single server to manage multiple databases
* Add option to instantly rate a song (everywhere) with a single command

### Changelog
* [...]
