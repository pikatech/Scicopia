#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read data from ArangoDB and save allowed fields in Elasticsearch
"""
import argparse
import logging
from datetime import datetime

from elasticsearch_dsl import (Completion, Date, Document, Keyword, Short,
                               Text, connections)
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError
from tqdm import tqdm

from scicopia.config import read_config

config = read_config()

def setup():
    conn = connections.create_connection(hosts=config["es_hosts"])
    if "arango_url" in config:
        arangoconn = Connection(
            arangoURL=config["arango_url"],
            username=config["username"],
            password=config["password"],
        )
    else:
        arangoconn = Connection(
            username=config["username"], password=config["password"]
        )

    if arangoconn.hasDatabase(config["database"]):
        db = arangoconn[config["database"]]
    else:
        logging.error(f"Database {config['database']} not found.")

    if db.hasCollection(config["collection"]):
        coll = db[config["collection"]]
    else:
        logging.error(f"Collection {config['collection']} not found.")

    allowed = config["fields"]

    return coll, db, config["collection"], allowed


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
    auto_tags = Keyword()
    year = Short()
    date = Keyword()
    pages = Keyword()
    journal = Text()
    volume = Keyword()
    number = Keyword()
    doi = Keyword()
    created_at = Date()

    class Index:
        name = config["index"]

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)


def main(timestamp: int):
    collection, db, collectionName, allowed = setup()
    Bibdoc.init()
    if timestamp != 0:
        aql = f"FOR x IN {collectionName} FILTER (x.elastic == null OR x.elastic < x.modified_at) AND x.modified_at > {timestamp} RETURN x._key"
    else:
        aql = f"FOR x IN {collectionName} FILTER (x.elastic == null OR x.elastic < x.modified_at) RETURN x._key"
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
    for key in tqdm(query):
        doc = Bibdoc(meta={"id": key})
        arangodoc = collection[key]
        try:
            for field in allowed:
                if field == "abstract":
                    abstract_arango = arangodoc[field]
                    abstract_elastic = []
                    if abstract_arango:
                        if arangodoc["abstract_offsets"]:
                            for start, end in arangodoc["abstract_offsets"]:
                                abstract_elastic.append(abstract_arango[start:end])
                                doc["abstract"] = abstract_elastic
                        else:
                            logging.warning(f"No offset for saving abstract in {key}.")
                else:
                    arango = arangodoc[field]
                    if arango:
                        doc[field] = arango
            arangodoc["elastic"] = round(datetime.now().timestamp())
            arangodoc.save()
        except DocumentNotFoundError:
            pass
        doc.save()


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
    main(ARGS.recent)
