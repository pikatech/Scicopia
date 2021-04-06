#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 16:18:45 2019

@author: tech
"""

import argparse
import base64
import bz2
import glob
import gzip
import logging
import math
import multiprocessing
import os
import re
from collections import deque
from contextlib import contextmanager
from datetime import datetime
from io import TextIOWrapper
from typing import Callable, Dict, Generator, List, Tuple

import dask
import zstandard as zstd
from dask.distributed import Client, LocalCluster
from pyArango.collection import Collection
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError, UpdateError
from tqdm import tqdm

from scicopia.config import read_config
from scicopia.exceptions import ConfigError, DBError
from scicopia.parsers.arxiv import parse as arxiv
from scicopia.parsers.bibtex import parse as bib
from scicopia.parsers.grobid import parse as grobid
from scicopia.parsers.pubmed import parse as pubmed
from scicopia.utils.zstandard import zstd_open

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



PARSE_DICT = {"bibtex": bib, "pubmed": pubmed, "arxiv": arxiv, "grobid": grobid}
EXT_DICT = {"bibtex": ".bib", "pubmed": ".xml", "arxiv": ".xml", "grobid": ".xml"}
ZIP_DICT = {"none": "", "gzip": ".gz", "bzip2": ".bz2", "zstd": ".zst"}
OPEN_DICT = {"none": open, "gzip": gzip.open, "bzip2": bz2.open, "zstd": zstd_open}


def setup() -> Tuple[Collection, Collection]:
    """
    Connect to the Arango database.

    Returns
    -------
    Collection, Collection
        1. The ArangoDB collection that holds the scientific documents
        2. The ArangoDB collection that holds the PDFs (if added) with keys corresponding to the scientific documents

    Raises
    ------
    ConfigError
        If a needed entry is missing in the config file.
    DBError
        If the connection to the ArangoDB server failed.
    """
    config = read_config()
    if not "username" in config:
        raise ConfigError("Setting missing in config file: 'username'.")
    if not "password" in config:
        raise ConfigError("Setting missing in config file: 'password'.")
    try:
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
    except:
        raise DBError(f"Connection to the ArangoDB server failed.")

    if not "database" in config:
        raise ConfigError("Setting missing in config file: 'database'.")
    if arangoconn.hasDatabase(config["database"]):
        db = arangoconn[config["database"]]
    else:
        db = arangoconn.createDatabase(name=config["database"])

    if not "documentcollection" in config:
        raise ConfigError("Setting missing in config file: 'documentcollection'.")
    if db.hasCollection(config["documentcollection"]):
        doccollection = db[config["documentcollection"]]
    else:
        doccollection = db.createCollection(name=config["documentcollection"])
        doccollection.ensurePersistentIndex(["modified_at"], unique=False, sparse=False, deduplicate=False, name="Modified")

    if not "pdfcollection" in config:
        raise ConfigError("Setting missing in config file: 'pdfcollection'.")
    if db.hasCollection(config["pdfcollection"]):
        pdfcollection = db[config["pdfcollection"]]
    else:
        pdfcollection = db.createCollection(name=config["pdfcollection"])
    return doccollection, pdfcollection


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
    if doc_format == "pdf":
        logging.info(e.message)
        for error in e.errors["details"]:
            if 'unique constraint violated' in error:
                # gets number of doc in docs
                # 12 is the start of the position in all error messages
                pos = error[12:error.index(":")]
                doc = docs[int(pos)]
                logging.warning(f"Key '{doc._key}' already exists for PDF. Update of PDFs is not supportet yet.\n")
    elif doc_format == "pubmed":
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
                logging.warning(f"Key '{doc._key}' already exists. To update the Data use --update.\n")

def parallel_import(
    batch: str,
    batch_size: int,
    doc_format: str,
    open_func: Callable,
    parse: Callable,
    update: bool,
    pdf: bool,
):
    collection, pdfcollection = setup()
    for file in batch:
        import_file(
            file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
        )


def import_file(
    file: str,
    collection: Collection,
    pdfcollection: Collection,
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
        pdfdocs = deque(maxlen=batch_size)
        for entry in parse(data):
            create_id(entry, doc_format)
            doc_id = re.sub(NOT_VALID, "_", entry["id"])
            # Make sure document keys are valid
            if update:
                try:
                    doc = collection[doc_id]
                    doc.delete()
                    # delete associated pdf?
                    # pdfdoc = pdfcollection[doc_id]
                    # pdfdoc.delete()
                except DocumentNotFoundError:
                    pass
            doc = collection.createDocument()
            doc._key = doc_id
            doc["modified_at"] = round(datetime.now().timestamp())
            for field in entry:
                if field == "id":
                    continue
                doc[field] = entry[field]
            docs.append(doc)
            if pdf:
                data = pdfsave(file)
                if data:
                    pdfdoc = pdfcollection.createDocument()
                    pdfdoc._key = doc_id # same id as associated document
                    pdfdoc["pdf"] = data
                    pdfdocs.append(pdfdoc)
                else:
                    if first:
                        logging.warning(f"No PDF found for '{file}'.")
                        first = False
            if len(docs) == docs.maxlen:
                try:
                    collection.bulkSave(docs, details=True)
                except UpdateError as e:
                    handleBulkError(e, docs, collection, doc_format)
                finally:
                    docs.clear()
            if len(pdfdocs) == pdfdocs.maxlen:
                try:
                    pdfcollection.bulkSave(pdfdocs, details=True)
                except UpdateError as e:
                    handleBulkError(e, pdfdocs, pdfcollection, "pdf")
                finally:
                    pdfdocs.clear()
        if len(docs) != 0:
            try:
                collection.bulkSave(docs, details=True)
            except UpdateError as e:
                handleBulkError(e, docs, collection, doc_format)
            finally:
                docs.clear()
        if len(pdfdocs) != 0:
            try:
                pdfcollection.bulkSave(pdfdocs, details=True)
            except UpdateError as e:
                handleBulkError(e, pdfdocs, pdfcollection, "pdf")
            finally:
                pdfdocs.clear()


def locate_files(
    path: str, doc_format: str, recursive: bool, compression: str
) -> List[str]:
    path = path if path.endswith(os.path.sep) else path + os.path.sep

    f = f"**{os.path.sep}" if recursive else ""
    files = glob.glob(
        f"{path}{f}*{EXT_DICT[doc_format]}{ZIP_DICT[compression]}", recursive=recursive
    )
    logging.info(
        f"{len(files)} {EXT_DICT[doc_format]}{ZIP_DICT[compression]}-files found" 
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
    collection, pdfcollection = setup()
    files = locate_files(path, doc_format, recursive, compression)
    if not files:
        logging.error(f"No files could be found in '{path}'.")
        return
    open_func = OPEN_DICT[compression]
    parse = PARSE_DICT[doc_format]
    for file in tqdm(files):
        import_file(
            file, collection, pdfcollection, batch_size, doc_format, open_func, parse, update, pdf
        )


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
            logging.error(f"No files could be found in '{path}'.")
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
