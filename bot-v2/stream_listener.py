#!/usr/bin/env python
# encoding: utf-8
"""
stream_listener.py

Created by Brado Subramanian on 2015-04-30.
Copyright (c) 2015 __MyCompanyName__. All rights reserved.
"""

import sys

sys.path.insert(0, 'lib')

import hashlib
import memcache
import tweepy
import config
import util
import time
import pika
import logger
import requests
import pickle

class CustomStreamListener(tweepy.StreamListener):

  def __init__(self, cache, channel):
    tweepy.StreamListener.__init__(self)
    self.tweet_num = 0
    self.cache = cache
    self.channel = channel

  def on_status(self, status):
    key = util.get_key(status.text) + '-text'
    prev_status = self.cache.get(key)

    if (status.user.screen_name not in config.CONFIG['excluded_accounts'] and
        not prev_status and
        any(word in status.text for word in config.CONFIG['keywords']) and
        not any(word in status.text
                for word in config.CONFIG['excluded_keywords'])):
      self.cache.set(key, status)
      self.tweet_num += 1
      logger.log(' '.join(['scheduling tweet_id', str(status.id),
                           'from', status.user.screen_name,
                           'matching', ','.join([word for word in config.CONFIG['keywords'] 
                                                if word in status.text]),
                           'as tweet_num:', str(self.tweet_num)]))

      self.channel.basic_publish(exchange='',
                                 routing_key=config.CONFIG['rabbitmq_queue'],
                                 body=pickle.dumps((self.tweet_num, status)),
                                 properties=pika.BasicProperties(delivery_mode=2))
      sys.stdout.flush()

  def on_error(self, status_code):
    logger.log(' '.join(['Encountered error with status code:', str(status_code)]))
    return True

  def on_timeout(self):
    logger.log('Timeout...')
    return True

def main():
    logger.log('Initializing stream listener')
    
    # Initialize API
    api = util.InitializeTwitterAPI(config.CONFIG['accounts'].values()[0])
    auth = api['auth']
    
    # Initialize memcache
    logger.log('Initializing memcache client')
    mc = memcache.Client([config.CONFIG['memcache_server']], debug=0)
    
    # Initialize pika
    logger.log('Initializing RabbitMQ queue')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.CONFIG['rabbitmq_host']))
    channel = connection.channel()
    channel.queue_declare(queue=config.CONFIG['rabbitmq_queue'], durable=True)
    try:
        # Start listening
        logger.log('Starting to listen')
        sapi = tweepy.streaming.Stream(auth, CustomStreamListener(mc, channel))
        sapi.filter(track=config.CONFIG['topics'])
    except requests.ConnectionError as e:
        logger.log(str(e))

if __name__ == '__main__':
	main()

