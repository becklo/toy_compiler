from parser import parser, pretty_print
import readline

func = None
block = None
builder = None

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
        global func, block, builder
        match ast.type:
            case "function_def":
                func = ir.Function(module, ir.FunctionType(ir.IntType(32), ()), name=ast.value)
                block = func.append_basic_block()
                builder = ir.IRBuilder(block)
                builder.ret(compile_ast(ast.children[0]))
            case "assign":
                var = builder.alloca(ir.IntType(32), name=ast.value)
                builder.store(compile_ast(ast.children[0]), var)
                return builder.load(var)
            case "factor":
                if len(ast.children) == 0:
                    return ir.Constant(ir.IntType(32), int(ast.value))
                else:
                    return compile_ast(ast.children[0])
            case "term":
                if ast.value == '':
                    return compile_ast(ast.children[0])
                if ast.value == '*':
                    return builder.mul(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
                if ast.value == '/':
                    return builder.sdiv(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            case "expression":
                if ast.value == '':
                    return compile_ast(ast.children[0])
                if ast.value == '+':
                    return builder.add(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
                if ast.value == '-':
                    return builder.sub(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            case "f_factor":
                if len(ast.children) == 0:
                    return ir.Constant(ir.FloatType(), float(ast.value))
                else:
                    return compile_ast(ast.children[0])
            case "f_term":
                if ast.value == '':
                    return compile_ast(ast.children[0])
                if ast.value == '*':
                    return builder.fmul(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
                if ast.value == '/':
                    return builder.fdiv(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            case "f_exp":
                if ast.value == '':
                    return compile_ast(ast.children[0])
                if ast.value == '+':
                    return builder.fadd(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
                if ast.value == '-':
                    return builder.fsub(compile_ast(ast.children[0]), compile_ast(ast.children[1]))
            case "x_expression":
                return compile_ast(ast.children[0])
            case "statement":
                return compile_ast(ast.children[0])
            case _:
                raise ValueError(f"Unknown AST node type: {ast.type}")

    compile_ast(ast)
    # Print the module IR
    print(pretty_print(ast))
    print(module)
    with open(f"{name}.ll", "w") as f:
        f.write(str(module))


def main():
    """
    This file demonstrates a trivial function "fpadd" returning the sum of
    two floating-point numbers.
    """
    while True:
        try:
            s = input('compiler > ')
        except EOFError:
            break
        if not s: continue
        compile("calc", s)

if __name__ == "__main__":
    main()
