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

from multiprocessing import Process, Queue

apis = {}
for name, secrets in config.CONFIG['accounts'].iteritems():
    auth = tweepy.OAuthHandler(secrets['consumer_key'], secrets['consumer_secret'])
    auth.set_access_token(secrets['access_token'], secrets['access_token_secret'])
    api = tweepy.API(auth)
    apis[name] = {
        'secrets': secrets,
        'auth': auth,
        'api': api
    }

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

queue = Queue()

def ts():
  return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ']'

def retweet(queue, name, api, tweets_per_hour):
  for tweet_num, status in iter(queue.get, 'STOP'):
    try:
      api.retweet(status.id)
      print ts(), '@' + name, 'tweeted ', str(status.id), status.text.encode('utf-8'), ' tweet_num:', str(tweet_num)
      time.sleep(3600/tweets_per_hour)
    except tweepy.TweepError as e:
      print ts(), e
    sys.stdout.flush()
  queue.close()
  return True

class CustomStreamListener(tweepy.StreamListener):

  def __init__(self):
    tweepy.StreamListener.__init__(self)
    self.scheduled = 0

  def get_key(self, text):
    sha = hashlib.sha1(text.encode('utf-8'))
    return sha.hexdigest()

  def on_status(self, status):
    key = self.get_key(status.text) + '-text'
    prev_status = mc.get(key)

    if (status.user.screen_name not in apis.keys() and
        not prev_status and
        any(word in status.text for word in config.CONFIG['keywords']) and
        not any(word in status.text for word in config.CONFIG['excluded_keywords'])):
      mc.set(key, status)
      self.scheduled += 1
      print ts(), 'scheduling tweet_id', str(status.id), ' from ', status.user.screen_name, ' matching ', ','.join([word for word in config.CONFIG['keywords']  if word in status.text]), 'as tweet_num:', self.scheduled
      queue.put((self.scheduled, status))
      sys.stdout.flush()

  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True

original_sigint_handler = signal.getsignal(signal.SIGINT)

def sigint_handler(sig, frame):
  signal.signal(signal.SIGINT, original_sigint_handler)
  print 'new sigint handler caught'
  queue.put('STOP')
  sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

print 'starting retweeters'
retweeters = {}
for name, entry in apis.iteritems():
    retweeters[name] = Process(target=retweet, args=(queue, name, entry['api'], entry['secrets']['tweets_per_hour']))
    retweeters[name].start()

auth = apis.values()[0]['auth']
sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=config.CONFIG['topics'])

for name, process in retweeters.iteritems():
    process.join()
