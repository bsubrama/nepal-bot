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
import config
import datetime
from multiprocessing import Process

# Initialize RabbitMQ
logger.log('Initializing RabbitMQ queue')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=config.CONFIG['rabbitmq_config']['host']))
channel = connection.channel()
channel.queue_declare(queue=config.CONFIG['rabbitmq_config']['queue'], durable=True)

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
              timediff = datetime.datetime.now() - status.created_at
              if timediff.total_seconds() < config.CONFIG['tweet_age'] * 3600:
                self.api['api'].retweet(status.id)
                logger.log(' '.join(['@' + self.handle,
                           'tweeted ', str(status.id), status.text.encode('utf-8'),
                           ' tweet_num:', str(tweet_num)]))
                time.sleep(3600/self.account_config['tweets_per_hour'])
              else:
                logger.log(' '.join(['Skipped tweet_num:', str(tweet_num),
                           'by @', self.handle, 'due to staleness.']))
            except tweepy.TweepError as e:
              logger.log(e)
              logger.log('Rescheduling for redelivery')
              channel.basic_publish(exchange='',
                                    routing_key=config.CONFIG['rabbitmq_config']['queue'],
                                    body=pickle.dumps((tweet_num, status)),
                                    properties=pika.BasicProperties(delivery_mode=2))
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

def run_retweeter(handle, account_config, rabbitmq_config):
    logger.log('called run')
    retweeter = Retweeter(handle, account_config, rabbitmq_config)
    retweeter.start()

rabbitmq_config = config.CONFIG['rabbitmq_config']
run_retweeter(config.CONFIG['accounts'].keys()[0], config.CONFIG['accounts'].values()[0], rabbitmq_config)