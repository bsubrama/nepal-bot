#!/usr/bin/env python
# encoding: utf-8
"""
retweeter.py

Created by Brado Subramanian on 2015-04-30.
"""

import sys
sys.path.insert(0, 'lib')

import pika
import tweepy
import util
import logger
import pickle
import time

class Retweeter(object):
    def __init__(self, handle, account_config, rabbitmq_config):
        self.handle = handle
        self.account_config = account_config
        self.rabbitmq_config = rabbitmq_config
        
        self.api = util.InitializeTwitterAPI(account_config)

    # ch = 'tweets', body = (tweet_num, status)
    def _get_callback(self):
        def _callback(ch, method, properties, body):
            tweet_num, status = pickle.loads(body)
            logger.log('Received tweet_num=%d' % (tweet_num,))
            try:
              self.api['api'].retweet(status.id)
              logger.log(' '.join(['@' + self.handle,
                                   'tweeted ', str(status.id), status.text.encode('utf-8'),
                                   ' tweet_num:', str(tweet_num)]))
              time.sleep(3600/self.account_config['tweets_per_hour'])
            except tweepy.TweepError as e:
              logger.log(e)
            sys.stdout.flush()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return _callback

    def start(self):
        logger.log('Retweeter ' + self.handle + ' started, waiting for messages.')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbitmq_config['host']))
        channel = connection.channel()
        channel.queue_declare(queue=self.rabbitmq_config['queue'], durable=True)
        channel.basic_consume(self._get_callback(), queue=self.rabbitmq_config['queue'])
        channel.start_consuming()

def run(handle, account_config, rabbitmq_config):
    retweeter = Retweeter(handle, account_config, rabbitmq_config)
    retweeter.start()
    
if __name__ == '__main__':
    pass