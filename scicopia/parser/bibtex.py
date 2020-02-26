#!/usr/bin/python
# Encoding: utf-8

import logging
from typing import Dict

from pybtex.database.input.bibtex import Parser
from pybtex.exceptions import PybtexError

allowed = {
    "author",
    "editor",
    "publisher",
    "institution",
    "title",
    "booktitle",
    "abstract",
    "keywords",
    "year",
    "pages",
    "journal",
    "volume",
    "number",
    "doi",
    "cited-by",
    "citing",
}


def parse(source) -> Dict[str, str]:
    try:
        parser = Parser()
        bib_data = parser.parse_stream(source)
        for entry in bib_data.entries.itervalues():
            datadict = dict()
            datadict["id"] = entry.key
            datadict["entrytype"] = entry.type
            for field in entry.fields.items():
                fieldname = field[0].lower()
                if fieldname in allowed:
                    # Non-standard field in personal library
                    if field[0] == "cited-by":
                        datadict["cited_by"] = field[1]
                    else:
                        datadict[fieldname] = field[1]
            for item in entry.persons.items():
                persons = []
                for person in item[1]:
                    names = []
                    names.extend(person.first_names)
                    names.extend(person.middle_names)
                    names.extend(person.prelast_names)
                    names.extend(person.lineage_names)
                    names.extend(person.last_names)
                    persons.append(" ".join(names))
                datadict[item[0]] = persons
            yield datadict
    except PybtexError as p:
        logging.error(f"{p}\n")
