# Toy compiler

## Installation

### VSCode DevContainer

Using VSCode devcontainer (requires only docker pre-installed and vscode with devcontainer extensions enabled).
- Open the command palette (CTRL+SHIFT+P) and select `Dev Container: Open Workspace in Container` or `Dev Container: Open Folder in Container`. This shall reopen the environment in container mode with all the dependencies automatically installed.
- Wait for the container to be built and then you can run the apps as described below.

### Poetry virtual environment

The following dependencies are required:
- python3-poetry 
- llvm 
- clang 
- python-is-python3 
- graphviz

The rest of the dependencies will be installed by Poetry by running `poetry install` in the root directory. Then you can activate the virtual environment by running `poetry shell`.

## Structure

- **tokenizer** - Tokenizer for the toy language, using PLY (Python Lex-Yacc)
- **parser** - Parser for the toy language, using PLY (Python Lex-Yacc). Generates an AST (Abstract Syntax Tree)
- **compiler** - Translates the AST into machine code (assembly) using llvmlite, a python wrapper for LLVM (Low Level Virtual Machine)
- **test** - Test cases for the compiler

## Running the apps 

This project is using poetry to manage the dependencies and virtual environment. 
To run the tokenizer, parser, and compiler, you can use the following commands, and provide inputs:

```
poetry run token
poetry run parser
poetry run compiler
```

To run the test cases, you can use the following command:

```
poetry run test 
```