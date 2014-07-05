## RatingSync

### Synchronizes the ratings of your music collection across multiple platforms.

The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes ratings with the server.
For now, this only supports winamp ratings saved in mp3 file tags, more coming soon.

### Installation & Running
#### Linux (and probably OSX):

Run the following commands:

* sudo pip install mutagen bintrees
* git clone https://github.com/Posedge/RatingSync.git
* cd RatingSync
* ./RatingSyncServer.py *args* -or- ./RatingSyncClient.py *args*

#### Windows:

* Download and install Python 2.7. [Link here](https://www.python.org/downloads/)
* Download and install [mutagen](https://pypi.python.org/pypi/mutagen) and [bintrees](https://pypi.python.org/pypi/bintrees/2.0.1)
* Make sure you are on branch "master"
* Download the zip file (the "Download ZIP" button is to the right) 
* Extract the zip file somewhere
* To run, hold shift and rightclick the explorer window and click "Open Command Window here"
* Type "python.exe RatingSyncServer.py *args*" -or- "python.exe RatingSyncClient.py *args*" and press enter (you might have to specify the full path to your python.exe)

### Dependencies (Python packages)
* mutagen
* bintrees

### TODO list
* Fix connecting at random ports bug
* Add a timeout to the socket?
* Add support for differently saved Ratings, other than WinAmp ratings in files, as well as an option to the config
* Add support for the Rhythmbox database
* Add option to override all local/server ratings
* Add option to monitor changes in a folder instead of syncing periodically
* Add option to instantly rate a song (everywhere) with a single command
* (some little #TODO or #FIXME tasks in the code)

### Ideas for additional features (distant TODO list)
* Add daemon/background process support for windows
* As an alternative to a server, allow synchronizing by using a common file shared across the network
* Add option to automatically generate/update playlists by rating and other attributes, according to user-defined rules. These should include ratings, genre, play count, folder, ...?
* Add option to automatically delete one-star-rated files from your music libraries
* Add messages and options to configure server remotely
* Add possibility for a single server to manage multiple databases

### Changelog
#### (next release)

* Fixed: Files containing ".mp3" instead of ending in ".mp3" bug
* Added: Ability to connect to hostnames

#### v0.1

* Initial Release
