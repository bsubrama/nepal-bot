# nepal-bot
Twitter bot for retweeting requests/offers for help.

*bot/*

Contains the bot script and the configuration for it.

The botscript basically looks for the keywords in the configuration, and retweets
statuses that match the keywords and does not contain the excluded keywords. If
the status has already been seen, it is not processed again; this is tracked using
memcached (you need to install memcached).

Depends on memcached.

*bot-v2*

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
- Add api keys and keywords to config.py
- ./bot_script.py to start off the job.

To bring up the v2 bot:

- cd nepal-bot/bot-v2/
- pip install -r requirements.txt -t lib/
- Add api keys and configs to config.py
- ./controller.py to start off the controller.

The admin interface is not complete, but to bring it up do the following.

- Install pip.
- cd nepal-bot/admin/
- pip install -r requirements.txt -t lib/
- ./run.py
