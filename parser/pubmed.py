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
from xml.etree.ElementTree import iterparse, Element


def extract_abstract(abstract: Element) -> str:
    parts = abstract.findall('AbstractText')
    text = []
    for part in parts:
        # Handle marked up text
        for tag in iter(part):
            if tag.text:
                tag.text = '<' + tag.tag + '>' + tag.text + '<' + tag.tag + '>'
        if 'Label' in part.attrib:
            text.append(part.attrib['Label'] + ': ' + "".join(part.itertext()))
        else:
            text.append("".join(part.itertext()))
    return '\n'.join(text)


def extract_authors(authors: Element) -> List[str]:
    # <!ELEMENT	Author (((LastName, ForeName?, Initials?, Suffix?) |
    #                    CollectiveName),
    #                   Identifier*, AffiliationInfo*) >
    team = authors.findall('Author')
    authorList = []
    for author in team:
        if 'ValidYN' in author.attrib and author.attrib['ValidYN'] == 'N':
            continue
        lastname = author.find('LastName')
        forename = author.find('ForeName')
        initials = author.find('Initials')
        suffix = author.find('Suffix')
        if forename is None:
            authorList.append(' '.join(x.text for x in [initials, lastname, suffix] if not x is None))
        else:
            authorList.append(' '.join(x.text for x in [forename, lastname, suffix] if not x is None))
    if 'CompleteYN' in author.attrib and author.attrib['CompleteYN'] == 'N':
        authorList.append('et al.')
    return authorList


def extract_journaldata(journal: Element, pmid: str) -> Dict[str, str]:
    # <!ELEMENT	Journal (ISSN?, JournalIssue, Title?, ISOAbbreviation?)>
    # <!ELEMENT	JournalIssue (Volume?, Issue?, PubDate) >
    # <!ELEMENT	PubDate ((Year, ((Month, Day?) | Season)?) | MedlineDate) >
    data = dict()
    volume = journal.find('JournalIssue/Volume')
    if volume is not None:
        data['volume'] = volume.text
        
    issue = journal.find('JournalIssue/Issue')
    if issue is not None:
        data['issue'] = issue.text
        
    pubdate = journal.find('JournalIssue/PubDate')
    if pubdate is not None:
        month = pubdate.find('Month')
        if month is not None:
            data['month'] = month.text.lower()
            
        year = pubdate.find('Year')
        if year is not None:
            data['year'] = year.text
    else:
        logging.warning('Article %s should have had a publication date entry',
                                pmid)
        
    title = journal.find('Title')
    if title is not None:
        data['journal'] = title.text
        
    return data


def parse(source) -> Dict[str, str]:
    context = iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)

    for event, elem in context:
        article = dict()
        if event == 'end' and elem.tag == 'PubmedArticle':
            pmid = elem.find('.//PMID')
            if pmid is None:
                logging.warning('Article without PMID occurred. Skipped.')
                continue
            pmid = pmid.text
            article['PMID'] = pmid
            article['url'] = 'https://www.ncbi.nlm.nih.gov/pubmed/' + pmid
            title = elem.find('.//ArticleTitle')
            if title is None:
                logging.warning('Article %s should have had a title', pmid)
                continue

            # Handle marked up text
            for tag in iter(title):
                if tag.text:
                    tag.text = ('<' + tag.tag + '>' + tag.text +
                                '<' + tag.tag + '>')
            article['title'] = "".join(title.itertext())

            abstract = elem.find('.//Abstract')
            # Abstract is optional
            if abstract is not None:
                article['abstract'] = extract_abstract(abstract)

            authors = elem.find('.//AuthorList')
            # List of authors is optional
            if authors is not None:
                article['author'] = extract_authors(authors)

            journal = elem.find('.//Journal')
            # journal entry is mandatory
            if journal is not None:
                article.update(extract_journaldata(journal, pmid))
            else:
                logging.warning('Article %s should have had a journal entry',
                                pmid)

            yield article
            root.clear()
