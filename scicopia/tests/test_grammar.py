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


class KeyPrinter(ScicopiaListener):
    def exitKey(self, ctx):
        print("Oh, a key!")


def test_main():
    input_stream = InputStream("Test me")
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    printer = KeyPrinter()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
