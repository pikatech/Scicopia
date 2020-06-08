# Generated from Scicopia.g4 by ANTLR 4.8
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
        buf.write("T\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\3\2\6\2\22\n\2\r\2\16\2\23\3\2\6\2\27\n\2\r\2\16")
        buf.write("\2\30\5\2\33\n\2\3\3\3\3\3\3\3\3\5\3!\n\3\3\4\3\4\3\4")
        buf.write("\3\5\3\5\7\5(\n\5\f\5\16\5+\13\5\3\5\3\5\3\5\7\5\60\n")
        buf.write("\5\f\5\16\5\63\13\5\3\5\5\5\66\n\5\3\6\6\69\n\6\r\6\16")
        buf.write("\6:\3\6\3\6\3\6\3\6\5\6A\n\6\3\7\3\7\3\7\3\7\3\7\3\7\3")
        buf.write("\7\3\7\5\7K\n\7\3\b\6\bN\n\b\r\b\16\bO\3\b\3\b\3\b\4)")
        buf.write("\61\2\t\2\4\6\b\n\f\16\2\3\4\2\6\6\13\13\2`\2\32\3\2\2")
        buf.write("\2\4 \3\2\2\2\6\"\3\2\2\2\b\65\3\2\2\2\n8\3\2\2\2\fJ\3")
        buf.write("\2\2\2\16M\3\2\2\2\20\22\5\4\3\2\21\20\3\2\2\2\22\23\3")
        buf.write("\2\2\2\23\21\3\2\2\2\23\24\3\2\2\2\24\33\3\2\2\2\25\27")
        buf.write("\5\6\4\2\26\25\3\2\2\2\27\30\3\2\2\2\30\26\3\2\2\2\30")
        buf.write("\31\3\2\2\2\31\33\3\2\2\2\32\21\3\2\2\2\32\26\3\2\2\2")
        buf.write("\33\3\3\2\2\2\34!\5\b\5\2\35!\5\f\7\2\36!\5\n\6\2\37!")
        buf.write("\7\22\2\2 \34\3\2\2\2 \35\3\2\2\2 \36\3\2\2\2 \37\3\2")
        buf.write("\2\2!\5\3\2\2\2\"#\7\13\2\2#$\5\4\3\2$\7\3\2\2\2%)\7\3")
        buf.write("\2\2&(\13\2\2\2\'&\3\2\2\2(+\3\2\2\2)*\3\2\2\2)\'\3\2")
        buf.write("\2\2*,\3\2\2\2+)\3\2\2\2,\66\7\3\2\2-\61\7\4\2\2.\60\13")
        buf.write("\2\2\2/.\3\2\2\2\60\63\3\2\2\2\61\62\3\2\2\2\61/\3\2\2")
        buf.write("\2\62\64\3\2\2\2\63\61\3\2\2\2\64\66\7\4\2\2\65%\3\2\2")
        buf.write("\2\65-\3\2\2\2\66\t\3\2\2\2\679\7\r\2\28\67\3\2\2\29:")
        buf.write("\3\2\2\2:8\3\2\2\2:;\3\2\2\2;<\3\2\2\2<@\7\5\2\2=A\7\22")
        buf.write("\2\2>A\5\b\5\2?A\5\f\7\2@=\3\2\2\2@>\3\2\2\2@?\3\2\2\2")
        buf.write("A\13\3\2\2\2BK\7\7\2\2CK\7\b\2\2DK\7\t\2\2EK\7\r\2\2F")
        buf.write("K\7\16\2\2GK\7\17\2\2HK\5\16\b\2IK\7\n\2\2JB\3\2\2\2J")
        buf.write("C\3\2\2\2JD\3\2\2\2JE\3\2\2\2JF\3\2\2\2JG\3\2\2\2JH\3")
        buf.write("\2\2\2JI\3\2\2\2K\r\3\2\2\2LN\7\17\2\2ML\3\2\2\2NO\3\2")
        buf.write("\2\2OM\3\2\2\2OP\3\2\2\2PQ\3\2\2\2QR\t\2\2\2R\17\3\2\2")
        buf.write("\2\r\23\30\32 )\61\65:@JO")
        return buf.getvalue()


class ScicopiaParser ( Parser ):

    grammarFileName = "Scicopia.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\"'", "'''", "':'", "'+'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'-'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "DASH", "NUM", "COMPOUND", "APOSTROPHE", 
                      "NOT", "DIGITS", "ALPHA", "ABBREV", "ALPHANUM", "LPAR", 
                      "RPAR", "SPECIAL", "WHITESPACE" ]

    RULE_query = 0
    RULE_part = 1
    RULE_logical = 2
    RULE_quotes = 3
    RULE_prefixed = 4
    RULE_term = 5
    RULE_charged = 6

    ruleNames =  [ "query", "part", "logical", "quotes", "prefixed", "term", 
                   "charged" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    DASH=5
    NUM=6
    COMPOUND=7
    APOSTROPHE=8
    NOT=9
    DIGITS=10
    ALPHA=11
    ABBREV=12
    ALPHANUM=13
    LPAR=14
    RPAR=15
    SPECIAL=16
    WHITESPACE=17

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


        def logical(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ScicopiaParser.LogicalContext)
            else:
                return self.getTypedRuleContext(ScicopiaParser.LogicalContext,i)


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
            self.state = 24
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.T__0, ScicopiaParser.T__1, ScicopiaParser.DASH, ScicopiaParser.NUM, ScicopiaParser.COMPOUND, ScicopiaParser.APOSTROPHE, ScicopiaParser.ALPHA, ScicopiaParser.ABBREV, ScicopiaParser.ALPHANUM, ScicopiaParser.SPECIAL]:
                self.enterOuterAlt(localctx, 1)
                self.state = 15 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 14
                    self.part()
                    self.state = 17 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ScicopiaParser.T__0) | (1 << ScicopiaParser.T__1) | (1 << ScicopiaParser.DASH) | (1 << ScicopiaParser.NUM) | (1 << ScicopiaParser.COMPOUND) | (1 << ScicopiaParser.APOSTROPHE) | (1 << ScicopiaParser.ALPHA) | (1 << ScicopiaParser.ABBREV) | (1 << ScicopiaParser.ALPHANUM) | (1 << ScicopiaParser.SPECIAL))) != 0)):
                        break

                pass
            elif token in [ScicopiaParser.NOT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 20 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 19
                    self.logical()
                    self.state = 22 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==ScicopiaParser.NOT):
                        break

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


    class PartContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

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
            self.state = 30
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 26
                self.quotes()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 27
                self.term()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 28
                self.prefixed()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 29
                self.match(ScicopiaParser.SPECIAL)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(ScicopiaParser.NOT, 0)

        def part(self):
            return self.getTypedRuleContext(ScicopiaParser.PartContext,0)


        def getRuleIndex(self):
            return ScicopiaParser.RULE_logical

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogical" ):
                listener.enterLogical(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogical" ):
                listener.exitLogical(self)




    def logical(self):

        localctx = ScicopiaParser.LogicalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_logical)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self.match(ScicopiaParser.NOT)
            self.state = 33
            self.part()
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
            self.state = 51
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.T__0]:
                self.enterOuterAlt(localctx, 1)
                self.state = 35
                self.match(ScicopiaParser.T__0)
                self.state = 39
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 36
                        self.matchWildcard() 
                    self.state = 41
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                self.state = 42
                self.match(ScicopiaParser.T__0)
                pass
            elif token in [ScicopiaParser.T__1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 43
                self.match(ScicopiaParser.T__1)
                self.state = 47
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 44
                        self.matchWildcard() 
                    self.state = 49
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                self.state = 50
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

        def SPECIAL(self):
            return self.getToken(ScicopiaParser.SPECIAL, 0)

        def quotes(self):
            return self.getTypedRuleContext(ScicopiaParser.QuotesContext,0)


        def term(self):
            return self.getTypedRuleContext(ScicopiaParser.TermContext,0)


        def ALPHA(self, i:int=None):
            if i is None:
                return self.getTokens(ScicopiaParser.ALPHA)
            else:
                return self.getToken(ScicopiaParser.ALPHA, i)

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
            self.state = 54 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 53
                self.match(ScicopiaParser.ALPHA)
                self.state = 56 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ScicopiaParser.ALPHA):
                    break

            self.state = 58
            self.match(ScicopiaParser.T__2)
            self.state = 62
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ScicopiaParser.SPECIAL]:
                self.state = 59
                self.match(ScicopiaParser.SPECIAL)
                pass
            elif token in [ScicopiaParser.T__0, ScicopiaParser.T__1]:
                self.state = 60
                self.quotes()
                pass
            elif token in [ScicopiaParser.DASH, ScicopiaParser.NUM, ScicopiaParser.COMPOUND, ScicopiaParser.APOSTROPHE, ScicopiaParser.ALPHA, ScicopiaParser.ABBREV, ScicopiaParser.ALPHANUM]:
                self.state = 61
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

        def charged(self):
            return self.getTypedRuleContext(ScicopiaParser.ChargedContext,0)


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
        try:
            self.state = 72
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 64
                self.match(ScicopiaParser.DASH)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 65
                self.match(ScicopiaParser.NUM)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 66
                self.match(ScicopiaParser.COMPOUND)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 67
                self.match(ScicopiaParser.ALPHA)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 68
                self.match(ScicopiaParser.ABBREV)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 69
                self.match(ScicopiaParser.ALPHANUM)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 70
                self.charged()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 71
                self.match(ScicopiaParser.APOSTROPHE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ChargedContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(ScicopiaParser.NOT, 0)

        def ALPHANUM(self, i:int=None):
            if i is None:
                return self.getTokens(ScicopiaParser.ALPHANUM)
            else:
                return self.getToken(ScicopiaParser.ALPHANUM, i)

        def getRuleIndex(self):
            return ScicopiaParser.RULE_charged

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCharged" ):
                listener.enterCharged(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCharged" ):
                listener.exitCharged(self)




    def charged(self):

        localctx = ScicopiaParser.ChargedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_charged)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 74
                self.match(ScicopiaParser.ALPHANUM)
                self.state = 77 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ScicopiaParser.ALPHANUM):
                    break

            self.state = 79
            _la = self._input.LA(1)
            if not(_la==ScicopiaParser.T__3 or _la==ScicopiaParser.NOT):
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





