# Generated from Scicopia.g4 by ANTLR 4.8
# encoding: utf-8
import sys
from io import StringIO

from antlr4 import *

if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\24")
        buf.write("@\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2")
        buf.write("\6\2\20\n\2\r\2\16\2\21\3\3\3\3\3\3\3\3\3\3\5\3\31\n\3")
        buf.write("\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4#\n\4\3\5\3\5\7\5")
        buf.write("\'\n\5\f\5\16\5*\13\5\3\5\3\5\3\5\7\5/\n\5\f\5\16\5\62")
        buf.write("\13\5\3\5\5\5\65\n\5\3\6\3\6\3\6\3\6\3\6\5\6<\n\6\3\7")
        buf.write("\3\7\3\7\4(\60\2\b\2\4\6\b\n\f\2\4\3\2\13\f\5\2\6\t\13")
        buf.write("\13\16\20\2F\2\17\3\2\2\2\4\30\3\2\2\2\6\"\3\2\2\2\b\64")
        buf.write("\3\2\2\2\n\66\3\2\2\2\f=\3\2\2\2\16\20\5\4\3\2\17\16\3")
        buf.write("\2\2\2\20\21\3\2\2\2\21\17\3\2\2\2\21\22\3\2\2\2\22\3")
        buf.write("\3\2\2\2\23\31\5\6\4\2\24\31\5\b\5\2\25\31\5\f\7\2\26")
        buf.write("\31\5\n\6\2\27\31\7\23\2\2\30\23\3\2\2\2\30\24\3\2\2\2")
        buf.write("\30\25\3\2\2\2\30\26\3\2\2\2\30\27\3\2\2\2\31\5\3\2\2")
        buf.write("\2\32\33\7\n\2\2\33#\5\b\5\2\34\35\7\n\2\2\35#\5\n\6\2")
        buf.write("\36\37\7\n\2\2\37#\5\f\7\2 !\7\n\2\2!#\7\23\2\2\"\32\3")
        buf.write("\2\2\2\"\34\3\2\2\2\"\36\3\2\2\2\" \3\2\2\2#\7\3\2\2\2")
        buf.write("$(\7\3\2\2%\'\13\2\2\2&%\3\2\2\2\'*\3\2\2\2()\3\2\2\2")
        buf.write("(&\3\2\2\2)+\3\2\2\2*(\3\2\2\2+\65\7\3\2\2,\60\7\4\2\2")
        buf.write("-/\13\2\2\2.-\3\2\2\2/\62\3\2\2\2\60\61\3\2\2\2\60.\3")
        buf.write("\2\2\2\61\63\3\2\2\2\62\60\3\2\2\2\63\65\7\4\2\2\64$\3")
        buf.write("\2\2\2\64,\3\2\2\2\65\t\3\2\2\2\66\67\t\2\2\2\67;\7\5")
        buf.write("\2\28<\7\23\2\29<\5\b\5\2:<\5\f\7\2;8\3\2\2\2;9\3\2\2")
        buf.write("\2;:\3\2\2\2<\13\3\2\2\2=>\t\3\2\2>\r\3\2\2\2\t\21\30")
        buf.write("\"(\60\64;")
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
                      "SNAKE", "DIGITS", "ABBREV", "CHARGED", "ALPHANUM", 
                      "LPAR", "RPAR", "SPECIAL", "WHITESPACE" ]

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
    SNAKE=10
    DIGITS=11
    ABBREV=12
    CHARGED=13
    ALPHANUM=14
    LPAR=15
    RPAR=16
    SPECIAL=17
    WHITESPACE=18

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):

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
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScicopiaParser.T__0) | (1 << ScicopiaParser.T__1) | (1 << ScicopiaParser.DASH) | (1 << ScicopiaParser.NUM) | (1 << ScicopiaParser.COMPOUND) | (1 << ScicopiaParser.APOSTROPHE) | (1 << ScicopiaParser.NOT) | (1 << ScicopiaParser.ALPHA) | (1 << ScicopiaParser.SNAKE) | (1 << ScicopiaParser.ABBREV) | (1 << ScicopiaParser.CHARGED) | (1 << ScicopiaParser.ALPHANUM) | (1 << ScicopiaParser.SPECIAL))) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PartContext(ParserRuleContext):

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


        def SPECIAL(self):
            return self.getToken(ScicopiaParser.SPECIAL, 0)

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
            self.state = 22
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

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 21
                self.match(ScicopiaParser.SPECIAL)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExcludeContext(ParserRuleContext):

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


        def SPECIAL(self):
            return self.getToken(ScicopiaParser.SPECIAL, 0)

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
            self.state = 32
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 24
                self.match(ScicopiaParser.NOT)
                self.state = 25
                self.quotes()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 26
                self.match(ScicopiaParser.NOT)
                self.state = 27
                self.prefixed()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 28
                self.match(ScicopiaParser.NOT)
                self.state = 29
                self.term()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 30
                self.match(ScicopiaParser.NOT)
                self.state = 31
                self.match(ScicopiaParser.SPECIAL)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuotesContext(ParserRuleContext):

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
            self.state = 50
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.T__0]:
                self.enterOuterAlt(localctx, 1)
                self.state = 34
                self.match(ScicopiaParser.T__0)
                self.state = 38
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 35
                        self.matchWildcard() 
                    self.state = 40
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                self.state = 41
                self.match(ScicopiaParser.T__0)
                pass
            elif token in [ScicopiaParser.T__1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 42
                self.match(ScicopiaParser.T__1)
                self.state = 46
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 43
                        self.matchWildcard() 
                    self.state = 48
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                self.state = 49
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

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALPHA(self):
            return self.getToken(ScicopiaParser.ALPHA, 0)

        def SNAKE(self):
            return self.getToken(ScicopiaParser.SNAKE, 0)

        def SPECIAL(self):
            return self.getToken(ScicopiaParser.SPECIAL, 0)

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
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            _la = self._input.LA(1)
            if not(_la==ScicopiaParser.ALPHA or _la==ScicopiaParser.SNAKE):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 53
            self.match(ScicopiaParser.T__2)
            self.state = 57
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.SPECIAL]:
                self.state = 54
                self.match(ScicopiaParser.SPECIAL)
                pass
            elif token in [ScicopiaParser.T__0, ScicopiaParser.T__1]:
                self.state = 55
                self.quotes()
                pass
            elif token in [ScicopiaParser.DASH, ScicopiaParser.NUM, ScicopiaParser.COMPOUND, ScicopiaParser.APOSTROPHE, ScicopiaParser.ALPHA, ScicopiaParser.ABBREV, ScicopiaParser.CHARGED, ScicopiaParser.ALPHANUM]:
                self.state = 56
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
            self.state = 59
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScicopiaParser.DASH) | (1 << ScicopiaParser.NUM) | (1 << ScicopiaParser.COMPOUND) | (1 << ScicopiaParser.APOSTROPHE) | (1 << ScicopiaParser.ALPHA) | (1 << ScicopiaParser.ABBREV) | (1 << ScicopiaParser.CHARGED) | (1 << ScicopiaParser.ALPHANUM))) != 0)):
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





