# read data from arangodb and save allowed fields in elasticsearch
import argparse
import logging
from datetime import datetime
from elasticsearch_dsl import (
    Document,
    Date,
    Completion,
    Keyword,
    Text,
    Short,
    connections,
)
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError
from config import read_config
from progress.bar import Bar

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
        aql = f"FOR x IN {collectionName} FILTER x.modified_at > {timestamp} RETURN x._key"
    else:
        aql = f"FOR x IN {collectionName} RETURN x._key"
    BATCHSIZE = 100
    TTL = BATCHSIZE * 10 # Time-to-live
    query = db.AQLQuery(aql, rawResults=True, batchSize=10, ttl=TTL)
    bar = Bar("entries", max=collection.count())
    for key in query:
        doc = Bibdoc(meta={"id": key})
        arangodoc = collection[key]
        for field in allowed:
            try:
                if field == "abstract":
                    abstract_arango = arangodoc[field]
                    abstract_elastic = []
                    if arangodoc["abstract_offsets"]:
                        for start, end in arangodoc["abstract_offsets"]:
                            abstract_elastic.append(abstract_arango[start:end])
                            doc['abstract'] = abstract_elastic
                    else:
                        logging.warning(f"No offset for saving abstract in {key}.")
                else:
                    doc[field] = arangodoc[field]
            except DocumentNotFoundError:
                pass
        doc.save()
        bar.next()
    bar.finish()


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Imports documents from ArangoDB into Elasticsearch")
    PARSER.add_argument("-t", "--recent", help="Documents that are more recent than this timestamp", default=0, type=int)
    ARGS = PARSER.parse_args()
    main(ARGS.recent)
