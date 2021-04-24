#!/usr/bin/python
# Encoding: utf-8

import logging
from io import TextIOWrapper
from typing import Any, Dict, Generator, List, Tuple, Union

from pybtex.database.input.bibtex import Parser
from pybtex.exceptions import PybtexError
from pylatexenc.latex2text import (
    LatexNodes2Text,
    MacroTextSpec,
    get_default_latex_context_db,
)


def tex2text(bib_data: Dict):
    """
    Resolve LaTeX special macros like accents and
    other character combinations.

    Parameters
    ----------
    bib_data : Dict
        BibTeX fields. The dictionary is modified in place.
    """
    adjusted_db = get_default_latex_context_db()
    cat = [
        MacroTextSpec("textgreater", ">"),
        MacroTextSpec("textless", "<"),
        MacroTextSpec("emph", "<i>%s</i>"),
        MacroTextSpec("textbf", "<b>%s</b>"),
        MacroTextSpec("textit", "<i>%s</i>"),
    ]
    adjusted_db.add_context_category("own", cat, prepend=True)
    # If we should ever want to display equations via MathJax,
    # math_mode needs to be set to verbatim
    l2t = LatexNodes2Text(
        math_mode="text", strict_latex_spaces=True, latex_context=adjusted_db
    )
    for field in ("author", "editor"):
        if field in bib_data:
            persons = []
            for author in bib_data[field]:
                persons.append(l2t.latex_to_text(author))
            bib_data[field] = persons
    for field in ("title", "abstract"):
        if field in bib_data:
            bib_data[field] = l2t.latex_to_text(bib_data[field])


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
            data = dict()
            data["id"] = entry.key
            data["entrytype"] = entry.type
            for field in entry.fields.items():
                handleField(field, data)
            for item in entry.persons.items():
                handlePerson(item, data)
            tex2text(data)
            yield data
    except PybtexError as p:
        logging.error(
            f"In File {source.name} the Error '{p}' occurred. None of the entries have been saved.\n"
        )
