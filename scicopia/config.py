import json
from os.path import exists, join
import sys

CONFIG = join("..", "config.json")


def read_config():
    if exists(CONFIG):
        with open(CONFIG) as config:
            conf = json.load(config)
    else:
        print("Could not find configuration file {0}.".format(CONFIG))
        sys.exit(1)

    return conf
