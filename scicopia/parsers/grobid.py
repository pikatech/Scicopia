#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 13:46:31 2020

@author: Tech
This module extracts the main text out of TEI-formatted XML.
It is meant to be used in conjunction with GROBID output.
"""

import glob
from io import TextIOWrapper
import logging
import re
from typing import Dict, List, Optional, Tuple, Union
import xml.etree.ElementTree as ET

TEI = "{http://www.tei-c.org/ns/1.0}"
TEIBACK = f"{TEI}back"
TEIDIV = f"{TEI}div"
TEIHEAD = f"{TEI}head"
TEIREF = f"{TEI}ref"
TEITEXT = f"{TEI}text"
FILEDESC = f"{TEI}fileDesc"

date_pattern = re.compile(r"(\d{4})-\d{2}-\d{2}", re.ASCII)


def extract_text(root: ET.Element) -> str:
    """
    
    root: ElementTree Element
    """
    text = []
    for div in root.iter(TEIDIV):
        for child in div:
            if child.tag == TEIHEAD:
                text.append(f"{child.text}\n")
            else:
                text.append(f'{"".join(child.itertext())}\n\n')
    return "".join(text).rstrip()


def remove_refs(root: ET.Element) -> None:
    """
    Removes the backmatter and references in text.
    
    root: ElementTree Element
    """
    for text in root.findall(TEITEXT):
        # remove back because there is no relevant information
        for back in text.findall(TEIBACK):
            if back is not None:
                text.remove(back)

    for p in root.findall(f".//{TEIDIV}/{TEI}p"):
        # remove ref text because it is not part of the main text
        # deleting it right away leads to missing blocks
        for ref in p.findall(TEIREF):
            ref.text = ""


def extract_title(node: ET.Element, data: Dict) -> None:
    # Works are allowed to have multiple titles according to the TEI standard,
    # but we disregard this option here
    title = node.find(f"{TEI}title")
    if not title is None and not title.text is None and title.text.rstrip():
        data["title"] = title.text
    else:
        logging.warning("No title!")


def extract_authors(authors: List[ET.Element], data: Dict) -> None:
    entries = []
    for author in authors:
        parts = []
        name = author.find(f"{TEI}persName")
        if name is not None:
            forenames = name.findall(f"{TEI}forename")
            for forename in forenames:
                if forename.text is not None:
                    parts.append(forename.text)
            surnames = name.findall(f"{TEI}surname")
            for surname in surnames:
                if surname.text is not None:
                    parts.append(surname.text)
        else:
            continue
        if parts:
            entries.append(" ".join(parts))
    if entries:
        data["author"] = entries

def extract_bibliographic_data(node: ET.Element) -> Optional[Dict]:
    """
    Find bibliographic data like title, authors and editors
    """
    data = dict()
    title = node.find(f"{TEI}titleStmt")
    if not title is None:
        extract_title(title, data)

    date = node.find(f"{TEI}publicationStmt/{TEI}date")
    if not date is None:
        if (
            "type" in date.attrib
            and date.attrib["type"] == "published"
            and "when" in date.attrib
        ):
            data["date"] = date.attrib["when"]
            match = date_pattern.match(date.attrib["when"])
            if not match is None:
                data["year"] = match.group(1)

    structured_info = node.find(f"{TEI}sourceDesc/{TEI}biblStruct")
    if not structured_info is None:
        authors = structured_info.findall(f"{TEI}analytic/{TEI}author")
        if authors:
            extract_authors(authors, data)

        idnos = structured_info.findall(f"{TEI}idno")
        for idno in idnos:
            if "type" in idno.attrib:
                if not "id" in data:
                    data[idno.attrib["type"].lower()] = idno.text
                    data["id"] = idno.text
            elif idno.text.startswith("doi:"):
                data["doi"] = idno.text[4:].replace(" ", "")
                data["id"] = data["doi"]
            elif idno.text.startswith("abs/"):
                data["url"] = f'https://arxiv.org/{idno.text}'
                data["id"] = idno.text
            else:
                logging.warning(f"non standard id type {idno.text}")
                if not "id" in data:
                    data["id"] = idno.text
        if not "id" in data:
            if "author" in data:
                logging.warning(f"no IDNO {data['author']}")
                data["id"] = f"noIDNO: {data['author']}"
            else:
                logging.warning("no IDNO")
                data["id"] = "noIDNO"
    else:
        logging.warning("no Info")
        data["id"] = "noInfo"
    return data


def parse(filename: TextIOWrapper) -> Dict[str, Union[str, List[str]]]:
    """
    Extracts bibliographic information and full text from TEI-formatted
    GROBID output.

    Parameters
    ----------
    filename : TextIOWrapper
        DESCRIPTION.

    Returns
    -------
    Dict
        DESCRIPTION.

    """
    xml = filename.read()
    xml = xml.replace(" <ref", "<ref")
    root = ET.fromstring(xml)
    del xml

    remove_refs(root)
    biblio = root.find(f"{TEI}teiHeader/{FILEDESC}")
    if biblio is not None and biblio.text is not None:
        bib = extract_bibliographic_data(biblio)

        text = extract_text(root)
        if text:
            bib["fulltext"] = text

        yield bib
