# Generated from Scicopia.g4 by ANTLR 4.9.2
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .ScicopiaParser import ScicopiaParser
else:
    from ScicopiaParser import ScicopiaParser

# This class defines a complete listener for a parse tree produced by ScicopiaParser.
class ScicopiaListener(ParseTreeListener):

    # Enter a parse tree produced by ScicopiaParser#query.
    def enterQuery(self, ctx: ScicopiaParser.QueryContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#query.
    def exitQuery(self, ctx: ScicopiaParser.QueryContext):
        pass

    # Enter a parse tree produced by ScicopiaParser#part.
    def enterPart(self, ctx: ScicopiaParser.PartContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#part.
    def exitPart(self, ctx: ScicopiaParser.PartContext):
        pass

    # Enter a parse tree produced by ScicopiaParser#exclude.
    def enterExclude(self, ctx: ScicopiaParser.ExcludeContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#exclude.
    def exitExclude(self, ctx: ScicopiaParser.ExcludeContext):
        pass

    # Enter a parse tree produced by ScicopiaParser#quotes.
    def enterQuotes(self, ctx: ScicopiaParser.QuotesContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#quotes.
    def exitQuotes(self, ctx: ScicopiaParser.QuotesContext):
        pass

    # Enter a parse tree produced by ScicopiaParser#prefixed.
    def enterPrefixed(self, ctx: ScicopiaParser.PrefixedContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#prefixed.
    def exitPrefixed(self, ctx: ScicopiaParser.PrefixedContext):
        pass

    # Enter a parse tree produced by ScicopiaParser#term.
    def enterTerm(self, ctx: ScicopiaParser.TermContext):
        pass

    # Exit a parse tree produced by ScicopiaParser#term.
    def exitTerm(self, ctx: ScicopiaParser.TermContext):
        pass


del ScicopiaParser
