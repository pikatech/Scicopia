#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import glob
from io import BufferedReader, TextIOWrapper
import logging
import argparse
import base64
import os
import re
from contextlib import contextmanager
from collections import defaultdict, deque
from typing import Dict
from progress.bar import Bar

import bz2
import gzip
import zstandard as zstd

from parser.bibtex import parse as bib
from parser.pubmed import parse as pubmed
from parser.arxiv import parse as arxiv
from parser.grobid import parse as grobid

from pyArango.collection import Collection
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError, UpdateError
from config import read_config

# See: https://www.arangodb.com/docs/stable/data-modeling-naming-conventions-document-keys.html
not_valid = re.compile("[^-_:.@()+,=;$!*'%A-Za-z0-9]")


def create_id(doc: Dict, doc_format: str) -> None:
    if doc_format == "pubmed":
        doc["id"] = f'PMID{doc["PMID"]}'


#   elif doc_format == 'arxiv':
#       pass
#   elif format == 'bibtex':
#       pass


@contextmanager
def zstd_open(
    filename: str, mode: str = "rb", encoding: str = "utf-8"
) -> BufferedReader:
    """
    This is an auxilliary function to provide an open() function which supports
    readline(), as ZstdDecompressor and the object produced by
    ZstdDecompressor.stream_reader() don't have one.'

    Parameters
    ----------
    filename : str
        DESCRIPTION.
    mode : str, optional
        This parameter only exists to keep compatibility with other open()
        functions and will be ignored. Interally, the mode is always 'rb'.
        The default is 'rb'.
    encoding : str, optional
        The name of the encoding used in the file. The default is 'utf-8'.

    Yields
    ------
    BufferedReader
        DESCRIPTION.

    """
    dctx = zstd.ZstdDecompressor()
    with open(filename, mode="rb") as fh:
        with dctx.stream_reader(fh) as reader:
            yield TextIOWrapper(BufferedReader(reader, 32768), encoding=encoding)


def setup() -> Collection:
    config = read_config()
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
        db = arangoconn.createDatabase(name=config["database"])
    if db.hasCollection(config["collection"]):
        collection = db[config["collection"]]
    else:
        collection = db.createCollection(name=config["collection"])
    return collection


def pdfsave(file: str) -> bytes:
    file = f'{file[:file.rindex(".")]}.pdf'  # muss ich noch verbessern
    try:
        with open(file, "rb") as f:
            data = base64.b64encode(f.read())
            data = data.decode()
    except FileNotFoundError:
        data = b""
    return data


def main(
    doc_format: str,
    path: str = "",
    pdf: bool = False,
    recursive: bool = False,
    compression: str = "none",
    update: bool = False,
    batch_size: int = 1000,
):
    collection = setup()
    path = path if path.endswith(os.path.sep) else path + os.path.sep
    typedict = defaultdict(lambda: ".xml")
    typedict["bib"] = ".bib"
    zipdict = defaultdict(lambda: "")
    zipdict.update({"gzip": ".gz", "bzip2": ".bz2", "zstd": ".zstd", "zip": ".zip"})
    fundict = {"bib": bib, "pubmed": pubmed, "arxiv": arxiv, "grobid": grobid}
    opendict = defaultdict(lambda: open)
    opendict.update({"gzip": gzip.open, "bzip": bz2.open, "zstd": zstd_open})
    f = f"**{os.path.sep}" if recursive else ""
    files = glob.glob(
        f"{path}{f}*{typedict[doc_format]}{zipdict[compression]}", recursive=recursive
    )
    logging.info(
        f"{len(files)} {typedict[doc_format]}{zipdict[compression]}-files found"
    )
    bar = Bar("files", max=len(files))
    for file in files:
        first = True
        with opendict[compression](file, "rt", encoding="utf-8") as data:
            docs = deque(maxlen=batch_size)
            for entry in fundict[doc_format](data):
                create_id(entry, doc_format)
                if update:
                    try:
                        doc = collection[entry["id"]]
                    except DocumentNotFoundError:
                        doc = collection.createDocument()
                        doc._key = entry["id"]
                else:
                    doc = collection.createDocument()
                    doc_id = entry["id"]
                    # Make sure document keys are valid
                    doc._key = re.sub(not_valid, "_", doc_id)
                for field in entry:
                    if field == "id":
                        continue
                    doc[field] = entry[field]
                if pdf:
                    data = pdfsave(file)
                    if data:
                        doc["pdf"] = data
                    else:
                        if first:
                            logging.warning(f"No PDF found for {file}\n")
                            first = False
                docs.append(doc)
                if len(docs) == docs.maxlen:
                    try:
                        collection.bulkSave(docs, details=True)
                    except UpdateError as e:
                        logging.error(e.message)
                        logging.error(e.errors)
                    finally:
                        docs.clear()
            if len(docs) != 0:
                try:
                    collection.bulkSave(docs, details=True)
                except UpdateError as e:
                    logging.error(e.message)
                    logging.error(e.errors)
                finally:
                    docs.clear()
        bar.next()
    bar.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saves the Data in an Arangodatabase")
    parser.add_argument(
        "type", choices=["bib", "pubmed", "arxiv", "grobid"], help="Type of the Data"
    )
    parser.add_argument("--path", help="Path to the directory", default="")
    parser.add_argument(
        "--pdf", help="Search and Save PDFs of the bib Data", action="store_true"
    )
    parser.add_argument(
        "-r", "--recursive", help="Searching of Subdirectory", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--compression",
        choices=["zip", "gzip", "zstd", "bzip2"],
        help="Archive?",
        default="none",
    )
    parser.add_argument(
        "--batch", type=int, help="Batch size of bulk import", default=1000,
    )
    parser.add_argument("--update", help="update arango if true", action="store_true")

    args = parser.parse_args()
    main(
        args.type,
        args.path,
        args.pdf,
        args.recursive,
        args.compression,
        args.update,
        args.batch,
    )
