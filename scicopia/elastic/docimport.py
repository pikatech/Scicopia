#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read data from ArangoDB and save allowed fields in Elasticsearch
"""
import argparse
import logging
import sys
from datetime import datetime

from elasticsearch_dsl import (
    Boolean,
    Completion,
    Date,
    Document,
    Keyword,
    Short,
    Text,
    connections,
)
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch.helpers import streaming_bulk
from pyArango.theExceptions import DocumentNotFoundError
from tqdm import tqdm

from scicopia.config import read_config
from scicopia.exceptions import (
    ConfigError,
    DBError,
    ScicopiaException,
    SearchError,
)
from scicopia.utils.arangodb import connect, get_docs, select_db

logger = logging.getLogger("scicopia")
logger.setLevel(logging.INFO)

config = read_config()


def setup():
    """
    Connect to the Arango database and Elasticsearch.

    Returns
    -------
    Collection, Database, str, list
        1. The ArangoDB collection that holds the scientific documents
        2. The ArangoDB database that holds the collection
        3. The name of the collection
        4. The list of fields that are take over from ArangoDB to Elasticsearch

    Raises
    ------
    ConfigError
        If a required entry is missing in the config file.
    DBError
        If the connection to the ArangoDB server failed or the database
        or the collection can not be found.
    SearchError
        If the connection to the Elasticsearch server failed.
    """
    if not "es_hosts" in config:
        raise ConfigError("Setting missing in config file: 'es_hosts'.")
    conn = connections.create_connection(hosts=config["es_hosts"])
    if not conn.ping():
        raise SearchError("Connection to the Elasticsearch server failed.")
    try:
        arangoconn = connect(config)
        db = select_db(config, arangoconn)
        docs = get_docs(config, db)
    except (ConfigError, DBError) as e:
        logger.error(e)
        raise e

    if not "fields" in config:
        raise ConfigError("Setting missing in config file: 'fields'.")
    allowed = config["fields"]
    if not "index" in config:
        raise ConfigError("Setting missing in config file: 'index'.")

    return docs, db, allowed, conn, config["index"]


# Used to declare the structure of documents and to
# initialize the Elasticsearch index with the correct data types
class Bibdoc(Document):
    entrytype = Keyword()
    author = Keyword(multi=True)
    editor = Keyword(multi=True)
    publisher = Keyword()
    institution = Keyword()
    title = Text()
    title_suggest = Completion()
    booktitle = Text()
    abstract = Text()
    keywords = Keyword()
    tags = Keyword()
    year = Short()
    date = Keyword()
    pages = Keyword()
    journal = Text()
    volume = Keyword()
    number = Keyword()
    graph = Boolean()
    doi = Keyword()
    created_at = Date()

    class Index:
        name = config["index"]

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)


def index(query, collection, allowed, es_index):
    for key in query:
        elastic_doc = Bibdoc(meta={"id": key})
        arango_doc = collection[key]
        if "cited_by" in arango_doc or "citing" in arango_doc:
            elastic_doc["graph"] = True
        for field in allowed:
            if field == "year" and "year" in arango_doc:
                year = arango_doc[field]
                try:
                    elastic_doc["year"] = int(year)
                except ValueError:
                    logging.warning("Can't parse year %s in document %s", year, key)
                    continue
            elif field == "abstract":
                abstract_arango = arango_doc[field]
                if abstract_arango:
                    if arango_doc["abstract_offsets"]:
                        elastic_doc["abstract"] = [
                            abstract_arango[start:end]
                            for start, end in arango_doc["abstract_offsets"]
                        ]
                    else:
                        logging.warning(
                            f"No offset for saving abstract in '{key}'."
                        )
            else:
                arango = arango_doc[field]
                if arango:
                    elastic_doc[field] = arango
        arango_doc["elastic"] = round(datetime.now().timestamp())
        arango_doc.save()
        doc = {
            "_op_type": "index",
            "_index": es_index,
            "_id": key
        }
        doc["_source"] = elastic_doc
        yield doc


def main(timestamp: int):
    collection, db, allowed, conn, es_index = setup()
    Bibdoc.init()
    if timestamp != 0:
        aql = f"FOR x IN {collection.name} FILTER (x.elastic == null OR x.elastic < x.modified_at) AND x.modified_at > {timestamp} RETURN x._key"
    else:
        aql = f"FOR x IN {collection.name} FILTER (x.elastic == null OR x.elastic < x.modified_at) RETURN x._key"
    BATCHSIZE = 100
    TTL = BATCHSIZE * 10  # Time-to-live
    query = db.AQLQuery(aql, rawResults=True, batchSize=BATCHSIZE, ttl=TTL)
    unfinished = (
        query.response["extra"]["stats"]["scannedFull"]
        - query.response["extra"]["stats"]["filtered"]
    )
    if unfinished == 0:
        logging.info("Elasticsearch is up to date")
        return
    logging.info(f"{unfinished} documents in found.")
    try:
        for ok, action in tqdm(streaming_bulk(
                index=es_index,
                client=conn,
                actions=index(query, collection, allowed, es_index),
                raise_on_error=False,
                request_timeout=60,
            )):
                if not ok and action["index"]["status"] != 409:
                    logger.warning(action)
    except ConnectionTimeout as e:
        logger.warning(
            "Timeout occurred while indexing"
        )
        logger.warning(e)
    except DocumentNotFoundError:
        pass


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Imports documents from ArangoDB into Elasticsearch"
    )
    PARSER.add_argument(
        "-t",
        "--recent",
        help="Documents that are more recent than this timestamp",
        default=0,
        type=int,
    )
    ARGS = PARSER.parse_args()
    try:
        main(ARGS.recent)
    except ScicopiaException as e:
        logger.error(e)
        sys.exit(-1)
