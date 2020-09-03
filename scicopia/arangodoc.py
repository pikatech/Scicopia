#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import glob
from io import TextIOWrapper
import logging
import math
import argparse
import base64
import os
import re
from contextlib import contextmanager
from collections import deque
from typing import Callable, Dict, Generator, List
from progress.bar import Bar
from datetime import datetime

import bz2
import gzip
import zstandard as zstd

import multiprocessing
import dask
from dask.distributed import Client, LocalCluster

from scicopia.parsers.bibtex import parse as bib
from scicopia.parsers.pubmed import parse as pubmed
from scicopia.parsers.arxiv import parse as arxiv
from scicopia.parsers.grobid import parse as grobid

from pyArango.collection import Collection
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError, UpdateError
from scicopia.config import read_config
logging.getLogger().setLevel(logging.INFO)

# See: https://www.arangodb.com/docs/stable/data-modeling-naming-conventions-document-keys.html
NOT_VALID = re.compile("[^-_:.@()+,=;$!*'%A-Za-z0-9]")


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


PARSE_DICT = {"bibtex": bib, "pubmed": pubmed, "arxiv": arxiv, "grobid": grobid}
EXT_DICT = {"bibtex": ".bib", "pubmed": ".xml", "arxiv": ".xml", "grobid": ".xml"}
ZIP_DICT = {"none": "", "gzip": ".gz", "bzip2": ".bz2", "zstd": ".zstd"}
OPEN_DICT = {"none": open, "gzip": gzip.open, "bzip2": bz2.open, "zstd": zstd_open}


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
        collection.ensurePersistentIndex(["modified_at"], unique=False, sparse=False, deduplicate=False, name="Modified")
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

def handleBulkError(e, docs, collection, doc_format):
    if doc_format == "pubmed":
        logging.info(e.message)
        errors = e.errors
        errordocs=[]
        # list of docs with same key as a saved document
        for error in errors["details"]:
            if 'unique constraint violated' in error:
                # gets number of doc in docs
                # 12 is the start of the position in all error messages
                pos = error[12:error.index(":")]
                errordocs.append(docs[int(pos)])
        # remove double in same batch
        # searching for better solution
        i = 0
        while i < len(errordocs)-1:
            j = i + 1
            while j < len(errordocs):
                if errordocs[i]["PMID"] == errordocs[j]["PMID"]:
                    if errordocs[i]["Version"] >= errordocs[j]["Version"]:
                        errordocs.remove(errordocs[j])
                        j -= 1
                    else:
                        errordocs.remove(errordocs[i])
                        j -= 1
                        i -= 1
                        break
                j += 1
            i += 1
        # save newest version
        for doc in errordocs:
            # load saved document
            arangodoc = collection[doc._key]
            if doc["Version"] > arangodoc["Version"]:
                arangodoc.delete()
                doc.save()
    else:
        logging.error(e.message)
        for error in e.errors["details"]:
            if 'unique constraint violated' in error:
                # gets number of doc in docs
                # 12 is the start of the position in all error messages
                pos = error[12:error.index(":")]
                doc = docs[int(pos)]
                logging.warning(f'Key {doc._key} already exists. To update the Data use --update\n')

def parallel_import(
    batch: str,
    batch_size: int,
    doc_format: str,
    open_func: Callable,
    parse: Callable,
    update: bool,
    pdf: bool,
):
    collection = setup()
    for file in batch:
        import_file(
            file, collection, batch_size, doc_format, open_func, parse, update, pdf
        )


def import_file(
    file: str,
    collection: Collection,
    batch_size: int,
    doc_format: str,
    open_func: Callable,
    parse: Callable,
    update: bool,
    pdf: bool,
):
    first = True
    with open_func(file, "rt", encoding="utf-8") as data:
        docs = deque(maxlen=batch_size)
        for entry in parse(data):
            create_id(entry, doc_format)
            doc_id = re.sub(NOT_VALID, "_", entry["id"])
            # Make sure document keys are valid
            if update:
                try:
                    doc = collection[doc_id]
                    doc.delete()
                except DocumentNotFoundError:
                    pass
            doc = collection.createDocument()
            doc._key = doc_id
            doc["modified_at"] = round(datetime.now().timestamp())
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
                        logging.warning(f"No PDF found for {file}")
                        first = False
            docs.append(doc)
            if len(docs) == docs.maxlen:
                try:
                    collection.bulkSave(docs, details=True)
                except UpdateError as e:
                    handleBulkError(e, docs, collection, doc_format)
                finally:
                    docs.clear()
        if len(docs) != 0:
            try:
                collection.bulkSave(docs, details=True)
            except UpdateError as e:
                handleBulkError(e, docs, collection, doc_format)
            finally:
                docs.clear()


def locate_files(
    path: str, doc_format: str, recursive: bool, compression: str
) -> List[str]:
    path = path if path.endswith(os.path.sep) else path + os.path.sep

    f = f"**{os.path.sep}" if recursive else ""
    files = glob.glob(
        f"{path}{f}*{EXT_DICT[doc_format]}{ZIP_DICT[compression]}", recursive=recursive
    )
    logging.info(
        "%d %s%s-files found", len(files), EXT_DICT[doc_format], ZIP_DICT[compression]
    )
    return files


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
    files = locate_files(path, doc_format, recursive, compression)
    if not files:
        logging.error(f"No files could be found in {path}")
        return
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    progress = Bar("files", max=len(files))
    for file in files:
        import_file(
            file, collection, batch_size, doc_format, open_func, parse, update, pdf
        )
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
                "Number of requested CPUs surpasses CPUs on machine: %d > %d.\nWill use all available CPUs.",
                parallel,
                multiprocessing.cpu_count(),
            )
            parallel = multiprocessing.cpu_count()
        cluster = LocalCluster(n_workers=parallel)
        client = Client(cluster)

        # Just make sure the database gets prepared, no need for return value
        setup()

        files = locate_files(path, doc_format, recursive, compression)
        if not files:
            logging.error(f"No files could be found in {path}")
            return
        open_func = OPEN_DICT[compression]
        parse = PARSE_DICT[doc_format]

        tasks = []
        # Split files into batches
        factor = math.ceil(len(files) / parallel)
        for batch in [files[i : i + factor] for i in range(0, len(files), factor)]:
            tasks.append(
                dask.delayed(parallel_import)(
                    batch, batch_size, doc_format, open_func, parse, update, pdf
                )
            )
        dask.compute(*tasks)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Saves the Data in an Arangodatabase")
    PARSER.add_argument(
        "type", choices=["bibtex", "pubmed", "arxiv", "grobid"], help="Type of the Data"
    )
    PARSER.add_argument("--path", help="Path to the directory", default="")
    PARSER.add_argument(
        "--pdf", help="Search and Save PDFs of the bib Data", action="store_true"
    )
    PARSER.add_argument(
        "-r", "--recursive", help="Searching of Subdirectory", action="store_true"
    )
    PARSER.add_argument(
        "-c",
        "--compression",
        choices=["zip", "gzip", "zstd", "bzip2"],
        help="Type of archive, if files are compressed",
        default="none",
    )
    PARSER.add_argument(
        "--batch", type=int, help="Batch size of bulk import", default=1000
    )
    PARSER.add_argument("--update", help="update arango if true", action="store_true")
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument(
        "-p",
        "--parallel",
        metavar="N",
        type=int,
        help="Distribute the computation on multiple cores",
    )
    GROUP.add_argument(
        "--cluster", type=str, help="Distribute the computation onto a cluster"
    )

    ARGS = PARSER.parse_args()
    if ARGS.parallel is None and ARGS.cluster is None:
        main(
            ARGS.type,
            ARGS.path,
            ARGS.pdf,
            ARGS.recursive,
            ARGS.compression,
            ARGS.update,
            ARGS.batch,
        )
    else:
        parallel_main(
            ARGS.parallel,
            ARGS.cluster,
            ARGS.type,
            ARGS.path,
            ARGS.pdf,
            ARGS.recursive,
            ARGS.compression,
            ARGS.update,
            ARGS.batch,
        )
