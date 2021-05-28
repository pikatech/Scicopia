#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 22:03:45 2020

@author: tech
"""
from collections import deque

from .ScicopiaListener import ScicopiaListener
from .ScicopiaParser import ScicopiaParser


class QueryListener(ScicopiaListener):
    def enterQuery(self, ctx: ScicopiaParser.QueryContext):
        self.term = None
        # A special case where just one word is quoted
        self.quoted_term = None
        self.phrase = None
        self.prefixed = None
        self.exclude = None
        self.queries = {"must": [], "must_not": [], "terms": deque()}
        self.counter = 0

    def exitPart(self, ctx: ScicopiaParser.PartContext):
        if not self.term is None:
            self.queries["terms"].append((self.counter, self.term))
            # self.queries["must"].append({"multi_match": {"query": self.term}})
            self.term = None
        elif not self.quoted_term is None:
            self.queries["must"].append({"multi_match": {"query": self.quoted_term}})
            self.quoted_term = None
        elif not self.phrase is None:
            self.queries["must"].append(
                {"multi_match": {"query": self.phrase, "type": "phrase"}}
            )
            self.phrase = None
        elif not self.prefixed is None:
            self.queries["must"].append(self.prefixed)

    def exitTerm(self, ctx: ScicopiaParser.TermContext):
        self.term = ctx.getText()
        self.counter += 1

    def exitQuotes(self, ctx: ScicopiaParser.QuotesContext):
        text = []
        for i in range(1, ctx.getChildCount() - 1):
            text.append(ctx.children[i].getText())
            self.counter += 1
        if ctx.getChildCount == 3:  # ' token '
            self.quoted_term = text[0]
        else:
            self.phrase = " ".join(text)

    def exitPrefixed(self, ctx: ScicopiaParser.PrefixedContext):
        text: str = ctx.getText()
        self.counter += 1
        field = text[: text.index(":")]
        if not self.term is None:
            self.prefixed = {"match": {field: self.term}}
            self.term = None
        elif not self.phrase is None:
            self.prefixed = {"match_phrase": {field: self.phrase}}
            self.phrase = None

    def exitExclude(self, ctx: ScicopiaParser.ExcludeContext):
        if not self.term is None:
            self.queries["must_not"].append({"multi_match": {"query": self.term}})
            self.term = None
        elif not self.phrase is None:
            self.queries["must_not"].append(
                {"multi_match": {"query": self.phrase, "type": "phrase"}}
            )
            self.term = None
        elif not self.prefixed is None:
            self.queries["must_not"].append(self.prefixed)

    def getQueries(self):
        return self.queries
