#!/usr/bin/env python

"""
Server Code
Tasks:
The server has a local database of songs, their ratings and last-change-date.
On request, compares the received list with the local database. Changes are synchronized in both direcitons:
If the received change is newer, update the local database.
Otherwise, send back a list of changes to be made in the clients music library.
"""

import os, sys, argparse
import json
from shared import *
from daemon import Daemon



class Server:
    """This time, I will structure my code better (or so I hope)"""
    
    def __init__(self, **kwargs):
        if kwargs["daemon"]:
            self.__daemon = True
    
    __daemon = False
    
    def parse_args(self):
        pass
    
    def run(self):
        pass

if __name__ == "__main__":
    srv = Server()
    srv.run()