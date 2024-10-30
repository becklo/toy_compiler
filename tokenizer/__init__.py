import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'FLOAT',
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'RBRACE',
   'LBRACE',
   'ID',
   'TYPE',
   'ASSIGN',
   'COMMA',
   'SEMICOLON'
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'{'
t_RBRACE  = r'}'
t_ASSIGN  = r'='
t_COMMA   = r','
t_SEMICOLON = r';'

def t_TYPE(t):
    r'int|float|bool|string'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Must be defined before NUMBER to avoid that the value matches the NUMBER rule first
def t_FLOAT(t):
    r'[+-]?\d+\.\d+'
    t.value = float(t.value)
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# # Test it out
# data = '''
# 3.24 + 4 * 10
#   + -20 *2
# '''

# # Give the lexer some input
# lexer.input(data)

# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok: 
#         break      # No more input
#     print(tok)