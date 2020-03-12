#!/usr/bin/python
# Encoding: utf-8

from io import TextIOWrapper
import logging
from typing import Any, Dict, Generator, List, Union, Tuple

from pybtex.database.input.bibtex import Parser
from pybtex.exceptions import PybtexError

def handleField(field: Tuple, datadict: Dict):
    fieldname = field[0].lower()
    # Non-standard field in personal library
    if fieldname == "cited-by":
        datadict["cited_by"] = field[1]
    else:
        datadict[fieldname] = field[1]
            
def handlePerson(item: Tuple, datadict: Dict):
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

def parse(
    source: TextIOWrapper,
) -> Generator[Dict[str, Union[str, List[str]]], Any, None]:
    try:
        parser = Parser()
        bib_data = parser.parse_stream(source)
        for entry in bib_data.entries.itervalues():
            datadict = dict()
            datadict["id"] = entry.key
            datadict["entrytype"] = entry.type
            for field in entry.fields.items():
                handleField(field, datadict)
            for item in entry.persons.items():
                handlePerson(item, datadict)
            yield datadict
    except PybtexError as p:
        logging.error(f"{p}\n")
