#!/usr/bin/python
# Encoding: utf-8

import xml.etree.ElementTree as ET
import re
import logging
from typing import Dict

date_pattern = re.compile(r"(\d{4})-\d{2}-\d{2}", re.ASCII)

DC = "/{http://www.openarchives.org/OAI/2.0/oai_dc/}dc"
OAI = "{http://www.openarchives.org/OAI/2.0/}"
METADATA = f"./{OAI}metadata"

HEADER = f"./{OAI}header"
RECORD = f"{OAI}record"
SETSPEC = f"{HEADER}/{OAI}setSpec"
HEADERDATE = f"{HEADER}/{OAI}datestamp"
HEADERID = f"{HEADER}/{OAI}identifier"

CREATOR = f"{METADATA}{DC}/{{http://purl.org/dc/elements/1.1/}}creator"
SUBJECT = f"{METADATA}{DC}/{{http://purl.org/dc/elements/1.1/}}subject"
TITLE = f"{METADATA}{DC}/{{http://purl.org/dc/elements/1.1/}}title"
DESC = f"{METADATA}{DC}/{{http://purl.org/dc/elements/1.1/}}description"
METAID = f"{METADATA}{DC}/{{http://purl.org/dc/elements/1.1/}}identifier"


def parse(source) -> Dict[str, str]:
    context = ET.iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        if event == "end" and elem.tag == RECORD:
            id = elem.find(HEADERID)
            if id is not None:
                id = id.text
            else:
                logging.warning(f"Found record without ID in file {source}")
                continue
            # An optional status attribute with a value of deleted
            # indicates the withdrawal of availability of the specified
            # metadata format for the item, dependent on the repository
            # support for deletions.
            if elem.find(HEADER + "[@status='deleted']") is not None:
                logging.info(f"Record {id} has been deleted")
                continue
            doc = dict()
            doc["id"] = id
            date = elem.find(HEADERDATE)
            if date is not None:
                date = date.text
                doc["date"] = date
                match = date_pattern.match(date)
                if not match is None:
                    doc["year"] = match.group(1)
            else:
                logging.warning(f"Record {id} doesn't contain a date")
                continue
            # zero or more setSpec elements
            setSpec = set(x.text for x in elem.findall(SETSPEC))
            doc["setSpec"] = setSpec
            title = elem.find(TITLE)
            if title is not None:
                title = title.text
                doc["title"] = title
            else:
                logging.warning(f"Record {id} doesn't contain a title")
                continue
            author = tuple(x.text for x in elem.findall(CREATOR))
            if author:
                doc["author"] = author
            else:
                logging.warning(f"Record {id} doesn't contain any authors")
            subject = set(x.text for x in elem.findall(SUBJECT))
            if subject:
                doc["subject"] = subject
            else:
                logging.warning(f"Record {id} doesn't contain any subjects")
            description = "\n".join(
                x.text.replace("\n", " ") for x in elem.findall(DESC)
            )
            if description:
                doc["abstract"] = description.strip()
            else:
                logging.warning(f"Record {id} doesn't contain any description")
            meta_id = tuple(x.text for x in elem.findall(METAID))
            if meta_id:
                doc["meta_id"] = meta_id
            yield doc
