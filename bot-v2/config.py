CONFIG = {
    'accounts': {
        'nepalrisesmod': {
            'consumer_key': '',
            'consumer_secret': '',
            'access_token': '',
            'access_token_secret': '',
            'tweets_per_hour': 100,
            },
        'nprisesmod1': {
            'consumer_key': '',
            'consumer_secret': '',
            'access_token': '',
            'access_token_secret': '',
            'tweets_per_hour': 100,
            },
    },
    'filters': {
        'excluded_accounts': ['nepalrises', 'nprisesmod1', 'nepalrisesmod'],
        'topics': ['#nepalquake', '#nepalquakerelief', '#nepalearthquake',
                   '#nepalquakerescue', '#nepalrescue', '#act4quake',
                   '#helpnepal', '#earthquake', 'sindhupalchowk', 'sindhupalchok',
                   'kathmandu', 'dhading', 'rasuwa', 'gorkha', 'nuwakot', 'ramechapp'],
        'excluded_keywords': ['donate', 'report', 'follow', 'damage', 'organization',
                              'say', 'thoughts', 'prayers', 'efforts', 'learn',
                              'rescued', 'recovered', 'evacuated', 'increase', 'rise',
                              'death toll', 'recovery', 'bjp', 'tells', 'prayer', 'proud',
                              'struggles', 'solidarity', 'baltimore', 'beef'],
        'keywords': ['food','tent','water','medicine','danger','urgent',
                     'emergency','assist','necessary','medicines','rescue',
                     'need','clothe','clothes','volunteer','relief','meds','aid', 'seeking',
                     'hospital', 'immediate', 'sindhupalchowk', 'sindhupalchok',
                     'transport', 'dhading', 'rasuwa', 'gorkha', 'contact', 'nuwakot', 'send',
                     'ramechapp', ],
    },
    'memcache': {
        'server': '127.0.0.1:11211',
    },
    'rabbitmq': {
        'host': 'localhost',
        'queue': 'tweets',
    }
}
