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
import config
import util
import argparse
import logger
import pickle
import time

#def retweet(queue, name, api, tweets_per_hour):
#  for tweet_num, status in iter(queue.get, 'STOP'):
#    try:
#      api.retweet(status.id)
#      print ts(), '@' + name, 'tweeted ', str(status.id), status.text.encode('utf-8'), ' tweet_num:', str(tweet_num)
#      time.sleep(3600/tweets_per_hour)
#    except tweepy.TweepError as e:
#      print ts(), e
#    sys.stdout.flush()
#  queue.close()
#  return True

parser = argparse.ArgumentParser(description='Listen on RabbitMQ queue and retweet tweets that come in.')
parser.add_argument('--handle', type=str, help='The handle to retweet the incoming tweets as')
parser.add_argument('--tweets_per_hour', type=int, help='The number of tweets to retweet per hour')

# ch = tweets, body = (tweet_num, status)
def _get_callback(args, api):
    def _callback(ch, method, properties, body):
        tweet_num, status = pickle.loads(body)
        logger.log('[x] Received tweet_num=%d' % (tweet_num,))
        try:
          api['api'].retweet(status.id)
          logger.log(' '.join(['@' + args.handle,
                               'tweeted ', str(status.id), status.text.encode('utf-8'),
                               ' tweet_num:', str(tweet_num)]))
          time.sleep(3600/args.tweets_per_hour)
        except tweepy.TweepError as e:
          logger.log(e)
        sys.stdout.flush()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    return _callback

def run_as_process(handle, tweets_per_hour):
    args = parser.parse_args(args=['--handle', handle, '--tweets_per_hour', str(tweets_per_hour)])
    main(args)

def main(args):
    logger.log(' '.join(['[*] Retweeter started with', str(args), 'waiting for messages.']))
    api = util.InitializeTwitterAPI(config.CONFIG['accounts'][args.handle])
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.CONFIG['rabbitmq_host']))
    channel = connection.channel()
    channel.queue_declare(queue=config.CONFIG['rabbitmq_queue'], durable=True)
    channel.basic_consume(_get_callback(args, api), queue=config.CONFIG['rabbitmq_queue'])
    channel.start_consuming()

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)