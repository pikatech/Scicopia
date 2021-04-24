#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:39:17 2020

@author: tech
"""

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker

from scicopia.app.parser.QueryListener import QueryListener
from scicopia.app.parser.ScicopiaLexer import ScicopiaLexer
from scicopia.app.parser.ScicopiaParser import ScicopiaParser


def test_sanity():
    input_stream = InputStream("Test me")
    expected = [{"multi_match": {"query": "Test"}}, {"multi_match": {"query": "me"}}]
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    listener = QueryListener()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    queries = listener.getQueries()
    assert "must" in queries
    assert queries["must"] == expected


def test_phrase():
    input_stream = InputStream("'Test me'")
    expected = [{"multi_match": {"query": "Test me", "type": "phrase"}}]
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    listener = QueryListener()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    queries = listener.getQueries()
    assert "must" in queries
    assert queries["must"] == expected


def test_excluded_author():
    input_stream = InputStream("-author:'Foo Bar'")
    expected = [{"match_phrase": {"author": "Foo Bar"}}]
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    listener = QueryListener()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    queries = listener.getQueries()
    assert "must_not" in queries
    assert queries["must_not"] == expected
