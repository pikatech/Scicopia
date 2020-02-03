
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import glob
import logging
import os
import argparse
import base64
from collections import defaultdict
from progress.bar import Bar

# import zstandard as zstd
import zipfile
import gzip
import bz2

from bib_parse import bib
from pubmed import parse as pubmed
from arxivparser import parse as arxiv
# from parser.grobid_parse import grobid

import pke
import string
from nltk.corpus import stopwords

from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError, CreationError
from config import read_config
    
config = read_config()
arangoconn = Connection(username = config.username, password = config.password)
if arangoconn.hasDatabase(config.database):
    db = arangoconn[config.database]
else:
    db = arangoconn.createDatabase(name = config.database) 
if db.hasCollection(config.collection):
    coll = db[config.collection]
else:
    coll = db.createCollection(name = config.collection)


# def dezip(file, zip):
    # ! zstd und zip als spezialfall erstmal zurück stellen
    # elif zip == 'zstd':
    #     with open(file, 'rb') as f:
    #         dctx = zstd.ZstdDecompressor()
    #         return dctx.stream_reader(f)
    # elif zip == 'zip':
    #     files = glob.glob(f'{path}**.zip', recursive = recursive)
    #     for file in files:
    #         with zipfile.ZipFile(files, 'r') as zip_ref:
    #             zip_ref.extractall('extract')
    #     # schreibt alle dateien in den neuen extract ordner
    #     # alternativ f'{path}/extract', jenachdem ob es im programmordner oder dataordner sein soll
    #     loggin.info('Files are extracted to extract in current direction')

def pdfsave(file):
    file = f'{file[:file.rindex(".")]}.pdf' # muss ich noch verbessern
    try:
        with open(file, 'rb') as f:
            data = base64.b64encode(f.read())
            data = data.decode()
    except FileNotFoundError:
        data = ''
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

def main(typ, path = '', pdf = False, recursive = False, zip = None, update = False):
    path = path if path.endswith(os.path.sep) else path + os.path.sep
    typedict = defaultdict(lambda:'.xml')
    typedict['bib'] = '.bib'
    zipdict = defaultdict(lambda:'')
    zipdict.update({'gzip':'.gz', 'bzip2':'.bz2','zstd':'.zstd','zip':'.zip'})
    fundict = {'bib':bib, 'pubmed':pubmed, 'arxiv':arxiv}#, 'grobid':grobid}
    opendict = defaultdict(lambda:open)
    opendict.update({'gzip':gzip.open,'bzip':bz2.open})
    f = f'**{os.path.sep}' if recursive else ''
    files = glob.glob(f'{path}{f}*{typedict[typ]}{zipdict[zip]}', recursive = recursive)
    logging.info(f'{len(files)} {typedict[typ]}{zipdict[zip]}-files found')
    bar = Bar('files', max=len(files))
    for file in files:
        first = True
        with opendict[zip](file, 'r', encoding='utf-8') as data:
            for entry in fundict[typ](data):
                if update:
                    try:
                        doc = coll[entry['id']]
                    except DocumentNotFoundError:
                        doc = coll.createDocument()
                        doc._key = entry['id']
                else:
                    doc = coll.createDocument()
                    doc._key = entry['id']
                for field in entry:
                    if field == 'id':
                        continue
                    elif field == 'abstract':
                        keyphrases, words, meta = auto_tag(entry[field])
                        doc[field] = entry[field]
                        doc['auto_tags'] = keyphrases
                        doc['words'] = words
                        doc['meta'] = meta
                    else:
                        doc[field] = entry[field]
                if pdf:
                    data = pdfsave(file)
                    if data:
                        doc['pdf'] = data
                    else:
                        if first:
                            logging.warning(f'No PDF found for {file}\n')
                            first = False
                try:
                    doc.save()
                except CreationError:
                    logging.warning(f'Key {entry["id"]} already exists. To update the Data use --update\n')
        bar.next()
    bar.finish()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Saves the Data in an Arangodatabase')
    parser.add_argument('type', choices=['bib', 'pubmed', 'arxiv', 'grobid'], help='Type of the Data')
    parser.add_argument('--path', help='Path to the directory', default='')
    parser.add_argument('--pdf', help='Search and Save PDFs of the bib Data', action='store_true')
    parser.add_argument('--recursive', help='Searching of Subdirectory', action='store_true')
    parser.add_argument('--zip', choices=['zip', 'gzip', 'zstd', 'bzip2'], help='Archive?', default=None)
    parser.add_argument('--update', help='update arango if true', action='store_true')

    args = parser.parse_args()
    main(args.type, args.path, args.pdf, args.recursive, args.zip, args.update)
