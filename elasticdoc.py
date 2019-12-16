
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
from progress.bar import Bar
import time

import pke
import string
from nltk.corpus import stopwords

from datetime import datetime
from elasticsearch_dsl import (Document, Date, Completion, Keyword, Text,
                               Short, connections)

from pyArango.connection import Connection

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
    coll = db[config.collection]
else:
    coll = db.createCollection(name = config.collection)
# verbindung zu arango
index = config.index
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
        name = index

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)


def bib(path):
    path = path if path.endswith(os.path.sep) else path + os.path.sep
    bibfiles = glob.glob(path + "*.bib", recursive=True)
    print("files geholt")
    Bibdoc.init()
    print("bib initialisiert")

    start = time.time()
    bar = Bar('Bibfiles', max=len(bibfiles))
    for bibfile in bibfiles:
        file_stats = os.stat(bibfile)
        if file_stats.st_size == 0:
            logging.warning('{} is empty\n'.format(bibfile))
            continue
        try:
            bib_data = parse_file(bibfile)
            if len(bib_data.entries) > 1:
                for entry in bib_data.entries.itervalues():
                    parse(entry)
            else:
                for entry in bib_data.entries.itervalues():
                    parse(entry, bibfile[:bibfile.rindex(".")]+".pdf" )
        except PybtexError as p:
            logging.error('{}: {}\n'.format(bibfile, p))
        bar.next()
    bar.finish()
    ende = time.time()
    print('{:5.3f}s'.format(ende-start))


def parse(entry, file = None):
    doca = coll.createDocument()
    doc = Bibdoc(meta = {'id': entry.key})
    doca._key = entry.key
    doc.entrytype = entry.type
    doca['entrytype'] = entry.type
    for field in entry.fields.items():
        fieldname = field[0].lower()
        if fieldname in allowed:
            # Non-standard field in personal library
            if field[0] == 'cited-by':
                doc.cited_by = field[1]
                doca['cited_by'] = field[1]
            else:
                if field[0] == 'abstract':
                    keyphrases, words, meta = auto_tag(field[1])
                    doc.auto_tags = keyphrases
                    doca['auto_tags'] = keyphrases
                    doca['words'] = words
                    doca['meta'] = meta
                doc[fieldname] = field[1]
                doca[fieldname] = field[1]
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
        doca[item[0]] = persons
    doca['pdf'] = pdf(file)
    doc.save()
    doca.save()


def pdf(file):
    if file is None:
        return None
    try:
        with open(file, 'rb') as f:
            data = base64.b64encode(f.read()) # umwandeln der pdf zu base64
            data = data.decode()
            if data == "":
                data = None
    except FileNotFoundError as c:
        logging.warning('Keine entsprechende Pdf vorhanden {}\n'.format(file))
    return data


def auto_tag(input):
    '''
    Extract keyphrases from text via pke (Python Keyphrase Extraction toolkit)
    '''
    extractor = pke.unsupervised.MultipartiteRank()
    extractor.load_document(input=input, encoding="utf-8")
    sentences = extractor.sentences
    words = [sentence.words for sentence in sentences]
    meta = [sentence.meta for sentence in sentences]
    pos = {'NOUN', 'PROPN', 'ADJ'}
    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    extractor.candidate_selection(pos=pos, stoplist=stoplist)
    extractor.candidate_weighting(alpha=1.1,
                              threshold=0.74,
                              method='average')
    keyphrases = extractor.get_n_best(n=10)
    return [key[0] for key in keyphrases], words, meta

#nich mit comitten, nur zum testen
if __name__ == '__main__':
    path = ""#"../../Elasticsearch/NAACL2019/"
    bib(path)