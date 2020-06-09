#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 11:39:17 2020

@author: tech
"""

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from app.parser.ScicopiaLexer import ScicopiaLexer
from app.parser.ScicopiaListener import ScicopiaListener
from app.parser.ScicopiaParser import ScicopiaParser


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
