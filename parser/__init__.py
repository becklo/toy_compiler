import ply.yacc as yacc
import readline

# Get the token map from the lexer.  This is required.
from tokenizer import tokens

class Node:
    def __init__(self, type, value, children=[]):
        self.type = type
        self.value = value
        self.children = children

def p_program(p):
    """program : function_def
               | statement
               | scope
    """
    p[0] = Node('program', '', [p[1]])

def p_function_def(p):
    """function_def : TYPE ID LPAREN params RPAREN scope
                   | TYPE ID LPAREN RPAREN scope
    """
    if len(p) == 7:
        p[0] = Node('function_def', p[2], [p[4], p[6]])
    if len(p) == 6:
        p[0] = Node('function_def', p[2], [p[5]])

def p_scope(p):
    """scope : LBRACE statement RBRACE"""
    p[0] = Node('scope', '', [p[2]])

def p_params(p):
    """params : param COMMA params
              | param 
    """
    if len(p) == 2:
        p[0] = Node('params', '', [p[1]])
    if len(p) == 4:
        p[0] = Node('params', ',', [p[1], p[3]])

def p_param(p): 
    """param : TYPE ID"""
    p[0] = Node(p[1], p[2], [])

def p_statement_assign(p):
    """assign : TYPE ID ASSIGN expression"""
    p[0] = Node('assign', p[2], [p[4]])

def p_expression_statement(p):
    """statement : expression
                 | assign
    """
    p[0] = Node('statement', '', [p[1]])

def p_int_or_float_exp(p):
    """expression : int_expression
                 | float_expression
    """
    p[0] = Node('expression', '', [p[1]])

def p_float_expression_plus(p):
    """float_expression : float_expression PLUS float_term"""
    p[0] = Node('float_expression', '+', [p[1], p[3]])

def p_float_expression_minus(p):
    """float_expression : float_expression MINUS float_term"""
    p[0] = Node('float_expression', '-', [p[1], p[3]])

def p_float_expression_term(p):
    """float_expression : float_term"""
    p[0] = Node('float_expression', '', [p[1]])

def p_float_term_times(p):
    """float_term : float_term TIMES float_factor"""
    p[0] = Node('float_term', '*', [p[1], p[3]])

def p_float_term_div(p):
    """float_term : float_term DIVIDE float_factor"""
    p[0] = Node('float_term', '/', [p[1], p[3]])

def p_float_term_factor(p):
    """float_term : float_factor"""
    p[0] = Node('float_term', '', [p[1]])

def p_float_factor_num(p):
    """float_factor : FLOAT """ # how to assign IDs to floats?
    p[0] = Node('float_factor', p[1], [])

def p_float_factor_expr(p):
    """float_factor : LPAREN float_expression RPAREN"""
    p[0] = Node('float_factor', '', [p[2]])

def p_int_expression_plus(p):
    """int_expression : int_expression PLUS int_term"""
    p[0] = Node('int_expression', '+', [p[1], p[3]])

def p_int_expression_minus(p):
    """int_expression : int_expression MINUS int_term"""
    p[0] = Node('int_expression', '-', [p[1], p[3]])

def p_int_expression_term(p):
    """int_expression : int_term"""
    p[0] = Node('int_expression', '', [p[1]])

def p_int_term_times(p):
    """int_term : int_term TIMES int_factor"""
    p[0] = Node('int_term', '*', [p[1], p[3]])

def p_int_term_div(p):
    """int_term : int_term DIVIDE int_factor"""
    p[0] = Node('int_term', '/', [p[1], p[3]])

def p_int_term_factor(p):
    """int_term : int_factor"""
    p[0] = Node('int_term', '', [p[1]])

def p_int_factor_num(p):
    """int_factor : NUMBER
              | ID"""
    p[0] = Node('int_factor', p[1], [])

def p_int_factor_expr(p):
    """int_factor : LPAREN int_expression RPAREN"""
    p[0] = Node('int_factor', '', [p[2]])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

def pretty_print(node, indent=0):
    print('  '* indent + node.type + ':'+ str(node.value))
    for child in node.children:
        pretty_print(child, indent+1)

def main():
    while True:
        try:
            s = input('parser > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        pretty_print(result)

if __name__ == '__main__':
    main()
