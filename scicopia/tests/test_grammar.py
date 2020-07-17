#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:39:17 2020

@author: tech
"""

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from antlr4.tree.Trees import Trees
from scicopia.app.parser.ScicopiaLexer import ScicopiaLexer
from scicopia.app.parser.ScicopiaListener import ScicopiaListener
from scicopia.app.parser.ScicopiaParser import ScicopiaParser


class PartLogger(ScicopiaListener):
    def __init__(self):
        self.tokens = []

    def exitQuery(self, ctx):
        print(f"Oh, a query! {ctx.getText()}")

    def exitPart(self, ctx):
        print(f"Oh, a key! {ctx.getText()}")
        self.tokens.append(ctx.getText())

    def getParts(self):
        return self.tokens


def test_sanity():
    input_stream = InputStream("Test me")
    expected = ["Test", "me"]
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    logger = PartLogger()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(logger, tree)
    assert logger.getParts() == expected


def test_excluded_author():
    input_stream = InputStream("-author:'Foo Bar'")
    expected = "(query (part (exclude - (prefixed author : (quotes ' Foo Bar ')))))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_auto_tags():
    input_stream = InputStream("auto_tags:'Compound Noun'")
    expected = "(query (part (prefixed auto_tags : (quotes ' Compound Noun '))))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_charged_then_term():
    input_stream = InputStream("CH3COO- oxygen")
    expected = "(query (part (term CH3COO-)) (part (term oxygen)))"

    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_charged_then_excluded():
    input_stream = InputStream("CH3COO- -oxygen")
    expected = "(query (part (term CH3COO-)) (part (exclude - (term oxygen))))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_alternating_term_excluded():
    input_stream = InputStream("foo -bar baz")
    expected = (
        "(query (part (term foo)) (part (exclude - (term bar))) (part (term baz)))"
    )
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_alternating_excluded_term():
    input_stream = InputStream("-foo bar -baz")
    expected = "(query (part (exclude - (term foo))) (part (term bar)) (part (exclude - (term baz))))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_charged_neighbours():
    input_stream = InputStream("CH3COO- AcO-")
    expected = "(query (part (term CH3COO-)) (part (term AcO-)))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected


def test_compounds():
    input_stream = InputStream("(E)-2-epi-beta-Caryophyllene cis-Muurola-4(14),5-diene")
    expected = "(query (part (term (E)-2-epi-beta-Caryophyllene)) (part (term cis-Muurola-4(14),5-diene)))"
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    tree = parser.query()
    assert Trees.toStringTree(tree, None, parser) == expected
