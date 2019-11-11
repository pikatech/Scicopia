
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import base64
import glob
import logging
import os

import time

from datetime import datetime
from elasticsearch_dsl import Document, Date, Completion, Keyword, Text, \
Short, connections

from pyArango.connection import Connection
from pyArango.theExceptions import CreationError

from pybtex.database import parse_file
from pybtex.exceptions import PybtexError

from config import read_config
    
config = read_config()
conn = connections.create_connection(hosts=config.hosts)
arangoconn = Connection(username = config.username, password = config.password) # connection to ArangoDB
if arangoconn.hasDatabase(config.database):
    db = arangoconn[config.database]
else:
    db = arangoconn.createDatabase(name = config.database) 
if db.hasCollection(config.collection):
    pdfc = db[config.collection]
else:
    pdfc = db.createCollection(name = config.collection)
# verbindung zu arango

allowed = {'author', 'editor', 'publisher', 'institution', 'title',
        'booktitle', 'abstract', 'keywords', 'year', 'pages', 'journal',
        'volume', 'number', 'doi', 'cited-by', 'citing'}

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
    keywords = Text()
    auto_tags = Text()
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
        name = 'library'

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)


def bib(dir):
    bibfiles = glob.glob(dir + "*.bib", recursive=True)
    Bibdoc.init()
    # es = Elasticsearch(hosts=['localhost'])

    pair = {}
    start = time.time()
    for bibfile in bibfiles:
        file_stats = os.stat(bibfile)
        if file_stats.st_size == 0:
            logging.warning('{} is empty\n'.format(bibfile))
            continue
        try:
            bib_data = parse_file(bibfile)
            if len(bib_data.entries) > 1:
                # was ist falls bib data mehrere einträge enthält?
                # titel findet sich nicht unbedingt 1:1 in pdf name
                continue
            for entry in bib_data.entries.itervalues():
                    key = parse(entry)
                    pair[key] = bibfile[:bibfile.rindex(".")]+".pdf" 
                    # funktioniert nur, wenn bib name und pdf name gleich sind
        except PybtexError as p:
            logging.error('{}: {}\n'.format(bibfile, p))
    ende = time.time()
    print('{:5.3f}s'.format(ende-start))

    start = time.time()
    for key in pair:
        pdf(key, pair[key])
    ende = time.time()
    print('{:5.3f}s'.format(ende-start))


def parse(entry):
    doc = Bibdoc(meta = {'id': entry.key})
    doc.entrytype = entry.type
    for field in entry.fields.items():
        fieldname = field[0].lower()
        if fieldname in allowed:
            # Non-standard field in personal library
            if field[0] == 'cited-by':
                doc.cited_by = field[1]
            else:
                doc[fieldname] = field[1]
    for item in entry.persons.items():
        persons = []
        for person in item[1]:
            names = []
            names.extend(person.first_names)
            names.extend(person.middle_names)
            names.extend(person.prelast_names)
            names.extend(person.lineage_names)
            names.extend(person.last_names)
            persons.append(' '.join(names))
        doc[item[0]] = persons
    doc.save()
    return entry.key


def pdf(key, file):
    with open(file, 'rb') as f:
        data = base64.b64encode(f.read()) # umwandeln der pdf zu base64
        doc = pdfc.createDocument()
        doc._key = key # key ist schlüssel der dazugehörigen bib data
        doc["data"] = data.decode()
        try:
            doc.save()
        except CreationError as c:
            logging.warning('{}: {}\n'.format(key, c))
        # speichern der base64 in arango
