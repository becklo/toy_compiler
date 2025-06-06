from parser import parser
from utils.scoped_dict import ScopedDict
import readline


func = None
block = None
builder = None
func_args = None

mydict_var = ScopedDict()
mydict_func = ScopedDict()

def compile(name, code):
    ast = parser.parse(code)

    from llvmlite import ir
    from llvmlite import binding as llvm

    def helper_get_type(type_str):
        match type_str:
            case "int":
                return ir.IntType(32)
            case "float":
                return ir.FloatType()
            case "str":
                return ir.PointerType(ir.IntType(8))
            case _:
                raise ValueError(f"Unknown type: {type_str}")

    llvm.initialize()
    tripple = llvm.get_default_triple()

    # Create an empty module..
    module = ir.Module(name=__file__)
    module.triple = tripple

    def compile_ast(ast):
        global func, block, builder, func_args, mydict_var, mydict_func
        func_args = ()
        match ast.type:
            case "program":
                return [compile_ast(x) for x in ast.children][-1] if len(ast.children)>0 else (0,0)
            case "include":
                # TODO: handle include
                raise NotImplementedError("Include not implemented")
            case "global_var":
                match ast.value[0]:
                    case "int":
                        type, return_type = ir.IntType(32), int
                    case "float":
                        type, return_type = ir.FloatType(), float
                    case "str":
                        type, return_type = ir.PointerType(ir.IntType(8)), str
                    case _:
                        raise ValueError(f"Unknown type: {ast.value[0]}")
                if len(ast.children) > 0:
                    value = compile_ast(ast.children[0])
                    if ast.value[0] == "str":
                        type = ir.ArrayType(ir.IntType(8), value[-1])
                else: 
                   # not set, put 0 as default value
                   value = (return_type, ir.Constant(type, 0))
                if mydict_var.in_scope(ast.value[1]):
                    raise ValueError(f"Variable {ast.value[1]} already defined in this scope")
                var = ir.GlobalVariable(module, type, name=ast.value[1])
                var.initializer = value[1]
                mydict_var[ast.value[1]] = {"type": return_type, "value" : value, "var" : var}
                return (return_type, var)
            case "external_function_declaration":
                func_args = compile_ast(ast.children[0])
                func_args_type = ()
                if func_args != ():
                    for i in range(0, len(func_args), 2):
                        func_args_type = func_args_type + (helper_get_type(func_args[i]),)
                func_t = ir.FunctionType(helper_get_type(ast.value[0]), func_args_type) 
                func_def = ir.Function(module, func_t, name=ast.value[1])
                mydict_func[ast.value[1]] = {"type": ast.value[0], "arg" : func_args, "func": func_def, "is_extended": False}
                return (ast.value[0], func_def)
            case "function_declaration":
                func_args = compile_ast(ast.children[0])
                func_args_type = ()
                if not func_args[1]: # not extended
                    if func_args[0] != ():
                        for i in range(0, len(func_args[0]), 2):
                            func_args_type = func_args_type + (helper_get_type(func_args[0][i]),)
                    func_t = ir.FunctionType(helper_get_type(ast.value[0]), func_args_type) 
                    func_def = ir.Function(module, func_t, name=ast.value[1])
                    mydict_func[ast.value[1]] = {"type": ast.value[0], "arg" : func_args[0], "func": func_def, "is_extended": func_args[1]}
                    # pass function name to children i.e. fonction block
                    ast.children[1].value = ast.value[1]
                    return compile_ast(ast.children[1])
                else: # extended function, will be defined during function call
                    mydict_func[ast.value[1]] = {"type": ast.value[0], "arg" : func_args[0], "is_extended": func_args[1]}
                    return 0
            case "function_block":
                definition = mydict_func[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined function: {ast.value}")
                func = definition.get("func")
                block = func.append_basic_block()
                builder = ir.IRBuilder(block)
                return_value = compile_ast(ast.children[0])
                #TODO: update to support return, i.e. return_statement
                # example: 
                # int f() {1}; int main(){f(); return 1}  OK
                # int f() {1}; int main(){f(); 1} OK 
                # int f() {1}; int main(){f(); return 1; 2} NOT OK
                # if return_value[-1].__class__ is not ir.Ret:
                try:
                    builder.ret(return_value[-1])
                except AssertionError:
                    pass
                return return_value
            case "func_dec_params":
                if ast.value == '':
                    return ((), False)
                return (compile_ast(ast.children[0]), False)
            case "extended_parameters":
                if len(ast.children) == 0:
                    return ((), True)
                return (compile_ast(ast.children[0]), True)
            case "dec_parameters":
                if len(ast.children) == 1:
                    return compile_ast(ast.children[0])
                return compile_ast(ast.children[0]) + compile_ast(ast.children[1])
            case "dec_parameter":
                return (ast.value[0], ast.value[1])
            case "statements":
                if len(ast.children) == 1 or (len(ast.children) == 2 and ast.children[1].type == ";"):
                    return compile_ast(ast.children[0])
                compile_ast(ast.children[0])
                return compile_ast(ast.children[1])
            case "statement":
                return compile_ast(ast.children[0])
            case "scope":
                if len(ast.children) == 1: 
                    mydict_func.__push__()
                    mydict_var.__push__()
                    v = compile_ast(ast.children[0])
                    mydict_func.__pop__()
                    mydict_var.__pop__()
                    return v
                return (None, ir.Constant(ir.IntType(32),0))
            case "iteration_statement":
                return compile_ast(ast.children[0])
            case "selection_statement":
                return compile_ast(ast.children[0])
            case "logical_statement":
                 return compile_ast(ast.children[0])
            case "expression":
                return compile_ast(ast.children[0])
            case "=":
                definition = mydict_var[ast.value[0]]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value[0]}")
                var = definition.get("var")
                value = compile_ast(ast.children[0])
                if value[0] != definition.get("type"):
                    raise ValueError(f"Cannot assign {value[0]} to {definition.get('type')}")
                builder.store(value[1], var)
                mydict_var[ast.value[0]] = {"type": value[0], "value" : value, "var" : var}
                return value
            case "declaration":
                match ast.value[0]:
                    case "int":
                        type, return_type = ir.IntType(32), int
                    case "float":
                        type, return_type = ir.FloatType(), float
                    case "str":
                        type, return_type = ir.PointerType(ir.IntType(8)), str
                    case _:
                        raise ValueError(f"Unknown type: {ast.value[0]}")
                if len(ast.children) > 0:
                    value = compile_ast(ast.children[0])
                    if value[0] == str:
                        type = ir.ArrayType(ir.IntType(8), value[-1])
                    # implicity cast to declared type
                    if value[0] != return_type:
                        match type:
                            case ir.IntType():
                                value = (return_type, builder.fptosi(rparm[1], ir.IntType(32)))
                            case ir.FloatType():
                                value = (return_type, builder.sitofp(value[1], ir.FloatType()))
                            # no implicit cast from str to int/float or back
                            case _:
                                raise ValueError(f"Cannot implicit cast type: {value[0]} to: {return_type}")
                else: 
                   # not set, put 0 as default value
                   value = (return_type, ir.Constant(type, 0))
                if mydict_var.in_scope(ast.value[1]):
                    raise ValueError(f"Variable {ast.value[1]} already defined in this scope")
                var = builder.alloca(type, name=ast.value[1])
                builder.store(value[1], var)
                mydict_var[ast.value[1]] = {"type": return_type, "value" : value, "var" : var}
                return (return_type, value[1])
            case "while_loop":
                loophead = builder.function.append_basic_block('while.loop.header')
                loopbody = builder.function.append_basic_block('while.loop.body')
                loopend = builder.function.append_basic_block('while.loop.end')

                builder.branch(loophead)
                builder.position_at_end(loophead)
                cond = compile_ast(ast.children[0])
                builder.cbranch(cond[1], loopbody, loopend)

                builder.position_at_end(loopbody)
                # while_block
                while_block = compile_ast(ast.children[-1])
                builder.branch(loophead)
                builder.position_at_end(loopend)
                return (while_block[0], builder.ret(while_block[1]))
            case "while_block":
                return compile_ast(ast.children[0])
            case "for_loop":
                # LOOP START
                # [optional] init
                # cond 
                # loop_entry
                # for_block
                # [optional] iter
                # cond : if true go to loop_entry, else go to loop_exit
                # loop_exit
                # LOOP END

                if (len(ast.children)) == 3 or (len(ast.children)) == 4:
                    # for (init; cond; iter;)
                    # for (init; cond;)
                    init = compile_ast(ast.children[0])

                loophead = builder.function.append_basic_block('for.loop.header')
                loopbody = builder.function.append_basic_block('for.loop.body')
                loopend = builder.function.append_basic_block('for.loop.end')

                builder.branch(loophead)
                builder.position_at_end(loophead)
                # cond
                match(len(ast.children)):
                    case 1:
                        # for () or for (;;) 
                        cond = (int ,ir.Constant(ir.IntType(32), 1))
                    case 2:
                        # for (iter;)
                        # todo: handle iter
                        raise NotImplementedError("Iter not implemented")
                    case 3:
                        # for (init; cond;)
                        cond = compile_ast(ast.children[1])
                    case 4:
                        # for (init; cond; iter;)
                        cond = compile_ast(ast.children[1])
                builder.cbranch(cond[1], loopbody, loopend)

                builder.position_at_end(loopbody)
                # for_block
                for_block = compile_ast(ast.children[-1])

                # [optional] iter
                if len(ast.children) == 4 or len(ast.children) == 2:
                    iter = compile_ast(ast.children[-2])

                builder.branch(loophead)
                builder.position_at_end(loopend)
                return (for_block[0], builder.ret(for_block[1]))
            case "for_block":
                return compile_ast(ast.children[0])
            case "if_statement":
                pred = compile_ast(ast.children[0])
                with builder.if_then(pred[1]):
                    if_block = compile_ast(ast.children[1])
                out_phi = builder.phi(ir.IntType(32))
                out_phi.add_incoming(if_block[1][1], if_block[0])
                return (if_block[1][0], builder.ret(out_phi)) 
            case "if_else_statement":
                pred = compile_ast(ast.children[0])
                with builder.if_else(pred[1]) as (then, otherwise):
                    with then:
                        if_block = compile_ast(ast.children[1])
                    with otherwise:
                        else_block = compile_ast(ast.children[2])
                out_phi = builder.phi(ir.IntType(32))
                out_phi.add_incoming(if_block[1][1], if_block[0])
                out_phi.add_incoming(else_block[1][1], else_block[0])
                return (if_block[1][0], builder.ret(out_phi))
            case "if_block":
                bb = builder.basic_block
                out_then = compile_ast(ast.children[0])
                return bb, out_then
            case "return_statement":
                return_value = compile_ast(ast.children[0])
                ret = builder.ret(return_value[1])
                return (return_value, ret)
            case "string":
                return (str, ir.Constant(ir.ArrayType(ir.IntType(8), len(ast.value)), bytearray(ast.value, encoding='utf8')), len(ast.value))
            case "increment_postfix_expression":
                definition = mydict_var[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value}")
                type, var = definition.get("type"), definition.get("var")
                r = builder.load(var)
                n = builder.add(r,ir.Constant(ir.IntType(32),1))
                builder.store(n, var)
                return (type, r)
            case "decrement_postfix_expression":
                definition = mydict_var[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value}")
                type, var =  definition.get("type"), definition.get("var")
                r = builder.load(var)
                n = builder.sub(r,ir.Constant(ir.IntType(32),1))
                builder.store(n, var)
                return (type, r)
            case "increment_prefix_expression":
                definition = mydict_var[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value}")
                type, var = definition.get("type"), definition.get("var")
                n = builder.add(ir.Constant(ir.IntType(32),1),builder.load(var))
                builder.store(n, var)
                return (type, builder.load(var))
            case "decrement_prefix_expression":
                definition = mydict_var[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value}")
                type, var = definition.get("type"), definition.get("var")
                n = builder.sub(ir.Constant(ir.IntType(32),1),builder.load(var))
                builder.store(n, var)
                return (type, builder.load(var))
            case "logical_op_expression":
                return compile_ast(ast.children[0])
            case "and":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])

                if lparm[1].__class__ is not ir.Constant: 
                    definition = mydict_var[lparm[-1]]
                    if definition is None:
                        raise ValueError(f"Undefined variable: {lparam[-1]}")
                    l_value = definition.get("value")
                else: 
                    l_value = lparm[1].constant

                if rparm[1].__class__ is not ir.Constant: 
                    definition = mydict_var[rparm[-1]]
                    if definition is None:
                        raise ValueError(f"Undefined variable: {rparm[-1]}")
                    r_value = definition.get("value")
                else: 
                    r_value = rparm[1].constant
                if ((lparm[0] is int and l_value != 0) and ((rparm[0] is int and r_value != 0))):
                    return (int, ir.Constant(ir.IntType(32), 1))
                else:
                    return (int, ir.Constant(ir.IntType(32), 0))
            case "logical_op_term":
                return compile_ast(ast.children[0])
            case "or": 
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])

                if lparm[1].__class__ is not ir.Constant: 
                    definition = mydict_var[lparm[-1]]
                    if definition is None:
                        raise ValueError(f"Undefined variable: {lparam[-1]}")
                    l_value = definition.get("value")
                else: 
                    l_value = lparm[1].constant

                if rparm[1].__class__ is not ir.Constant: 
                    definition = mydict_var[rparm[-1]]
                    if definition is None:
                        raise ValueError(f"Undefined variable: {rparm[-1]}")
                    r_value = definition.get("value")
                else: 
                    r_value = rparm[1].constant
                if ((lparm[0] is int and l_value != 0) or ((rparm[0] is int and r_value != 0))):
                    return (int, ir.Constant(ir.IntType(32), 1))
                else:
                    return (int, ir.Constant(ir.IntType(32), 0))
            case "logical_op_not":
                # TODO: handle logical op not
                raise NotImplementedError("Logical op not not implemented")
            case "logical_op_factor":
                if ast.value.lower() == "true":
                    return (int, ir.Constant(ir.IntType(32), 1))
                elif ast.value.lower() == "false":
                    return (int, ir.Constant(ir.IntType(32), 0))
                else:
                    raise ValueError("Unknown logical factor")
            case "logical_factor":
                return compile_ast(ast.children[0])
            case "==":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('==', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('==', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case "!=":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int ):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('!=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('!=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case ">":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int ):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('>', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('>', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case "<":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('<', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('<', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case ">=":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('>=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('>=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case "<=":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.icmp_signed('<=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fcmp_unordered('<=', lparm[1], rparm[1]))
                    raise ValueError(f"Cannot compare {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for comparison: {lparm[0]} and {rparm[1]}")
            case "+":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.add(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot add {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fadd(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot add {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for addition: {lparm[0]} and {rparm[1]}")
            case "-":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.sub(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot sub {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, ir.Constant(ir.FloatType(), float(rparm[1].constant)))
                    if (rparm[0] is float):
                        return (float, builder.fsub(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot sub {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for subtraction: {lparm[0]} and {rparm[1]}")       
            case "*":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if (rparm[0] is float):
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.mul(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot mul {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fmul(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot mul {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for multiplication: {lparm[0]} and {rparm[1]}")
            case "/":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int):
                    # implicit conversion to int
                    if rparm[0] is float:
                        rparm = (int, builder.fptosi(rparm[1], ir.IntType(32)))
                    if (rparm[0] is int):
                        return (int, builder.sdiv(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot div {lparm} and {rparm}")
                if (lparm[0] is float):
                    # implicit conversion to float
                    if (rparm[0] is int):
                        rparm = (float, builder.sitofp(rparm[1], ir.FloatType()))
                    if (rparm[0] is float):
                        return (float, builder.fdiv(lparm[1], rparm[1]))
                    raise ValueError(f"Cannot div {lparm} and {rparm}")
                raise ValueError(f"Unsupported type for division: {lparm[0]} and {rparm[1]}")
            case "term":
                return compile_ast(ast.children[0])
            case "int":
                return (int, ir.Constant(ir.IntType(32), int(ast.value)))
            case "float":
                return (float, ir.Constant(ir.FloatType(), float(ast.value)))
            case "var":
                definition = mydict_var[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value}")
                value, return_type, var = definition.get("value"), definition.get("type"), definition.get("var")
                # print(return_type, builder.load(var), ast.value)
                # breakpoint()
                return (return_type, builder.load(var))
            case "func_call":             
                definition = mydict_func[ast.value]
                if definition is None:
                    raise ValueError(f"Undefined function: {ast.value}")
                if definition.get("is_extended"):
                    # define function during call
                    func_args_type = ()
                    func_args_call = compile_ast(ast.children[0])
                    func_args_def = definition.get("args")
                    if func_args_call == ():
                        raise ValueError(f"Function {ast.value} requires at least one argument")
                    if func_args_type != ():
                        for i in range(0, len(func_args_call), 2):
                            # make sure the types match
                            if (i < len(func_args_def) and func_args_call[i] != func_args_def[i]):
                                raise ValueError(f"Type mismatch in argument {i+1} of function {ast.value}")
                            func_args_type = func_args_type + (helper_get_type(func_args_def[i]),)
                    func_type = definition.get("type")
                    func_t = ir.FunctionType(helper_get_type(func_type), func_args_type) 
                    func_def = ir.Function(module, func_t, name=ast.value)
                else:
                    func_def = definition.get("func")
                func_type = definition.get("type")
                func_args = ()
                func_arg_list = []
                if len(ast.children) > 0:
                    func_args = compile_ast(ast.children[0])
                for i in range(1, len(func_args), 2):
                    func_arg_list.append(func_args[i]) 
                return (func_type, builder.call(func_def, func_arg_list))
            case "func_call_args":
                if len(ast.children) == 1:
                    return compile_ast(ast.children[0])
                else:
                    return compile_ast(ast.children[0]) + compile_ast(ast.children[1])
            case "func_call_arg":
                return compile_ast(ast.children[0])
            case ";":
                return
            case _:
                raise ValueError(f"Unknown AST node type: {ast.type}")

    print(ast)
    compile_ast(ast)
    # Print the module IR
    print(module)
    # clean scope definition to avoid conflicts
    mydict_var.clear()
    mydict_func.clear()
    with open(f"{name}.ll", "w") as f:
        f.write(str(module))

    return str(module)

def main():
    while True:
        try:
            s = input('compiler > ')
        except EOFError:
            break
        if not s: continue
        compile("calc", s)

if __name__ == "__main__":
    main()
