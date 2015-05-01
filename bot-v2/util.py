#!/usr/bin/env python
# encoding: utf-8
"""
util.py

Created by Brado Subramanian on 2015-04-30.
"""

import sys
sys.path.insert(0, 'lib')

import hashlib
import tweepy

def InitializeTwitterAPI(secrets):
    auth = tweepy.OAuthHandler(secrets['consumer_key'],
                               secrets['consumer_secret'])
    auth.set_access_token(secrets['access_token'],
                          secrets['access_token_secret'])
    api = tweepy.API(auth)
    return {
        'secrets': secrets,
        'auth': auth,
        'api': api
    }

def get_key(text):
    sha = hashlib.sha1(text.encode('utf-8'))
    return sha.hexdigest()