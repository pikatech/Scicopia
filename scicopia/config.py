import json
from os.path import exists
import sys
from typing import Any, Dict

CONFIG = "config.json"


def read_config() -> Dict[str, Any]:
    if exists(CONFIG):
        with open(CONFIG) as config:
            conf = json.load(config)
    else:
        print("Could not find configuration file {0}.".format(CONFIG))
        sys.exit(1)

    return conf
