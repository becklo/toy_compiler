from parser import parser, pretty_print
import readline

def compile(name, code):
    ast = parser.parse(code)

    from llvmlite import ir
    from llvmlite import binding as llvm

    llvm.initialize()
    tripple = llvm.get_default_triple()

    # Create an empty module..
    module = ir.Module(name=__file__)
    module.triple = tripple
    func = ir.Function(module, ir.FunctionType(ir.IntType(32), ()), name="_start")

    # Now implement the function
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    def compile_ast(ast):
        match ast.type:
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
                result = compile_ast(ast.children[0])
                builder.ret(result)
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
            s = input('calc > ')
        except EOFError:
            break
        if not s: continue
        compile("calc", s)

if __name__ == "__main__":
    main()
