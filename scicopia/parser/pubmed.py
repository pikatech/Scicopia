#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to parse PubMed files.
Main function is parse(source).
"""

# Article (Journal,ArticleTitle,((Pagination, ELocationID*) | ELocationID+),
#                  Abstract?,AuthorList?, Language+, DataBankList?, GrantList?,
#                  PublicationTypeList, VernacularTitle?, ArticleDate*) >

from io import TextIOWrapper
import logging
from typing import Any, Dict, Generator, List, Union
from xml.etree.ElementTree import iterparse, Element


def extract_abstract(abstract: Element) -> str:
    parts = abstract.findall("AbstractText")
    text = []
    for part in parts:
        # Handle marked up text
        for tag in iter(part):
            if tag.text:
                tag.text = f"<{tag.tag}>{tag.text}<{tag.tag}>"
        if "Label" in part.attrib:
            text.append(f"{part.attrib['Label']}: {''.join(part.itertext())}")
        else:
            text.append("".join(part.itertext()))
    return "\n".join(text)


def extract_authors(authors: Element) -> List[str]:
    """
    Extract the list of authors from an AuthorList node.

    Parameters
    ----------
    authors : Element
        An AuthorList XML node element.

    Returns
    -------
    List[str]
        A list of authors including their fore names (or initials), last names and suffixes.

    """
    # <!ELEMENT	Author (((LastName, ForeName?, Initials?, Suffix?) |
    #                    CollectiveName),
    #                   Identifier*, AffiliationInfo*) >
    team = authors.findall("Author")
    author_list = []
    for author in team:
        if "ValidYN" in author.attrib and author.attrib["ValidYN"] == "N":
            continue
        lastname = author.find("LastName")
        forename = author.find("ForeName")
        initials = author.find("Initials")
        suffix = author.find("Suffix")
        if forename is None:
            # Check for non-existing and also empty elements
            # e.g. <Initials/>
            author_list.append(
                " ".join(
                    x.text
                    for x in [initials, lastname, suffix]
                    if not x is None and not x.text is None
                )
            )
        else:
            author_list.append(
                " ".join(
                    x.text
                    for x in [forename, lastname, suffix]
                    if not x is None and not x.text is None
                )
            )
    if "CompleteYN" in author.attrib and author.attrib["CompleteYN"] == "N":
        author_list.append("et al.")
    return author_list


def extract_mesh_headings(mesh_headings: Element, pmid: str) -> List[str]:
    # <!ELEMENT	MeshHeadingList (MeshHeading+)>
    # <!ELEMENT	MeshHeading (DescriptorName, QualifierName*)>
    headings = mesh_headings.findall("MeshHeading")
    heading_list = []
    for heading in headings:
        name = heading.find("DescriptorName")
        if name is None:
            logging.warning("Article %s is missing a descriptor name", pmid)
        else:
            name = name.text
            heading_list.append(name)
    return heading_list


def extract_journaldata(journal: Element, pmid: str) -> Dict[str, str]:
    # <!ELEMENT	Journal (ISSN?, JournalIssue, Title?, ISOAbbreviation?)>
    # <!ELEMENT	JournalIssue (Volume?, Issue?, PubDate) >
    # <!ELEMENT	PubDate ((Year, ((Month, Day?) | Season)?) | MedlineDate) >
    data = dict()
    volume = journal.find("JournalIssue/Volume")
    if volume is not None:
        data["volume"] = volume.text

    issue = journal.find("JournalIssue/Issue")
    if issue is not None:
        data["issue"] = issue.text

    pubdate = journal.find("JournalIssue/PubDate")
    if pubdate is not None:
        # Could be a non-standard date
        medline_date = pubdate.find("MedlineDate")
        if not medline_date is None:
            data["date"] = medline_date.text
        else:
            year = pubdate.find("Year")
            if year is not None:
                data["year"] = year.text

            month = pubdate.find("Month")
            if month is not None:
                data["month"] = month.text.lower()
    else:
        logging.warning("Article %s should have had a publication date entry", pmid)

    title = journal.find("Title")
    if title is not None:
        data["journal"] = title.text

    return data


def parse(
    source: TextIOWrapper,
) -> Generator[Dict[str, Union[str, List[str]]], Any, None]:
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":
            pmid = elem.find(".//PMID")
            if pmid is None:
                logging.warning("Article without PMID occurred. Skipped.")
                continue
            article["Version"]=pmid.attrib
            pmid = pmid.text
            article["PMID"] = pmid
            article["url"] = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"
            title = elem.find(".//ArticleTitle")
            if title is None:
                logging.warning("Article %s should have had a title", pmid)
                continue

            # Handle marked up text
            for tag in iter(title):
                if tag.text:
                    tag.text = f"<{tag.tag}>{tag.text}<{tag.tag}>"
            article["title"] = "".join(title.itertext())

            abstract = elem.find(".//Abstract")
            # Abstract is optional
            if abstract is not None:
                article["abstract"] = extract_abstract(abstract)

            authors = elem.find(".//AuthorList")
            # List of authors is optional
            if authors is not None:
                article["author"] = extract_authors(authors)

            journal = elem.find(".//Journal")
            # journal entry is mandatory
            if journal is not None:
                article.update(extract_journaldata(journal, pmid))
            else:
                logging.warning("Article %s should have had a journal entry", pmid)

            mesh_headings = elem.find(".//MeshHeadingList")
            # List of authors is optional
            if mesh_headings is not None:
                article["mesh"] = extract_mesh_headings(mesh_headings, pmid)

            root.clear()
            yield article
