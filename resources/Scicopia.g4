grammar Scicopia;

query: part+
     ;

part: exclude | quotes | term | prefixed | SPECIAL ;

exclude: NOT quotes
       | NOT prefixed
       | NOT term
       | NOT SPECIAL
       ;

quotes: '"' .*? '"'
      |  '\'' .*? '\''
      ;

prefixed: ( ALPHA | '_' )+ ':' ( SPECIAL | quotes | term ) ;

term: CHARGED | DASH | NUM | COMPOUND | ALPHA | ABBREV | ALPHANUM | APOSTROPHE ;

// internal dashes for compound words
DASH:  ALPHA ('-' ALPHANUM )+
    |  ( ALPHANUM '-' )+ ALPHA ('-' ALPHANUM )*
    ;

// floating point, serial, model numbers, ip addresses, IUPAC names etc.
NUM: ALPHANUM ( PCT ALPHANUM )+ ;

// terms like (E)-2-epi-beta-Caryophyllene or cis-Muurola-4(14),5-diene
COMPOUND: LPAR ( '-' | '+' | 'E' | 'S' ) RPAR ('-' ( ALPHA | DIGITS ) )+
        | ( ALPHA | DIGITS ) ('-' ( ALPHA | DIGITS (',' DIGITS )* ) | LPAR DIGITS RPAR (',' DIGITS )* )+
        ;

// internal apostrophes: O'Reilly, you're, O'Reilly's
APOSTROPHE: ALPHA ('\'' ALPHA)+ ;

NOT: '-' ;

ALPHA:    ( LETTER )+ ;
DIGITS:   ( DIGIT )+ ;
ABBREV:   ( LETTER )+ '.' ;
CHARGED:  ( ALPHANUM )+ ( '+' | '-' ) ;
ALPHANUM: ( LETTER | DIGIT )+ ;

LPAR: '(' ;
RPAR: ')' ;

SPECIAL: '\u2328' DIGITS '\u2328' ;

fragment LETTER:   [\p{L}] [\p{M}]* ;
fragment DIGIT:    [\p{Nd}] ;
fragment FILEPCT:  '_' | '-' | '.' | ',' ;
fragment PCT:      '_' | '-' | '/' | '.' | ',' ;

WHITESPACE: [ \r\n\t\f]+ -> skip;

