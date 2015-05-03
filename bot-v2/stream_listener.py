#!/usr/bin/env python
# encoding: utf-8
"""
stream_listener.py

Created by Brado Subramanian on 2015-04-30.
"""

import sys

sys.path.insert(0, 'lib')

import hashlib
import memcache
import tweepy
import util
import time
import pika
import logger
import requests
import pickle

class CustomStreamListener(tweepy.StreamListener):

  def __init__(self, account_config, memcache_config, rabbitmq_config):
    tweepy.StreamListener.__init__(self)
    self.tweet_num = 0
    
    # Initialize API
    self.api = util.InitializeTwitterAPI(account_config)
    self.auth = self.api['auth']
    self.account_config = account_config

    # Initialize memcache
    logger.log('Initializing memcache client')
    self.cache = memcache.Client([memcache_config['server'],], debug=0)
    self.memcache_config = memcache_config

    # Initialize RabbitMQ
    logger.log('Initializing RabbitMQ queue')
    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_config['host']))
    self.channel = self.connection.channel()
    self.channel.queue_declare(queue=rabbitmq_config['queue'], durable=True)
    self.rabbitmq_config = rabbitmq_config

  def on_status(self, status):
    key = util.get_key(status.text) + '-text'
    prev_status = self.cache.get(key)

    if (status.user.screen_name not in self.filter_config['excluded_accounts'] and
        not prev_status and
        any(word in status.text for word in self.filter_config['keywords']) and
        not any(word in status.text
                for word in self.filter_config['excluded_keywords'])):
      self.cache.set(key, status)
      self.tweet_num += 1
      logger.log(' '.join(['scheduling tweet_id', str(status.id),
                           'from', status.user.screen_name,
                           'matching', ','.join([word for word in self.filter_config['keywords'] 
                                                if word in status.text]),
                           'as tweet_num:', str(self.tweet_num)]))

      self.channel.basic_publish(exchange='',
                                 routing_key=self.rabbitmq_config['queue'],
                                 body=pickle.dumps((self.tweet_num, status)),
                                 properties=pika.BasicProperties(delivery_mode=2))
      sys.stdout.flush()

  def on_error(self, status_code):
    logger.log(' '.join(['Encountered error with status code:', str(status_code)]))
    return True

  def on_timeout(self):
    logger.log('Timeout...')
    return True

  def start(self, filter_config):
      try:
          logger.log('Starting to listen')
          sapi = tweepy.streaming.Stream(self.auth, self)
          sapi.filter(track=filter_config['topics'])
      except requests.ConnectionError as e:
          logger.log(e)

def run(account_config, memcache_config, rabbitmq_config, filter_config):
    logger.log('Initializing stream listener')
    listener = CustomStreamListener(account_config, memcache_config, rabbitmq_config)
    listener.start(filter_config)

if __name__ == '__main__':
	pass

