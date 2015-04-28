import config

if (config.CONFIG['consumer_key'] != '' or
    config.CONFIG['consumer_secret'] != '' or
    config.CONFIG['access_token'] != '' or
    config.CONFIG['access_token_secret'] != ''):
  print 'config.py contains API access keys. Remove them before committing.'
  exit(1)
