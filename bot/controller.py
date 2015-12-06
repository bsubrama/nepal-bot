#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
import sys

sys.path.insert(0, 'lib')

import hashlib
import memcache
import tweepy
import config
import time
import logger
import pika
import pickle
import subprocess
import time

def run_processes():
    print 'Starting stream listener'
    stream_listener = subprocess.Popen('./stream_listener.py', shell=True)
    print 'Starting retweeter'
    retweeter = subprocess.Popen('./retweeter.py', shell=True)
    while True:
        stream_listener.poll()
        retweeter.poll()
        if stream_listener.returncode is not None:
            print 'Stream listener is dead; killing retweeter'
            retweeter.terminate()
            return True
        if retweeter.returncode is not None:
            print 'Retweeter is dead; killing stream listener'
            stream_listener.terminate()
            return True
        time.sleep(60)
    return False

while run_processes():
    pass