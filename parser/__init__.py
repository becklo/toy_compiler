import ply.yacc as yacc
import utils.history as history

from utils.node import Node

# Get the token map from the lexer.  This is required.
from tokenizer import tokens

# def p_test(p):
#     '''program : statements
#     '''
#     p[0] = Node('program', '', [p[1]])

# Define the grammar rules

def p_program(p):
    '''program : program include
                | include
                | program global_var
                | global_var
                | program function_declaration
                | function_declaration
                | program external_function_declaration
                | external_function_declaration
                | program SEMICOLON
                | SEMICOLON
    '''
    match len(p):
        case 2: 
            if(p[1] == ';'):
                p[0] = Node(';', '', [])
            else:
                p[0] = Node('program', '', [p[1]])
        case 3:
            if(p[2] == ';'):
                p[0] = Node('program', '', [p[1]])
            else:
                p[0] = Node('program', '', [p[1], p[2]])

def p_include(p):
    ''' include : INCLUDE IDENTIFIER
    '''
    p[0] = Node(p[1], p[2], [])

def p_global_var(p):
    '''global_var : TYPE IDENTIFIER
                    | TYPE IDENTIFIER ASSIGN logical_op_expression 
    '''
    if (len(p) == 3):
        p[0] = Node('global_var', [p[1], p[2]], [])
    else:
        p[0] = Node('global_var', [p[1], p[2]], [p[4]])


def p_external_function_declaration(p):
    '''external_function_declaration : DECLARE TYPE IDENTIFIER func_dec_params
    '''
    p[0] = Node('external_function_declaration', [p[2], p[3]], [p[4]])

def p_function_declaration(p):
    '''function_declaration : TYPE IDENTIFIER func_dec_params function_block
    '''
    p[0] = Node('function_declaration', [p[1], p[2]], [p[3], p[4]])

def p_function_block(p):
    '''function_block : scope
    '''
    p[0] = Node('function_block', '', [p[1]])

def p_func_dec_params(p):
    '''func_dec_params : LPAREN dec_parameters RPAREN
                    | LPAREN extended_parameters RPAREN
                    | LPAREN RPAREN
    '''
    if (len(p) == 3):
        p[0] = Node('func_dec_params', '' , [])
    else:
        # p[0] = Node('func_dec_params', '', [p[2]])
        p[0] = p[2]

def p_expend_parameters(p):
    '''extended_parameters : dec_parameters COMMA THREE_DOTS
                        | THREE_DOTS
    '''
    match len(p):
        case 4:
            p[0] = Node('extended_parameters', p[3], [p[1]])
        case 2:
            p[0] = Node('extended_parameters', p[1], [])

def p_dec_parameters(p):
    '''dec_parameters : dec_parameters COMMA dec_parameter
                    | dec_parameter
    '''
    if (len(p) == 2):
        p[0] = Node('dec_parameters', '', [p[1]])
    else:
        p[0] = Node('dec_parameters', '', [p[1], p[3]])

def p_dec_parameter(p):
    '''dec_parameter : TYPE IDENTIFIER
    '''
    p[0] = Node('dec_parameter', [p[1], p[2]], [])

def p_statements(p):
    '''statements : statement
                  | statements statement
    '''
    match len(p):
        case 3:
            p[0] = Node('statements', '', [p[1], p[2]])
        case 2:
            p[0] = Node('statements', '', [p[1]])

def p_statement(p):
    ''' statement : iteration_statement
                    | selection_statement
                    | return_statement
                    | assignment
                    | declaration
                    | logical_statement
                    | SEMICOLON
    '''
    if p[1] == ';':
        p[0] = Node(';', '', [])
    else:
        p[0] = Node('statement', '', [p[1]])

def p_scope(p):
    '''scope : LBRACE statements RBRACE 
                | LBRACE RBRACE
                | statement
    '''
    match len(p):
        case 4:
            p[0] = Node('scope', '', [p[2]])
        case 3:
            p[0] = Node('scope', '', [])
        case 2:
            p[0] = Node('scope', '', [p[1]])

def p_iteration_statement(p):
    '''iteration_statement : while_loop
                        | for_loop
    '''
    p[0] = Node('iteration_statement', '', [p[1]])

def p_selection_statement(p):
    '''selection_statement : if_statement
    '''
    p[0] = Node('selection_statement', '', [p[1]])

def p_logical_statement(p):
    '''logical_statement : logical_op_expression
    '''
    p[0] = Node('logical_statement', '', [p[1]])

def p_expression(p):
    '''expression : increment_postfix_expression
                    | increment_prefix_expression
                    | decrement_postfix_expression
                    | decrement_prefix_expression 
                    | string_op_expression
                    | term
    '''
    p[0] = Node('expression', '', [p[1]])

def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN logical_op_expression 
    '''
    p[0] = Node(p[2], p[1],  [p[3]])

def p_declaration(p):
    '''declaration : TYPE IDENTIFIER 
                    | TYPE IDENTIFIER ASSIGN logical_op_expression 
    '''
    if (len(p) == 3):
        p[0] = Node('declaration', [p[1], p[2]], [])
    else:
        p[0] = Node('declaration', [p[1], p[2]], [p[4]])

def p_while_loop(p):
    '''while_loop : WHILE LPAREN logical_op_expression RPAREN while_block'''
    p[0] = Node('while_loop', '', [p[3], p[5]])

def p_while_block(p):
    '''while_block : scope
    '''
    p[0] = Node('while_block', '', [p[1]])

def p_for_loop(p):
    '''for_loop : FOR LPAREN declaration SEMICOLON logical_op_expression SEMICOLON expression RPAREN for_block 
                    | FOR LPAREN RPAREN for_block 
                    | FOR LPAREN logical_op_expression RPAREN for_block
                    | FOR LPAREN declaration SEMICOLON logical_op_expression RPAREN for_block
                    | FOR LPAREN SEMICOLON SEMICOLON RPAREN for_block

    '''
    match(len(p)):
        case 10:
            p[0] = Node('for_loop', '', [p[3], p[5], p[7], p[9]])
        case 5:
            p[0] = Node('for_loop', '', [p[4]])
        case 6: 
            p[0] = Node('for_loop', '', [p[3], p[5]])
        case 7:
            p[0] = Node('for_loop', '', [p[6]])
        case 8:
            p[0] = Node('for_loop', '', [p[3], p[5], p[7]])

def p_for_block(p):
    '''for_block : scope
    '''
    p[0] = Node('for_block', '', [p[1]])

def p_if_statement(p):
    '''if_statement : IF LPAREN logical_op_expression RPAREN if_block ELSE if_block
                    | IF LPAREN logical_op_expression RPAREN if_block SEMICOLON
    '''
    match len(p):
        case 7:
            p[0] = Node('if_statement', '', [p[3], p[5]])
        case 8:
            p[0] = Node('if_else_statement', '', [p[3], p[5], p[7]])

def p_if_block(p):
    '''if_block : scope
    '''
    p[0] = Node('if_block', '', [p[1]])

def p_return_statement(p):
    '''return_statement : RETURN expression  
                        | RETURN SEMICOLON
    '''
    if (p[2] == ';'):
            p[0] = Node('return_statement', '', [])
    else:
            p[0] = Node('return_statement', '', [p[2]])
        
def p_string_op(p):
    '''string_op_expression : STRING'''
    p[0] = Node('string', p[1], [])

def p_increment_postfix(p):
    '''increment_postfix_expression : INCREMENT_POSTFIX 
    '''
    p[0] = Node('increment_postfix_expression', p[1], [])

def p_decrement_postfix(p):
    '''decrement_postfix_expression : DECREMENT_POSTFIX
    '''
    p[0] = Node('decrement_postfix_expression', p[1], [])

def p_increment_prefix(p):
    '''increment_prefix_expression : INCREMENT_PREFIX
    '''
    p[0] = Node('increment_prefix_expression', p[1], [])

def p_decrement_prefix(p):
    '''decrement_prefix_expression :  DECREMENT_PREFIX 
    '''
    p[0] = Node('decrement_prefix_expression', p[1], [])

def p_logical_op_expression(p):
    '''logical_op_expression : logical_op_expression AND logical_op_term
                    | logical_op_term
    '''
    if (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node('logical_op_expression', '', [p[1]])

def p_logical_op_term(p):
    '''logical_op_term : logical_op_term OR logical_factor
                        | logical_factor
    '''
    if (len(p) == 4):
        p[0] = Node(p[2], '', [p[1], p[3]])
    else:
        p[0] = Node('logical_op_term', '', [p[1]])

def p_logical_op_not(p):
    '''logical_op_term : NOT logical_factor
    '''
    p[0] = Node('logical_op_not', '', [p[2]])

def p_logical_op_factor(p):
    '''logical_factor : TRUE
                | FALSE
    '''
    p[0] = Node('logical_op_factor', p[1], [])

def p_logical_factor_expression(p):
    '''logical_factor : expression'''
    p[0] = Node('logical_factor', '', [p[1]])

def p_binary_cmp_op_expression(p):
    '''logical_op_expression : expression EQUAL term
                    | expression NOT_EQUAL term
                    | expression GREATER_THAN term
                    | expression LESS_THAN term
                    | expression GREATER_EQUAL term
                    | expression LESS_EQUAL term
    '''
    p[0] = Node(p[2], '', [p[1], p[3]])
    

def p_binary_op_expression(p):
    '''expression : expression PLUS term
                    | expression MINUS term
    '''
    p[0] = Node(p[2], '', [p[1], p[3]])

def p_binary_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor
    '''
    p[0] = Node(p[2], '', [p[1], p[3]])

def p_term(p):
    '''term : factor'''
    p[0] = Node('term', '', [p[1]])

def p_factor_int(p):
    '''factor : INTEGER'''
    p[0] = Node('int', p[1], [])

def p_factor_float(p):
    '''factor : FLOAT'''
    p[0] = Node('float', p[1], [])

# def p_factor_inverse_int(p):
#     '''factor : MINUS INTEGER'''
#     p[0] = Node('int', -p[2], [])

# def p_factor_inverse_float(p):
#     '''factor : MINUS FLOAT'''
#     p[0] = Node('float', -p[2], [])

def p_variable(p):
    '''factor : IDENTIFIER'''
    p[0] = Node('var', p[1], [])

def p_func_call(p):
    '''factor : IDENTIFIER LPAREN func_call_args RPAREN
                  | IDENTIFIER LPAREN RPAREN  
    '''
    if (len(p) == 4):
        p[0] = Node('func_call', p[1], [])
    else:
        p[0] = Node('func_call', p[1], [p[3]])
             
def p_func_call_args(p):
    '''func_call_args : func_call_arg
                    | func_call_args COMMA func_call_arg
    '''
    if (len(p) == 2):
        p[0] = Node('func_call_args', '', [p[1]])
    else:
        p[0] = Node('func_call_args', '', [p[1], p[3]])

def p_func_call_arg(p):
    '''func_call_arg : expression
    '''
    p[0] = Node('func_call_arg','', [p[1]])

# def p_factor_paren(p):
#     '''factor : LPAREN expression RPAREN'''
#     p[0] = Node('factor_paren', '', [p[2]])

# def p_factor_brace(p):
#     '''factor : LBRACE expression RBRACE'''
#     p[0] = Node('factor_brace', '', [p[2]])

# Error rule for syntax errors
def p_error(p):
    raise Exception("Syntax error in input!")

# Build the parser
parser = yacc.yacc()


def main():
    while True:
        try:
            s = input('parser > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        print(result)

if __name__ == '__main__':
    main()
