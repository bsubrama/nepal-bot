# nepal-bot
Twitter bot for retweeting requests/offers for help.

*bot/*

Contains the bot script and the configuration for it.

The botscript basically looks for the keywords in the configuration, and retweets
statuses that match the keywords, is not stale and does not contain the excluded 
keywords. If the status has already been seen, it is not processed again; this is 
tracked using memcached (you need to install memcached). Uses RabbitMQ to make sure  are
that tweets processed even if the job fails. 

Depends on memcached and RabbitMQ.

*bot-v2*
*UPDATE: THIS BOT IS BROKEN! Some features have been moved to bot-v1.*

Contains the second version of the bot.

A better organized and failure-proof version of the bot.

1. The stream listener and retweeter code has been separated out.
2. RabbitMQ is used for passing messages between the stream listener and
the retweeters.
3. A separate controller script spawns the listener and the retweeters.
4. A fancy logging framework is now available.
5. Some better configuration management.

Depends on memcached and rabbitmq.

*admin/*

Contains the admin interface for managing the bot. This is a WIP. It is being built
with flask, flask-wtf, sqlalchemy and bootstrap. The eventual goal is for the bot to
simply read off the admin interface.

1. Manage the keywords, api keys and included/excluded keywords.
2. Moderate tweets before retweeting them.

*Installation*

- Install memcached and pip.
- git clone https://github.com/nepal-bot.git

To bring up the v1 bot:

- cd nepal-bot/bot/
- pip install -r requirements.txt -t lib/
- Install RabbitMQ and memcached.
- Add api keys and keywords to config.py
- ./logger.py in one terminal to watch log messages (or pipe them to a file)
- ./controller.py in another terminal to start off the job actual.
- http://localhost:15672/ username: guest, password: guest for RabbitMQ console. Or whatever your RabbitMQ configuration is.

The admin interface is not complete, but to bring it up do the following.

- Install pip.
- cd nepal-bot/admin/
- pip install -r requirements.txt -t lib/
- ./run.py

The v2 bot is broken - ignore it. 
