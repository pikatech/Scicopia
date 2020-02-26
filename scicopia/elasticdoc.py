# read data from arangodb and save allowed fields in elasticsearch
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
conn = connections.create_connection(hosts=config.hosts)
arangoconn = Connection(username=config.username, password=config.password)
if arangoconn.hasDatabase(config.database):
    db = arangoconn[config.database]
else:
    logging.error(f"Database {config.database} not found.")
if db.hasCollection(config.collection):
    coll = db[config.collection]
else:
    logging.error(f"Collection {config.collection} not found.")

allowed = {
    "author",
    "editor",
    "publisher",
    "institution",
    "title",
    "booktitle",
    "abstract",
    "keywords",
    "auto_tags",
    "year",
    "pages",
    "journal",
    "volume",
    "number",
    "doi",
    "cited_by",
    "citing",
}
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
    pages = Keyword()
    journal = Text()
    volume = Keyword()
    number = Keyword()
    doi = Keyword()
    cited_by = Keyword(multi=True)
    citing = Keyword(multi=True)
    created_at = Date()

    class Index:
        name = config.index

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)


def main():
    Bibdoc.init()
    queryResult = coll.fetchAll()
    bar = Bar("entries", max=len(queryResult))
    for entry in queryResult:
        doc = Bibdoc(meta={"id": entry._key})
        for field in allowed:
            try:
                doc[field] = entry[field]
            except DocumentNotFoundError as ignore:
                pass
        doc.save()
        bar.next()
    bar.finish()


if __name__ == "__main__":
    main()
