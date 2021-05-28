grammar Scicopia;

query: part+
     ;

part: exclude | quotes | term | prefixed ;

exclude: NOT quotes
       | NOT prefixed
       | NOT term
       ;

quotes: '"' .*? '"'
      |  '\'' .*? '\''
      ;

prefixed: ( ALPHA | SNAKE ) ':' ( quotes | term ) ;

term: CHARGED
    | DASH
    | NUM 
    | COMPOUND 
    | ALPHA 
    | ABBREV 
    | ALPHANUM 
    | APOSTROPHE
    | DIGITS
    | STRING 
    ;

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
SNAKE:    ( LETTER | '_' )+ ;
DIGITS:   ( DIGIT )+ ;
ABBREV:   ( LETTER )+ '.' ;
CHARGED:  ( ALPHANUM )+ ( '+' | '-' ) ;
ALPHANUM: ( LETTER | DIGIT )+ ;
STRING :  ( LETTER | DIGIT | ASCII)+ ;

LPAR: '(' ;
RPAR: ')' ;

fragment LETTER:   [\p{L}] [\p{M}]* ; // Letters and combining modifiers
fragment DIGIT:    [\p{Nd}] ;
fragment PCT:      '-' | '/' | '.' | ',' ;
// ASCII punctuation without quotes or special characters of the grammar
fragment ASCII: [!#$%&;^~_*+,./<=>?@] ;

WHITESPACE: [ \r\n\t\f]+ -> skip;

