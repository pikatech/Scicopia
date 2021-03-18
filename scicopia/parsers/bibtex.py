#!/usr/bin/python
# Encoding: utf-8

import logging
from io import TextIOWrapper
from typing import Any, Dict, Generator, List, Tuple, Union

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
    itemname = item[0].lower()
    persons = []
    for person in item[1]:
        names = []
        names.extend(person.first_names)
        names.extend(person.middle_names)
        names.extend(person.prelast_names)
        names.extend(person.lineage_names)
        names.extend(person.last_names)
        persons.append(" ".join(names))
    datadict[itemname] = persons

def parse(
    source: TextIOWrapper,
) -> Generator[Dict[str, Union[str, List[str]]], Any, None]:
    try:
        parser = Parser()
        bib_data = parser.parse_stream(source)
        for entry in bib_data.entries.values():
            datadict = dict()
            datadict["id"] = entry.key
            datadict["entrytype"] = entry.type
            for field in entry.fields.items():
                handleField(field, datadict)
            for item in entry.persons.items():
                handlePerson(item, datadict)
            yield datadict
    except PybtexError as p:
        logging.error(f"In File {source.name} the Error '{p}' occurred. None of the entries have been saved.\n")
