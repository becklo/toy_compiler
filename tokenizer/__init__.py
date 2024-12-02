import ply.lex as lex

reserved = {
   'include' : 'INCLUDE',
   'if' : 'IF',
   'else' : 'ELSE',
   'while' : 'WHILE',
   'for' : 'FOR',
   'return' : 'RETURN',
   'declare' : 'DECLARE'
}

# List of token names.   This is always required
tokens = [
   'FLOAT',
   'INTEGER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'RBRACE',
   'LBRACE',
   'IDENTIFIER',
   'TYPE',
   'ASSIGN',
   'COMMA',
   'SEMICOLON',
   'STRING',
#    'EXTERNAL_FUNC',
   'THREE_DOTS',
   'DOT',
   'EQUAL',
   'NOT_EQUAL',
   'GREATER_THAN',
   'LESS_THAN',
   'GREATER_EQUAL',
   'LESS_EQUAL',
   'GLOBAL_VAR',
   'INCREMENT_PREFIX',
   'DECREMENT_PREFIX',
   'INCREMENT_POSTFIX',
   'DECREMENT_POSTFIX',
   'AND',
   'OR',
   'NOT',
   'TRUE',
   'FALSE'
]

tokens += list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'\-'
t_TIMES   = r'\*'
t_DIVIDE  = r'\/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_ASSIGN  = r'\='
t_COMMA   = r'\,'
t_SEMICOLON = r'\;'
t_THREE_DOTS = r'\.{3}'
t_DOT     = r'\.'
t_EQUAL = r'\=\='
t_NOT_EQUAL = r'\!\='
t_GREATER_THAN = r'\>'
t_LESS_THAN = r'\<'
t_GREATER_EQUAL = r'\>\='
t_LESS_EQUAL = r'\<\='
t_ignore_COMMENT = r'\#.*'

def t_AND(t):
    r'&&|and|AND'
    return t

def t_OR(t):
    r'\|\||or|OR'
    return t

def t_NOT(t):
    r'!|not|NOT'
    return t

def t_TRUE(t):
    r'(?i)true'
    return t

def t_FALSE(t):
    r'(?i)false'
    return t

def t_STRING(t):
    r'\".*\n?\"'
    t.value = t.value[1:-1]
    return t

def t_TYPE(t):
    r'int|float|bool|str'
    return t

def t_INCREMENT_PREFIX(t):
    r'\+\+[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value[2:]
    return t

def t_DECREMENT_PREFIX(t):
    r'\-\-[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value[2:]
    return t

def t_INCREMENT_POSTFIX(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*\+\+'
    t.value = t.value[:-2]
    return t

def t_DECREMENT_POSTFIX(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*\-\-'
    t.value = t.value[:-2]
    return t

def t_GLOBAL_VAR(t):
    r'Global\_[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# def t_EXTERNAL_FUNC(t):
#     r'external\_[a-zA-Z_][a-zA-Z0-9_]*'
#     return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

# Must be defined before INTEGER to avoid that the value matches the INTEGER rule first
def t_FLOAT(t):
    r'[+-]?\d+\.\d+'
    t.value = float(t.value)
    return t

# A regular expression rule with some action code
def t_INTEGER(t):
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

# Test it out
data = '''
# This is a comment until the end of the line 
include ModuleNameSomewhere; # this should act like a C include, we will ignore it initially and implement it later
int Global_Variable;
float Global_Float = 3*5-(36/6);
str Global_str = "String content\n";
declare int external_function1();
declare int external_function2(int a, int b);
declare int printf(str text,...); # variable argument
int fibonacci(int n) if (n < 2) 1 else fibonacci(n-1)+fibonacci(n-2) # remember if is an expression now so it returns a value, and the latest value in scope is also a return statement so this is implicit return. Also we do not have a scope block because we have defined a function to have an expression, while in expression we can have many scope blocks
int one() 1; # here we have implicit return of 1
int two() return 2; # here we have explicit return of 2
int something(float b) { if (one() < two() and { 5*6 >= 4*6}) { return 1}; return 2;}
int main() { if (something(2.1*5) > 0) { printf("Hello world %s\n", Global_str);}
int n = { -5};
while (n<0) n++; n # this is going to be our return value
}
'''

def main():
    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        print(tok)

if __name__ == "__main__":
    main()