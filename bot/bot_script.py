#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, 'lib')

import hashlib
import memcache
import tweepy
import config
import time

auth = tweepy.OAuthHandler(config.CONFIG['consumer_key'], config.CONFIG['consumer_secret'])
auth.set_access_token(config.CONFIG['access_token'], config.CONFIG['access_token_secret'])
api = tweepy.API(auth)

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

def ts():
  return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ']'

class CustomStreamListener(tweepy.StreamListener):
  def get_key(self, text):
    sha = hashlib.sha1(text.encode('utf-8'))
    return sha.hexdigest()

  def on_status(self, status):
    #TODO(bharadwajs) Do some filtering here.i
    key = self.get_key(status.text) + '-text'
    prev_status = mc.get(key)

    if (not prev_tweet and not prev_status and
        any(word in status.text for word in config.CONFIG['keywords']) and
        not any(word in status.text for word in config.CONFIG['excluded_keywords'])):
      mc.set(key, status)
      print ts(), 'tweet matched', ','.join([word in status.text for word in config.CONFIG['keywords']])
      try:
        api.retweet(status.id)
        print ts(), status.text.encode('utf-8')
      except tweepy.TweepError:
        print ts(), 'tried retweeting previously retweeted id ', str(status.id)
      sys.stdout.flush()


  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=config.CONFIG['topics'])
