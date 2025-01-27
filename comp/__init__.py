from parser import parser
import readline

func = None
block = None
builder = None
func_args = None

scoped_definition = dict()
scope_level = 0 # one scope for now, until scope is implemented

mydict = dict()
mydict[scope_level] = scoped_definition


def compile(name, code):
    ast = parser.parse(code)

    from llvmlite import ir
    from llvmlite import binding as llvm

    llvm.initialize()
    tripple = llvm.get_default_triple()

    # Create an empty module..
    module = ir.Module(name=__file__)
    module.triple = tripple

    def compile_ast(ast):
        global func, block, builder, func_args
        func_args = ()
        match ast.type:
            case "program":
                func = ir.Function(module, ir.FunctionType(ir.IntType(32), ()), name="main")
                block = func.append_basic_block()
                builder = ir.IRBuilder(block)
                builder.ret(compile_ast(ast.children[0]))  
            case "statements":
                for statement in ast.children:
                    compile_ast(statement)
            case "statement":
                # TODO: handle SEMICOLON
                return compile_ast(ast.children[0])
            case "declaration":
                if len(ast.children) > 0:
                    value = compile_ast(ast.children[0])
                    mydict[scope_level][ast.value[1]] = {"type": ast.value[0], "value" : value[1]}
                else: 
                   # if not set, save as 0 ? 
                    mydict[scope_level][ast.value[1]] = {"type": ast.value[0], "value" : 0}
            case "expression":
                return compile_ast(ast.children[0])
            case "term":
                return compile_ast(ast.children[0])
            case "logical_statement":
                return compile_ast(ast.children[0])
            case "logical_op_expression":
                for statement in ast.children:
                    compile_ast(statement)
            case "logical_op_term":
                return compile_ast(ast.children[0])
            case "logical_factor":
                if ast.value == "TRUE":
                    return (int, ir.Constant(ir.IntType(32), 1))
                elif ast.value == "FALSE":
                    return (int, ir.Constant(ir.IntType(32), 0))
                else:
                    return compile_ast(ast.children[0])
            case "+":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int and rparm[0] is int):
                    return (int, builder.add(lparm[1], rparm[1]))
                if (lparm[0] is float and rparm[0] is float):
                    return (float, builder.fadd(lparm[1], rparm[1]))
                raise ValueError(f"Cannot add {lparm} and {rparm}")
            case "-":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int and rparm[0] is int):
                    return (int, builder.sub(lparm[1], rparm[1]))
                if (lparm[0] is float and rparm[0] is float):
                    return (float, builder.fsub(lparm[1], rparm[1]))
                raise ValueError(f"Cannot sub {lparm} and {rparm}")
            case "*":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int and rparm[0] is int):
                    return (int, builder.mul(lparm[1], rparm[1]))
                if (lparm[0] is float and rparm[0] is float):
                    return (float, builder.fmul(lparm[1], rparm[1]))
                raise ValueError(f"Cannot mul {lparm} and {rparm}")
            case "/":
                lparm = compile_ast(ast.children[0])
                rparm = compile_ast(ast.children[1])
                if (lparm[0] is int and rparm[0] is int):
                    return (int, builder.sdiv(lparm[1], rparm[1]))
                if (lparm[0] is float and rparm[0] is float):
                    return (float, builder.fdiv(lparm[1], rparm[1]))
                raise ValueError(f"Cannot div {lparm} and {rparm}")
            case ";":
                return
            case "int":
                return (int, ir.Constant(ir.IntType(32), int(ast.value)))
            case "var":
                # TODO: handle scope
                definition = mydict[scope_level].get(ast.value[0])
                if definition is None:
                    raise ValueError(f"Undefined variable: {ast.value[0]}")
                value = definition.get("value")
                type_name = definition.get("type")
                
                match type_name:
                    case "int":
                        type = ir.IntType(32)
                        return_type = int
                    case "float":
                        type = ir.FloatType()          
                        return_type = float
                var = builder.alloca(type, name=ast.value[0])
                builder.store(value, var)
                return (return_type, builder.load(var))
            case "global_var":
                lparm = compile_ast(ast.children[0])
                var = ir.GlobalVariable(module, lparm[0], name=ast.value)
                var.initializer = ir.Constant(lparm[0], 0)
                return builder.load(var)
            case "func_call":
                func_name = ast.value
                func_args = ()
                func_args_type = ()
                for arg in ast.children:
                    current_arg = compile_ast(arg)
                    func_args_type = func_args_type + (current_arg[0],)
                    func_args = func_args + (current_arg[1],)
                func_type = ir.FunctionType(ir.IntType(32), func_args_type) 
                func_call = ir.Function(module, func_type, name=func_name)
                block = func_call.append_basic_block()
                builder = ir.IRBuilder(block)
                return builder.call(func_call, func_args)
            case "func_call_args":
                if len(ast.children) == 1:
                    return compile_ast(ast.children[0])
                else:
                    return (compile_ast(ast.children[0]),) + compile_ast(ast.children[1])
            case "func_call_arg":
                return compile_ast(ast.children[0])
            # return compile_ast(ast.children[0])
            # case "function_def":
            #     if ast.value[0] == 'int':
            #         func = ir.Function(module, ir.FunctionType(ir.IntType(32), func_args), name=ast.value[1])
            #     elif ast.value[0] == 'float':
            #         func = ir.Function(module, ir.FunctionType(ir.FloatType(), func_args), name=ast.value[1])
            #     else:
            #         raise ValueError(f"Unknown function type: {ast.value[0]}")
            #     block = func.append_basic_block()
            #     builder = ir.IRBuilder(block)
            #     if len(ast.children) > 1:
            #         compile_ast(ast.children[0])
            #         builder.ret(compile_ast(ast.children[1]))
            #     else:
            #         builder.ret(compile_ast(ast.children[0]))
            # case "scope":
            #     return compile_ast(ast.children[0])
            # case "assign":
            #     var = builder.alloca(ir.IntType(32), name=ast.value)
            #     builder.store(compile_ast(ast.children[0]), var)
            #     return builder.load(var)
            # case "statements":
            #     if ast.value == ';':
            #         compile_ast(ast.children[0])
            #         return compile_ast(ast.children[1])
            #     else:
            #         return compile_ast(ast.children[0])
            # case "statement":
            #     return compile_ast(ast.children[0])
            # case "expression":
            #     return compile_ast(ast.children[0])
            # case "params":
            #     print(ast.value)
            #     if ast.value == ',':
            #         compile_ast(ast.children[0]) # not sure if that is the way
            #         return compile_ast(ast.children[1])
            #     else: 
            #         return compile_ast(ast.children[0])
            # case "int":
            #     if len(ast.children) == 0:
            #         func.args = func.args + (ir.IntType(32),)
            #     else:
            #         return compile_ast(ast.children[0])
            # case "int_factor":
            #     if len(ast.children) == 0:
            #         if isinstance(ast.value, int):
            #             return ir.Constant(ir.IntType(32), int(ast.value))
            #         else:
            #             var = builder.alloca(ir.IntType(32), name=ast.value)
            #             return builder.load(var)
            #     else:
            #         return compile_ast(ast.children[0])
            # case "int_term":
            #     if ast.value == '':
            #         return compile_ast(ast.children[0])
            #     if ast.value == '*':
            #         return builder.mul(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            #     if ast.value == '/':
            #         return builder.sdiv(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            # case "int_expression":
            #     if ast.value == '':
            #         return compile_ast(ast.children[0])
            #     if ast.value == '+':
            #         return builder.add(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            #     if ast.value == '-':
            #         return builder.sub(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            # case "float":
            #     if len(ast.children) == 0:
            #         func.args = func.args + (ir.FloatType(),)
            #     else:
            #         return compile_ast(ast.children[0])
            # case "float_factor":
            #     if len(ast.children) == 0:
            #         # cannot be a variable for now, so no need to handle it
            #         return ir.Constant(ir.FloatType(), float(ast.value))
            #     else:
            #         return compile_ast(ast.children[0])
            # case "float_term":
            #     if ast.value == '':
            #         return compile_ast(ast.children[0])
            #     if ast.value == '*':
            #         return builder.fmul(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            #     if ast.value == '/':
            #         return builder.fdiv(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            # case "float_expression":
            #     if ast.value == '':
            #         return compile_ast(ast.children[0])
            #     if ast.value == '+':
            #         return builder.fadd(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            #     if ast.value == '-':
            #         return builder.fsub(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            case _:
                raise ValueError(f"Unknown AST node type: {ast.type}")

    print(ast)
    compile_ast(ast)
    # Print the module IR
    print(module)
    with open(f"{name}.ll", "w") as f:
        f.write(str(module))


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
