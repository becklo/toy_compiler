import subprocess
import os

from ctypes import CFUNCTYPE, c_int

import llvmlite.binding as llvm

from compiler import compile

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine

def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    engine.run_static_constructors()
    return mod

def main():
    # All these initializations are required for code generation!
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()  # yes, even this one

    input_path = os.path.join(os.path.dirname(__file__), 'input/valid')
    # expected_output_path = os.path.join(os.path.dirname(__file__), 'expected_output')
    for filename in os.listdir(input_path):
        input_file = os.path.join(input_path, filename)
        print(input_file)

        try:
            llvm_ir = compile(f'{input_file}.out',open(input_file).read())
            engine = create_execution_engine()
            mod = compile_ir(engine, llvm_ir)

            # Look up the function pointer (a Python int)
            func_ptr = engine.get_function_address("main")

            # Run the function via ctypes
            # TODO: make this dependent on the test case
            cfunc = CFUNCTYPE(c_int)(func_ptr)
            res = cfunc()
            print("main(...) =", res)
            # assert res == 'expected_output'
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()