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
from typing import Any, Dict, Iterator, Iterable

import elasticsearch
from elasticsearch.helpers import streaming_bulk
from elasticsearch.exceptions import ConnectionTimeout
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

    try:
        for ok, action in tqdm(streaming_bulk(
            index=config["suggestions"],
            client=conn,
            actions=index(phrases),
            raise_on_error=False,
            request_timeout=60,
            chunk_size=10_000,
            max_chunk_bytes=10*1024**2,
        )):
            if not ok and action["index"]["status"] != 409:
                logger.warning(action)
    except ConnectionTimeout as e:
        logger.warning(
            "Timeout occurred while processing suggestions"
        )


def index(suggestions: Iterable) -> Iterator[Dict[str, Any]]:
    for i, suggestion in enumerate(suggestions.items(), 1):
        doc = {
            "_op_type": "index",
            "_index": config["suggestions"],
            "_id": i
        }
        doc["_source"] = {"keywords_suggest": suggestion[0], "weight": suggestion[1]}
        print(doc)
        yield doc

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
