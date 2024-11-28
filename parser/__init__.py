import ply.yacc as yacc
import history

# Get the token map from the lexer.  This is required.
from tokenizer import tokens

class Node:
    def __init__(self, type, value, children=[]):
        self.type = type
        self.value = value
        self.children = children

def p_test(p):
    """mytest : mytest scope 
                | scope
                | mytest SEMICOLON
                | SEMICOLON"""
    if len(p) == 3:
        if p[2]==';':
            p[0] = Node('test', '', [p[1]])
        else:
            p[0] = Node('test', '', [p[1],p[2]])
    else: 
        if(p[1] == ';'):
            p[0] = Node(';', '', [])
        else:
            p[0] = Node('test', '', [p[1]])


# Define the grammar rules
def p_program(p):
    '''program : program global_var
                | global_var
                | program function_declaration
                | function_declaration
                | program func_call
                | func_call
                | program SEMICOLON
                | SEMICOLON
                | program external_function_declaration
                | external_function_declaration
                | program include
                | include
                | program scope
                | scope
    '''
    if (len(p) == 2):
        if(p[1] == ';'):
            p[0] = Node(';', '', [])
        else:
            p[0] = Node('program', '', [p[1]])
    else:
        if(p[2] == ';'):
            p[0] = Node('program', '', [p[1]])
        else:
            p[0] = Node('program', '', [p[1], p[2]])

def p_global_var(p):
    '''global_var : GLOBAL_VAR'''
    p[0] = Node('global_var', p[1], [])

def p_include(p):
    ''' include : INCLUDE IDENTIFIER
    '''
    p[0] = Node(p[1], p[2], [])

def p_external_function_declaration(p):
    '''external_function_declaration : DECLARE TYPE IDENTIFIER func_dec_params
    '''
    p[0] = Node('external_function_declaration', [p[2], p[3]], [p[4]])

def p_function_declaration(p):
    '''function_declaration : TYPE IDENTIFIER func_dec_params scope
    '''
    p[0] = Node('function_declaration', [p[1], p[2]], [p[3], p[4]])

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
    '''func_call_arg : binary_expression
                    | string_op_expression
                    | global_var
    '''
    p[0] = Node('func_call_arg','', [p[1]])

def p_scope(p):
    '''scope : LBRACE statements RBRACE
                | LBRACE RBRACE
    '''
    if (len(p) == 4):
        p[0] = Node('scope', '', [p[2]])
    # if (len(p) == 2):
    #     p[0] = Node('scope', '', [p[1]])
    else:
        p[0] = Node('scope', '', [])

def p_statements(p):
    '''statements : statements statement
                    | statements SEMICOLON
                    | SEMICOLON
                    | statement
    '''
    if (len(p) == 2):
        if p[1] == ';':
            p[0] = Node('statements', ';', [])
        else:
            p[0] = Node('statements', '', [p[1]])
    else:
        if p[2] == ';':
            p[0] = Node('statements', ';', [p[1]])
        else:
            p[0] = Node('statements', '', [p[1], p[2]])

def p_statement(p):
    '''statement : expression
                    | assignments
                    | declarations
                    | while_loop
                    | for_loop
                    | if_statement
                    | return_statement
    '''
    p[0] = Node('statement', '', [p[1]])

def p_expression(p):
    '''expression : binary_expression 
                    | string_op_expression
                    | increment_after
                    | increment_before
                    | logical_op_expression
    '''
    p[0] = Node('expression', '', [p[1]])

def p_assignments(p):
    '''assignments : assignment SEMICOLON assignments
                    | assignment
    '''
    if (len(p) == 2):
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

def p_declarations(p):
    '''declarations : declaration declarations
                    | declaration
    '''
    if (len(p) == 2):
        p[0] = Node('declarations', '', [p[1]])
    else:
        p[0] = Node('declarations', '', [p[1], p[2]])

def p_declaration(p):
    '''declaration : TYPE IDENTIFIER 
                    | TYPE GLOBAL_VAR
    '''
    p[0] = Node('declaration', [p[1], p[2]], [])

def p_while_loop(p):
    '''while_loop : WHILE LPAREN expression RPAREN scope '''
    p[0] = Node('while_loop', '', [p[3], p[5]])

def p_for_loop(p):
    '''for_loop : FOR LPAREN statement SEMICOLON statement SEMICOLON statement RPAREN scope 
                    | FOR LPAREN RPAREN scope 
                    | FOR LPAREN SEMICOLON SEMICOLON RPAREN scope
                    | FOR LPAREN statement SEMICOLON RPAREN scope
                    | FOR LPAREN statement SEMICOLON statement RPAREN
    '''
    match(len(p)):
        case 10:
            p[0] = Node('for_loop', '', [p[3], p[5], p[7], p[9]])
        case 5:
            p[0] = Node('for_loop', '', [p[4]])
        case 7:
            if (p[3] == ';'):
                p[0] = Node('for_loop', '', [p[6]])
            else:
                if (p[5] == ')'):
                    p[0] = Node('for_loop', '', [p[3], p[6]])
                else:
                    p[0] = Node('for_loop', '', [p[3], p[5]])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN statements 
                    | IF LPAREN expression RPAREN statements ELSE statements
    '''
    if (len(p) == 6):
        p[0] = Node('if_statement', '', [p[3], p[5]])
    else:
        p[0] = Node('if_statement', '', [p[3], p[5], p[7]])

def p_return_statement(p):
    '''return_statement : RETURN expression  
                        | RETURN '''
    match len(p):
        case 2:
            p[0] = Node('return_statement', '', [])
        case 3:
            if (p[2] == ';'):
                p[0] = Node('return_statement', '', [])
            else:
                p[0] = Node('return_statement', '', [p[2]])
        case 4:
            p[0] = Node('return_statement', '', [p[2]])

def p_string_op(p):
    '''string_op_expression : STRING'''
    p[0] = Node('string', p[1], [])

def p_increment_after(p):
    '''increment_after : IDENTIFIER INCREMENT 
                    | GLOBAL_VAR INCREMENT 
                    | IDENTIFIER DECREMENT 
                    | GLOBAL_VAR DECREMENT 
    '''
    p[0] = Node(p[2], p[1], [])

def p_increment_before(p):
    '''increment_before : INCREMENT IDENTIFIER 
                    | INCREMENT GLOBAL_VAR 
                    | DECREMENT IDENTIFIER 
                    | DECREMENT GLOBAL_VAR 
    '''
    p[0] = Node(p[2], p[1], [])

def p_logical_op_expression(p):
    '''logical_op_expression : logical_op_expression AND logical_op_term
                    | logical_op_expression OR logical_op_term
                    | NOT logical_op_term
    '''
    if (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node(p[1], '', [p[2]])

def p_logical_op_term(p):
    '''logical_op_term : logical_op_factor
    '''
    p[0] = Node('logical_op_term', '', [p[1]])

def p_logical_op_factor(p):
    '''logical_op_factor : TRUE
                        | FALSE
    '''
    p[0] = Node('logical_op_factor', '', [p[1]])


def p_binary_cmp_op_expression(p):
    '''binary_expression : binary_expression EQUAL binary_term
                    | binary_expression NOT_EQUAL binary_term
                    | binary_expression GREATER_THAN binary_term
                    | binary_expression LESS_THAN binary_term
                    | binary_expression GREATER_EQUAL binary_term
                    | binary_expression LESS_EQUAL binary_term
    '''
    p[0] = Node(p[2], '', [p[1], p[3]])

def p_binary_op_expression(p):
    '''binary_expression : binary_expression PLUS binary_term
                    | binary_expression MINUS binary_term
                    | MINUS binary_term
                    | binary_term
    '''
    if (len(p) == 3):
        p[0] = Node(p[1], '', [p[2]])
    elif (len(p) == 2):
        p[0] = Node('binary_op_expression', '', [p[1]])
    else:
        p[0] = Node(p[2], '', [p[1], p[3]])

def p_term(p):
    '''binary_term  : binary_term TIMES factor
                        | binary_term DIVIDE factor
                        | factor
    '''
    if (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node('binary_term', '', [p[1]])

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
