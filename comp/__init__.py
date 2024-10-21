
def main():
    """
    This file demonstrates a trivial function "fpadd" returning the sum of
    two floating-point numbers.
    """

    from llvmlite import ir
    from llvmlite import binding as llvm

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    tripple = llvm.Target.from_default_triple()

    # Create an empty module..
    module = ir.Module(name=__file__)
    module.triple = tripple.triple
    # and declare a function named "fpadd" inside it
    func = ir.Function(module, ir.FunctionType(ir.IntType(32), (ir.IntType(32), ir.IntType(32))), name="main")

    # Now implement the function
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    a, b = func.args
    result = builder.add(a, b, name="res")
    builder.ret(result)

    # Print the module IR
    print(module)

if __name__ == "__main__":
    main()
