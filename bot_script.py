#!/usr/bin/python
import sys

sys.path.insert(0, 'lib')

import tweepy
import config

auth = tweepy.OAuthHandler(config.CONFIG['consumer_key'], config.CONFIG['consumer_secret'])
auth.set_access_token(config.CONFIG['access_token'], config.CONFIG['access_token_secret'])
api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
  def on_status(self, status):
    #TODO(bharadwajs) Do some filtering here.
    if any(word in status.text for word in config.CONFIG['keywords']):
      print status.text
    #api.retweet(status.id)

  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=config.CONFIG['topics'])


