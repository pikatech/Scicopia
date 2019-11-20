from collections import namedtuple
import json
from os.path import exists
import sys

Config = namedtuple('Config', ['username', 'password', 'secret', 'hosts',
                               'index', 'database', 'collection',
                               'usercollection', 'mailusername',
                               'mailpassword'])
CONFIG = 'config.json'

def read_config():
    if exists(CONFIG):
        with open(CONFIG) as config:
            conf = json.load(config)
    else:
        print("Could not find configuration file {0}.".format(CONFIG))
        sys.exit(1)
    
    return Config(
        username = conf['username'],
        password = conf['password'],
        secret = conf['secret_key'],
        hosts = conf['es_hosts'],
        index = conf['index'],
        database = conf['database'],
        collection = conf['collection'],
        usercollection = conf['usercollection'],
        mailusername = conf['mailusername'],
        mailpassword = conf['mailpassword']
    )

