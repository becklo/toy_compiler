import ply.yacc as yacc
import readline

# Get the token map from the lexer.  This is required.
from tokenizer import tokens

class Node:
    def __init__(self, type, value, children=[]):
        self.type = type
        self.value = value
        self.children = children

# Define the grammar rules
def p_program(p):
    '''program : expressions 
                | include
    '''
    p[0] = Node('program', '', [p[1]])

def p_include(p):
    ''' include : INCLUDE IDENTIFIER SEMICOLON
    '''
    p[0] = Node(p[1], p[2], [])
 
def p_expressions(p):
    '''expressions : expressions SEMICOLON expression
                    | expression SEMICOLON
                    | expression
    '''
    if (len(p) == 2 or len(p) == 3):
        p[0] = Node('expressions', '', [p[1]])
    else:
        p[0] = Node('expressions', '', [p[1], p[3]])

def p_expression(p):
    '''expression : binary_op_expression 
                    | string_op_expression
                    | binary_cmp_op
                    | assignments
                    | declarations
                    | scopes
                    | function_declaration
                    | external_function_declaration
                    | func_call
                    | while_loop
                    | increment_after
                    | increment_before
                    | for_loop
                    | if_statement
    '''
    p[0] = Node('expression', '', [p[1]])

def p_assignments(p):
    '''assignments : assignment SEMICOLON assignments
                    | assignment SEMICOLON
    '''
    if (len(p) == 3):
        p[0] = Node('assignment', '', [p[1]])
    else:
        p[0] = Node('assignments', '', [p[1], p[3]])

def p_assignment(p):
    '''assignment : TYPE IDENTIFIER ASSIGN expression 
                    | TYPE GLOBAL_VAR ASSIGN expression 
                    | IDENTIFIER ASSIGN expression 
                    | GLOBAL_VAR ASSIGN expression 
    '''
    if (len(p) == 5):
        p[0] = Node(p[3], [p[1], p[2]], [p[4]])
    else:
        p[0] = Node(p[2], p[1],  [p[3]])

def p_function_declaration(p):
    '''function_declaration : TYPE IDENTIFIER func_dec_params SEMICOLON
                            | TYPE IDENTIFIER func_dec_params expressions SEMICOLON
                            | TYPE IDENTIFIER func_dec_params expressions
    '''
    match len(p):
        case 5:
            if p[4] == ';':
                p[0] = Node('function_declaration', [p[1], p[2]], [p[3]])
            else:
                p[0] = Node('function_declaration', [p[1], p[2]], [p[3], p[4]])
        case 6:
            p[0] = Node('function_declaration', [p[1], p[2]], [p[3], p[4]])

def p_external_function_declaration(p):
    '''external_function_declaration : DECLARE TYPE IDENTIFIER func_dec_params SEMICOLON
                                    | DECLARE TYPE IDENTIFIER func_dec_params expressions SEMICOLON
                                    | DECLARE TYPE IDENTIFIER func_dec_params expressions
    '''
    match len(p):
        case 6:
            if p[5] == ';':
                p[0] = Node('external_function_declaration', [p[2], p[3]], [p[4]])
            else:
                p[0] = Node('external_function_declaration', [p[2], p[3]], [p[4], p[5]])
        case 7:
            p[0] = Node('external_function_declaration', [p[2], p[3]], [p[4], p[5]])

def p_func_dec_params(p):
    '''func_dec_params : LPAREN dec_parameters RPAREN
                    | LPAREN RPAREN
    '''
    if (len(p) == 3):
        p[0] = Node('dec_parameters', '' , [])
    else:
        p[0] = p[2]

def p_dec_parameters(p):
    '''dec_parameters : dec_parameters COMMA dec_parameter
                    | dec_parameter
    '''
    if (len(p) == 2):
        p[0] = Node('dec_parameters', '', [p[1]])
    else:
        p[0] = Node('dec_parameter', '', [p[1], p[3]])

def p_dec_parameter(p):
    '''dec_parameter : TYPE IDENTIFIER
                    | THREE_DOTS
    '''
    # THREE_DOTS should only be accepted as only or last parameter
    if (len(p) == 2):
        p[0] = Node('dec_parameter', [p[1]], [])
    else:
        p[0] = Node('dec_parameter', [p[1], p[2]], [])

def p_func_call(p):
    '''func_call : IDENTIFIER func_call_params'''
    p[0] = Node('func_call', p[1], [p[2]])

def p_func_call_params(p):
    '''func_call_params : LPAREN func_call_args RPAREN
                    | LPAREN RPAREN
    '''
    if (len(p) == 3):
        p[0] = Node('func_call_args', '', [])
    else:
        p[0] = p[2]

def p_func_call_args(p):
    '''func_call_args : func_call_args COMMA func_call_arg
                    | func_call_arg
    '''
    if (len(p) == 2):
        p[0] = Node('func_call_args', '', [p[1]])
    else:
        p[0] = Node('func_call_arg', '', [p[1], p[3]])

def p_func_call_arg(p):
    '''func_call_arg : binary_op_expression
                    | string_op_expression
                    | global_var
    '''
    p[0] = Node('func_call_arg','', [p[1]])

def p_declarations(p):
    '''declarations : declaration declarations
                    | declaration
    '''
    if (len(p) == 2):
        p[0] = Node('declarations', '', [p[1]])
    else:
        p[0] = Node('declarations', '', [p[1], p[2]])

def p_declaration(p):
    '''declaration : TYPE IDENTIFIER SEMICOLON
                    | TYPE GLOBAL_VAR SEMICOLON
                    | TYPE IDENTIFIER
                    | TYPE GLOBAL_VAR
    '''
    p[0] = Node('declaration', [p[1], p[2]], [])

def p_scopes(p):
    '''scopes : scope scopes
                | scope
    '''
    if (len(p) == 2):
        p[0] = Node('scopes', '', [p[1]])
    else:
        p[0] = Node('scopes', '', [p[1], p[2]])

def p_scope(p):
    '''scope : LBRACE expressions RBRACE'''
    p[0] = Node('scope', '', [p[2]])

def p_while_loop(p):
    '''while_loop : WHILE LPAREN expression RPAREN expressions '''
    p[0] = Node('while_loop', '', [p[3], p[5]])

def p_for_loop(p):
    '''for_loop : FOR LPAREN expression SEMICOLON expression SEMICOLON expression RPAREN expressions 
                 | FOR LPAREN SEMICOLON SEMICOLON RPAREN expressions 
    '''
    if (len(p) == 7):
        p[0] = Node('for_loop', '', [p[6]])
    else:
        p[0] = Node('for_loop', '', [p[3], p[5], p[7], p[9]])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN expressions 
                    | IF LPAREN expression RPAREN expressions ELSE expressions
    '''
    if (len(p) == 6):
        p[0] = Node('if_statement', '', [p[3], p[5]])
    else:
        p[0] = Node('if_statement', '', [p[3], p[5], p[7]])

def p_global_var(p):
    '''global_var : GLOBAL_VAR'''
    p[0] = Node('global_var', p[1], [])

def p_string_op(p):
    '''string_op_expression : STRING'''
    p[0] = Node('string', p[1], [])

def p_increment_after(p):
    '''increment_after : IDENTIFIER INCREMENT SEMICOLON
                    | GLOBAL_VAR INCREMENT SEMICOLON
                    | IDENTIFIER INCREMENT 
                    | GLOBAL_VAR INCREMENT 
                    | IDENTIFIER DECREMENT SEMICOLON
                    | GLOBAL_VAR DECREMENT SEMICOLON
                    | IDENTIFIER DECREMENT 
                    | GLOBAL_VAR DECREMENT 
    '''
    p[0] = Node(p[2], p[1], [])

def p_increment_before(p):
    '''increment_before : INCREMENT IDENTIFIER SEMICOLON
                    | INCREMENT GLOBAL_VAR SEMICOLON
                    | DECREMENT IDENTIFIER SEMICOLON
                    | DECREMENT GLOBAL_VAR SEMICOLON
                    | INCREMENT IDENTIFIER 
                    | INCREMENT GLOBAL_VAR 
                    | DECREMENT IDENTIFIER 
                    | DECREMENT GLOBAL_VAR 
    '''
    p[0] = Node(p[2], p[1], [])

def p_binary_cmp_op(p):
    '''binary_cmp_op : expression EQUAL expression
                    | expression NOT_EQUAL expression
                    | expression GREATER_THAN expression
                    | expression LESS_THAN expression
                    | expression GREATER_EQUAL expression
                    | expression LESS_EQUAL expression
    '''
    p[0] = Node(p[2], '', [p[1], p[3]])

def p_binary_op_expression(p):
    '''binary_op_expression : binary_op_expression PLUS binary_op_term
                    | binary_op_expression MINUS binary_op_term
                    | MINUS binary_op_expression
                    | binary_op_term
    '''
    if (len(p) == 3):
        p[0] = Node(p[1], '', [p[2]])
    elif (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node('binary_op_expression', '', [p[1]])

def p_term(p):
    '''binary_op_term  : binary_op_term TIMES factor
                        | binary_op_term DIVIDE factor
                        | factor
    '''
    if (len(p) == 3):
        p[0] = Node(p[1], '', [p[2]])
    elif (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node('binary_op_term', '', [p[1]])

def p_factor(p):
    '''factor : INTEGER
                | FLOAT
                | IDENTIFIER
                | LPAREN expression RPAREN
    '''
    if (len(p) == 4):
        p[0] = p[2]
    else:
        if (isinstance(p[1], int)):
            p[0] = Node('int', p[1], [])
        elif (isinstance(p[1], str)):
            p[0] = Node('var', p[1], [])
        elif (isinstance(p[1], float)):
            p[0] = Node('float', p[1], [])
        else:
            print("Invalid factor type")

# Error rule for syntax errors
def p_error(p):
    raise Exception("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

def pretty_print(node, indent=0):
    print_string = '  '* indent
    print_string += str(node.type) +' : '
    if str(node.type) == '='  and len(node.value) == 2:
        print_string += '(' + str(node.value[0]) +') ' + str(node.value[1]) +' '
    else:
        print_string += str(node.value) +' '

    print(print_string)
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
