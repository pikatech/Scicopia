#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 16:27:08 2021

@author: tech
"""
import argparse
import logging
import sys
from collections import Counter
from pathlib import Path
from pickle import UnpicklingError

import elasticsearch
from elasticsearch_dsl import Completion, Document, connections
from tqdm import tqdm

from scicopia.config import read_config
from scicopia.utils.zstandard import zstd_unpickle

config = read_config()


logger = logging.getLogger("scicopia.elastic")


class Suggestion(Document):
    keywords_suggest = Completion()

    class Index:
        name = config["suggestions"]

    def save(self, **kwargs):
        return super().save(**kwargs)


def store_suggestions(phrases: Counter):
    conn = connections.create_connection(hosts=config["es_hosts"])
    Suggestion.init()
    for phrase in tqdm(phrases.keys()):
        doc = Suggestion()
        doc["keywords_suggest"] = phrase
        doc.save()


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Set up index for autocomplete suggestions"
    )
    PARSER.add_argument(
        "completions",
        type=Path,
        help="Path to a Zstandard-compressed pickled Counter containing strings",
    )
    ARGS = PARSER.parse_args()
    try:
        completions = zstd_unpickle(ARGS.completions)
    except FileNotFoundError:
        print(f"File {ARGS.completions} does not exist", file=sys.stderr)
        sys.exit(-1)
    except UnpicklingError as e:
        print(e)
        sys.exit(-2)
    else:
        try:
            store_suggestions(completions)
        except (
            elasticsearch.exceptions.RequestError,
            elasticsearch.exceptions.ConnectionError,
        ) as e:
            logger.error(e)
            print(
                "There have been errors trying to access Elasticsearch.",
                file=sys.stderr,
            )
            sys.exit(-3)
