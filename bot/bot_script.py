#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, 'lib')

import hashlib
import memcache
import tweepy
import config

auth = tweepy.OAuthHandler(config.CONFIG['consumer_key'], config.CONFIG['consumer_secret'])
auth.set_access_token(config.CONFIG['access_token'], config.CONFIG['access_token_secret'])
api = tweepy.API(auth)

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

class CustomStreamListener(tweepy.StreamListener):
  def get_key(self, text):
    sha = hashlib.sha1(text.encode('utf-8'))
    return sha.hexdigest()

  def on_status(self, status):
    #TODO(bharadwajs) Do some filtering here.i
    key = self.get_key(status.text) + '-text'
    prev_status = mc.get(key)
    prev_tweet = mc.get(str(status.id) + '-key')

    if (not prev_tweet and not prev_status and
        any(word in status.text for word in config.CONFIG['keywords']) and
        not any(word in status.text for word in config.CONFIG['excluded_keywords'])):
      mc.set(key, status)
      print status.text
      try:
        api.retweet(status.id)
      except tweepy.TweepError:
        print 'tried retweeting previously retweeted id ', status.id


  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=config.CONFIG['topics'])
