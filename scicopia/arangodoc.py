#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import glob
from io import TextIOWrapper
import logging
import argparse
import base64
import os
import re
from contextlib import contextmanager
from collections import deque
from typing import Dict, Generator
from exceptions import NotImplementedError
from progress.bar import Bar

import bz2
import gzip
import zstandard as zstd

import multiprocessing
import dask
from dask.distributed import Client, LocalCluster

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
) -> Generator[TextIOWrapper, None, None]:
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
    TextIOWrapper
        DESCRIPTION.

    """
    dctx = zstd.ZstdDecompressor()
    with open(filename, mode="rb") as fh:
        with dctx.stream_reader(fh) as reader:
            yield TextIOWrapper(reader, encoding=encoding)


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


def pdfsave(file: str) -> str:
    file = f'{file[:file.rindex(".")]}.pdf'  # muss ich noch verbessern
    try:
        with open(file, "rb") as f:
            data = base64.b64encode(f.read())
            data = data.decode()
    except FileNotFoundError:
        data = ""
    return data


def import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf):
    first = True
    with open_func(file, "rt", encoding="utf-8") as data:
        docs = deque(maxlen=batch_size)
        for entry in parse(data):
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
                        logging.warning("No PDF found for %s", file)
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

    parse_dict = {"bibtex": bib, "pubmed": pubmed, "arxiv": arxiv, "grobid": grobid}
    ext_dict = {"bibtex": ".bib", "pubmed": ".xml", "arxiv": ".xml", "grobid": ".xml"}
    zip_dict = {"none": "", "gzip": ".gz", "bzip2": ".bz2", "zstd": ".zstd"}
    open_dict = {"none": open, "gzip": gzip.open, "bzip": bz2.open, "zstd": zstd_open}

    f = f"**{os.path.sep}" if recursive else ""
    files = glob.glob(
        f"{path}{f}*{ext_dict[doc_format]}{zip_dict[compression]}", recursive=recursive
    )
    logging.info(
        "%d %s%s-files found", len(files), ext_dict[doc_format], zip_dict[compression]
    )
    
    open_func = open_dict[compression]
    parse = parse_dict[doc_format]
    progress = Bar("files", max=len(files))
    for file in files:
        import_file(file, collection, batch_size, doc_format, open_func, parse, update, pdf)
        progress.next()
    progress.finish()


def parallel_main(
    parallel: int,
    cluster: str,
    doc_format: str,
    path: str = "",
    pdf: bool = False,
    recursive: bool = False,
    compression: str = "none",
    update: bool = False,
    batch_size: int = 1000,
):
    if parallel is None:
        print(cluster)
        raise NotImplementedError
    if cluster is None:
        if parallel <= 0:
            print("The number of processes has to be greater than zero!")
            return
        if parallel > multiprocessing.cpu_count():
            logging.warning(
                f"Number of requested CPUs surpasses CPUs on machine: %d > %d.\nWill use all available CPUs.",
                parallel,
                multiprocessing.cpu_count(),
            )
            parallel = multiprocessing.cpu_count()
        cluster = LocalCluster(n_workers=parallel)
        client = Client(cluster)
        print(parallel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saves the Data in an Arangodatabase")
    parser.add_argument(
        "type", choices=["bibtex", "pubmed", "arxiv", "grobid"], help="Type of the Data"
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
        help="Type of archive, if files are compressed",
        default="none",
    )
    parser.add_argument(
        "--batch", type=int, help="Batch size of bulk import", default=1000
    )
    parser.add_argument("--update", help="update arango if true", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-p",
        "--parallel",
        metavar="N",
        type=int,
        help="Distribute the computation on multiple cores",
    )
    group.add_argument(
        "--cluster", type=str, help="Distribute the computation onto a cluster"
    )

    args = parser.parse_args()
    if args.parallel is None and args.cluster is None:
        main(
            args.type,
            args.path,
            args.pdf,
            args.recursive,
            args.compression,
            args.update,
            args.batch,
        )
    else:
        parallel_main(
            args.parallel,
            args.cluster,
            args.type,
            args.path,
            args.pdf,
            args.recursive,
            args.compression,
            args.update,
            args.batch,
        )
