#!/usr/bin/env python
# encoding: utf-8
"""
logger.py

Created by Brado Subramanian on 2015-04-30.
Copyright (c) 2015 __MyCompanyName__. All rights reserved.
"""

import sys
sys.path.insert(0, 'lib')

import pika
import time
import config

_DEFAULT_QUEUE_NAME = 'log_messages'

class Logger(object):
    def _ts(self):
        return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ']'
        
    def __init__(self, queue_name=None):
        self.queue_name = _DEFAULT_QUEUE_NAME
        if queue_name:
            self.queue_name = queue_name
        # Set up a queue for logging
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.CONFIG['rabbitmq_host']))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def log(self, entry):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=' '.join([self._ts(), __name__, entry])) 

_LOGGER = Logger()

def log(entry):
    msg = entry
    # Try a string conversion
    if not isinstance(entry, str) and not isinstance(entry, unicode):
        msg = str(entry)
    _LOGGER.log(msg)

def _callback(ch, method, properties, body):
    print body
    ch.basic_ack(delivery_tag=method.delivery_tag)
        
class LogListener(object):
    _DEFAULT_QUEUE_NAME = 'log_messages'
    def __init__(self, queue_name=None):
        self.queue_name = _DEFAULT_QUEUE_NAME
        if queue_name:
            self.queue_name = queue_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.CONFIG['rabbitmq_host']))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def listen(self):
        self.channel.basic_consume(_callback, queue=self.queue_name)
        self.channel.start_consuming()

def run_log_listener_as_process():
    listener = LogListener()
    listener.listen()

if __name__ == '__main__':
    pass

