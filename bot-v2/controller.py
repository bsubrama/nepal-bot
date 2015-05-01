#!/usr/bin/env python
# encoding: utf-8
"""
controller.py

Created by Brado Subramanian on 2015-04-30.
Copyright (c) 2015 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from multiprocessing import Process
import logger
import util
import config
import stream_listener as sl
import retweeter as rt

# Start up 1 stream_listener, n_accounts retweeters and 1 log_listener
def main():
    stream_listener = Process(target=sl.main)
    stream_listener.start()
    
    retweeters = []
    for name, account in config.CONFIG['accounts'].iteritems():
        retweeter = Process(target=rt.run_as_process, args=(name, account['tweets_per_hour']))
        retweeter.start()
    
    log_listener = Process(target=logger.run_log_listener_as_process)
    log_listener.start()
    
    stream_listener.join()
    for retweeter in retweeters:
        retweeter.join()
    log_listener.join()

if __name__ == '__main__':
    main()

