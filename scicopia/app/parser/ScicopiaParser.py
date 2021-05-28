# Generated from Scicopia.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\23")
        buf.write("<\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2")
        buf.write("\6\2\20\n\2\r\2\16\2\21\3\3\3\3\3\3\3\3\5\3\30\n\3\3\4")
        buf.write("\3\4\3\4\3\4\3\4\3\4\5\4 \n\4\3\5\3\5\7\5$\n\5\f\5\16")
        buf.write("\5\'\13\5\3\5\3\5\3\5\7\5,\n\5\f\5\16\5/\13\5\3\5\5\5")
        buf.write("\62\n\5\3\6\3\6\3\6\3\6\5\68\n\6\3\7\3\7\3\7\4%-\2\b\2")
        buf.write("\4\6\b\n\f\2\3\4\2\6\t\13\20\2?\2\17\3\2\2\2\4\27\3\2")
        buf.write("\2\2\6\37\3\2\2\2\b\61\3\2\2\2\n\63\3\2\2\2\f9\3\2\2\2")
        buf.write("\16\20\5\4\3\2\17\16\3\2\2\2\20\21\3\2\2\2\21\17\3\2\2")
        buf.write("\2\21\22\3\2\2\2\22\3\3\2\2\2\23\30\5\6\4\2\24\30\5\b")
        buf.write("\5\2\25\30\5\f\7\2\26\30\5\n\6\2\27\23\3\2\2\2\27\24\3")
        buf.write("\2\2\2\27\25\3\2\2\2\27\26\3\2\2\2\30\5\3\2\2\2\31\32")
        buf.write("\7\n\2\2\32 \5\b\5\2\33\34\7\n\2\2\34 \5\n\6\2\35\36\7")
        buf.write("\n\2\2\36 \5\f\7\2\37\31\3\2\2\2\37\33\3\2\2\2\37\35\3")
        buf.write("\2\2\2 \7\3\2\2\2!%\7\3\2\2\"$\13\2\2\2#\"\3\2\2\2$\'")
        buf.write("\3\2\2\2%&\3\2\2\2%#\3\2\2\2&(\3\2\2\2\'%\3\2\2\2(\62")
        buf.write("\7\3\2\2)-\7\4\2\2*,\13\2\2\2+*\3\2\2\2,/\3\2\2\2-.\3")
        buf.write("\2\2\2-+\3\2\2\2.\60\3\2\2\2/-\3\2\2\2\60\62\7\4\2\2\61")
        buf.write("!\3\2\2\2\61)\3\2\2\2\62\t\3\2\2\2\63\64\7\13\2\2\64\67")
        buf.write("\7\5\2\2\658\5\b\5\2\668\5\f\7\2\67\65\3\2\2\2\67\66\3")
        buf.write("\2\2\28\13\3\2\2\29:\t\2\2\2:\r\3\2\2\2\t\21\27\37%-\61")
        buf.write("\67")
        return buf.getvalue()


class ScicopiaParser ( Parser ):

    grammarFileName = "Scicopia.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\"'", "'''", "':'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'-'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "DASH", "NUM", "COMPOUND", "APOSTROPHE", "NOT", "ALPHA", 
                      "DIGITS", "ABBREV", "CHARGED", "ALPHANUM", "STRING", 
                      "LPAR", "RPAR", "WHITESPACE" ]

    RULE_query = 0
    RULE_part = 1
    RULE_exclude = 2
    RULE_quotes = 3
    RULE_prefixed = 4
    RULE_term = 5

    ruleNames =  [ "query", "part", "exclude", "quotes", "prefixed", "term" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    DASH=4
    NUM=5
    COMPOUND=6
    APOSTROPHE=7
    NOT=8
    ALPHA=9
    DIGITS=10
    ABBREV=11
    CHARGED=12
    ALPHANUM=13
    STRING=14
    LPAR=15
    RPAR=16
    WHITESPACE=17

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def part(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScicopiaParser.PartContext)
            else:
                return self.getTypedRuleContext(ScicopiaParser.PartContext,i)


        def getRuleIndex(self):
            return ScicopiaParser.RULE_query

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery" ):
                listener.enterQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery" ):
                listener.exitQuery(self)




    def query(self):

        localctx = ScicopiaParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 12
                self.part()
                self.state = 15 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScicopiaParser.T__0) | (1 << ScicopiaParser.T__1) | (1 << ScicopiaParser.DASH) | (1 << ScicopiaParser.NUM) | (1 << ScicopiaParser.COMPOUND) | (1 << ScicopiaParser.APOSTROPHE) | (1 << ScicopiaParser.NOT) | (1 << ScicopiaParser.ALPHA) | (1 << ScicopiaParser.DIGITS) | (1 << ScicopiaParser.ABBREV) | (1 << ScicopiaParser.CHARGED) | (1 << ScicopiaParser.ALPHANUM) | (1 << ScicopiaParser.STRING))) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PartContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def exclude(self):
            return self.getTypedRuleContext(ScicopiaParser.ExcludeContext,0)


        def quotes(self):
            return self.getTypedRuleContext(ScicopiaParser.QuotesContext,0)


        def term(self):
            return self.getTypedRuleContext(ScicopiaParser.TermContext,0)


        def prefixed(self):
            return self.getTypedRuleContext(ScicopiaParser.PrefixedContext,0)


        def getRuleIndex(self):
            return ScicopiaParser.RULE_part

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPart" ):
                listener.enterPart(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPart" ):
                listener.exitPart(self)




    def part(self):

        localctx = ScicopiaParser.PartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_part)
        try:
            self.state = 21
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 17
                self.exclude()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 18
                self.quotes()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 19
                self.term()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 20
                self.prefixed()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExcludeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(ScicopiaParser.NOT, 0)

        def quotes(self):
            return self.getTypedRuleContext(ScicopiaParser.QuotesContext,0)


        def prefixed(self):
            return self.getTypedRuleContext(ScicopiaParser.PrefixedContext,0)


        def term(self):
            return self.getTypedRuleContext(ScicopiaParser.TermContext,0)


        def getRuleIndex(self):
            return ScicopiaParser.RULE_exclude

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExclude" ):
                listener.enterExclude(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExclude" ):
                listener.exitExclude(self)




    def exclude(self):

        localctx = ScicopiaParser.ExcludeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_exclude)
        try:
            self.state = 29
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 23
                self.match(ScicopiaParser.NOT)
                self.state = 24
                self.quotes()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 25
                self.match(ScicopiaParser.NOT)
                self.state = 26
                self.prefixed()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 27
                self.match(ScicopiaParser.NOT)
                self.state = 28
                self.term()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuotesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ScicopiaParser.RULE_quotes

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuotes" ):
                listener.enterQuotes(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuotes" ):
                listener.exitQuotes(self)




    def quotes(self):

        localctx = ScicopiaParser.QuotesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_quotes)
        try:
            self.state = 47
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.T__0]:
                self.enterOuterAlt(localctx, 1)
                self.state = 31
                self.match(ScicopiaParser.T__0)
                self.state = 35
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 32
                        self.matchWildcard() 
                    self.state = 37
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                self.state = 38
                self.match(ScicopiaParser.T__0)
                pass
            elif token in [ScicopiaParser.T__1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 39
                self.match(ScicopiaParser.T__1)
                self.state = 43
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 40
                        self.matchWildcard() 
                    self.state = 45
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                self.state = 46
                self.match(ScicopiaParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrefixedContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALPHA(self):
            return self.getToken(ScicopiaParser.ALPHA, 0)

        def quotes(self):
            return self.getTypedRuleContext(ScicopiaParser.QuotesContext,0)


        def term(self):
            return self.getTypedRuleContext(ScicopiaParser.TermContext,0)


        def getRuleIndex(self):
            return ScicopiaParser.RULE_prefixed

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrefixed" ):
                listener.enterPrefixed(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrefixed" ):
                listener.exitPrefixed(self)




    def prefixed(self):

        localctx = ScicopiaParser.PrefixedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_prefixed)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.match(ScicopiaParser.ALPHA)
            self.state = 50
            self.match(ScicopiaParser.T__2)
            self.state = 53
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.T__0, ScicopiaParser.T__1]:
                self.state = 51
                self.quotes()
                pass
            elif token in [ScicopiaParser.DASH, ScicopiaParser.NUM, ScicopiaParser.COMPOUND, ScicopiaParser.APOSTROPHE, ScicopiaParser.ALPHA, ScicopiaParser.DIGITS, ScicopiaParser.ABBREV, ScicopiaParser.CHARGED, ScicopiaParser.ALPHANUM, ScicopiaParser.STRING]:
                self.state = 52
                self.term()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TermContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CHARGED(self):
            return self.getToken(ScicopiaParser.CHARGED, 0)

        def DASH(self):
            return self.getToken(ScicopiaParser.DASH, 0)

        def NUM(self):
            return self.getToken(ScicopiaParser.NUM, 0)

        def COMPOUND(self):
            return self.getToken(ScicopiaParser.COMPOUND, 0)

        def ALPHA(self):
            return self.getToken(ScicopiaParser.ALPHA, 0)

        def ABBREV(self):
            return self.getToken(ScicopiaParser.ABBREV, 0)

        def ALPHANUM(self):
            return self.getToken(ScicopiaParser.ALPHANUM, 0)

        def APOSTROPHE(self):
            return self.getToken(ScicopiaParser.APOSTROPHE, 0)

        def DIGITS(self):
            return self.getToken(ScicopiaParser.DIGITS, 0)

        def STRING(self):
            return self.getToken(ScicopiaParser.STRING, 0)

        def getRuleIndex(self):
            return ScicopiaParser.RULE_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTerm" ):
                listener.enterTerm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTerm" ):
                listener.exitTerm(self)




    def term(self):

        localctx = ScicopiaParser.TermContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_term)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScicopiaParser.DASH) | (1 << ScicopiaParser.NUM) | (1 << ScicopiaParser.COMPOUND) | (1 << ScicopiaParser.APOSTROPHE) | (1 << ScicopiaParser.ALPHA) | (1 << ScicopiaParser.DIGITS) | (1 << ScicopiaParser.ABBREV) | (1 << ScicopiaParser.CHARGED) | (1 << ScicopiaParser.ALPHANUM) | (1 << ScicopiaParser.STRING))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





