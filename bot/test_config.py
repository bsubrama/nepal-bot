import config

for name, secret in config.CONFIG['accounts'].iteritems():
    if (secret['consumer_key'] != '' or
        secret['consumer_secret'] != '' or
        secret['access_token'] != '' or
        secret['access_token_secret'] != ''):
        print 'config.py contains API access keys. Remove them before committing.'
    exit(1)
