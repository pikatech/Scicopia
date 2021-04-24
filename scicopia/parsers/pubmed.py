#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to parse PubMed files.
Main function is parse(source).
"""

# Article (Journal,ArticleTitle,((Pagination, ELocationID*) | ELocationID+),
#                  Abstract?,AuthorList?, Language+, DataBankList?, GrantList?,
#                  PublicationTypeList, VernacularTitle?, ArticleDate*) >

import logging
from typing import Dict, List
from xml.etree.ElementTree import Element, iterparse

from scicopia.parsers.marccode import marccode


def handle_markup(element):
    # Handle marked up text
    for tag in iter(element):
        if tag.text:
            tag.text = "<" + tag.tag + ">" + tag.text + "<" + tag.tag + ">"


def extract_abstract(abstract: Element) -> str:
    parts = abstract.findall("AbstractText")
    text = []
    for part in parts:
        handle_markup(part)
        if "Label" in part.attrib:
            parttext = "".join(part.itertext())
            if parttext != "":
                text.append(part.attrib["Label"] + ": " + parttext)
        else:
            parttext = "".join(part.itertext())
            if parttext != "":
                text.append(parttext)
    if text:
        return "\n".join(text)
    else:
        return None


def extract_authors(authors: Element) -> List[str]:
    # <!ELEMENT	Author (((LastName, ForeName?, Initials?, Suffix?) |
    #                    CollectiveName),
    #                   Identifier*, AffiliationInfo*) >
    team = authors.findall("Author")
    authorList = []
    for author in team:
        if "ValidYN" in author.attrib and author.attrib["ValidYN"] == "N":
            continue
        lastname = author.find("LastName")
        forename = author.find("ForeName")
        initials = author.find("Initials")
        suffix = author.find("Suffix")
        if forename is None or forename.text is None:
            # Check for non-existing and also empty elements
            # e.g. <Initials/>
            names = " ".join(
                x.text
                for x in [initials, lastname, suffix]
                if not x is None and not x.text is None
            )
            if not names == "":
                authorList.append(names)
        else:
            authorList.append(
                " ".join(
                    x.text
                    for x in [forename, lastname, suffix]
                    if not x is None and not x.text is None
                )
            )
    if "CompleteYN" in authors.attrib and authors.attrib["CompleteYN"] == "N":
        authorList.append("et al.")
    return authorList


def extract_mesh_headings(mesh_headings: Element, pmid: str) -> List[str]:
    # <!ELEMENT	MeshHeadingList (MeshHeading+)>
    # <!ELEMENT	MeshHeading (DescriptorName, QualifierName*)>
    headings = mesh_headings.findall("MeshHeading")
    headingList = []
    for heading in headings:
        name = heading.find("DescriptorName")
        if name is None or name.text is None:
            logging.warning(f"Article {pmid} is missing a descriptor name")
        else:
            name = name.text
            headingList.append(name)
    return headingList


def extract_journaldata(journal: Element, pmid: str) -> Dict[str, str]:
    # <!ELEMENT	Journal (ISSN?, JournalIssue, Title?, ISOAbbreviation?)>
    # <!ELEMENT	JournalIssue (Volume?, Issue?, PubDate) >
    # <!ELEMENT	PubDate ((Year, ((Month, Day?) | Season)?) | MedlineDate) >
    data = dict()
    volume = journal.find("JournalIssue/Volume")
    if volume is not None and volume.text is not None:
        data["volume"] = volume.text

    issue = journal.find("JournalIssue/Issue")
    if issue is not None and issue.text is not None:
        data["issue"] = issue.text

    pubdate = journal.find("JournalIssue/PubDate")
    if pubdate is not None and pubdate.text is not None:
        # Could be a non-standard date
        medline_date = pubdate.find("MedlineDate")
        if not medline_date is None and medline_date.text is not None:
            data["date"] = medline_date.text
        else:
            year = pubdate.find("Year")
            if year is not None and year.text is not None:
                data["year"] = year.text

            month = pubdate.find("Month")
            if month is not None and month.text is not None:
                data["month"] = month.text.lower()
    else:
        logging.warning("Article %s should have had a publication date entry", pmid)
    title = journal.find("Title")
    if title is not None and title.text is not None:
        data["journal"] = title.text

    return data


def parse(source) -> Dict[str, str]:
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == "end" and elem.tag == "PubmedArticle":
            pmid = elem.find(".//PMID")
            if pmid is None or pmid.text is None:
                logging.warning("Article without PMID occurred. Skipped.")
                continue
            att = pmid.attrib
            pmid = pmid.text
            article["PMID"] = pmid
            if "Version" in att:
                article["Version"] = att["Version"]
            else:
                article["Version"] = "1"
            article["url"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + pmid
            title = elem.find(".//ArticleTitle")
            if title is None or title.text is None:
                title = elem.find(".//VernacularTitle")
                if title is None or title.text is None:
                    logging.warning("Article %s should have had a title", pmid)
                    continue
            else:
                handle_markup(title)
                titletext = "".join(title.itertext())
                if titletext != "":
                    article["title"] = titletext
                else:
                    title = elem.find(".//VernacularTitle")
                    if title is None or title.text is None:
                        logging.warning("Article %s should have had a title", pmid)
                        continue
                    else:
                        handle_markup(title)
                        titletext = "".join(title.itertext())
                        if titletext != "":
                            article["title"] = titletext
                        else:
                            logging.warning("Article %s should have had a title", pmid)
                            continue

            abstract = elem.find(".//Abstract")
            # Abstract is optional
            if abstract is not None and abstract.text is not None:
                abstract = extract_abstract(abstract)
                if abstract is not None:
                    article["abstract"] = abstract

            authors = elem.find(".//AuthorList")
            # List of authors is optional
            if authors is not None and authors.text is not None:
                authors = extract_authors(authors)
                if authors:
                    article["author"] = authors

            journal = elem.find(".//Journal")
            # journal entry is mandatory
            if journal is not None and journal.text is not None:
                article.update(extract_journaldata(journal, pmid))
            else:
                logging.warning("Article %s should have had a journal entry", pmid)
                continue

            mesh_headings = elem.find(".//MeshHeadingList")
            # List of mesh_headings is optional
            if mesh_headings is not None and mesh_headings.text is not None:
                mesh = extract_mesh_headings(mesh_headings, pmid)
                if mesh:
                    article["mesh"] = mesh

            yield article
            root.clear()
