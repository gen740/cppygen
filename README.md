# CPPYGEN

Automatic code generation for pybind11.

Pybind11 is a powerful library that exposes C++ types in Python and vice versa, 

This generator will be generate c++ code for pybind11, and make it easy to
write a python module using c++.

## Installation
```
pip install cppygen
```

## Usage Guide

After installing cppygen, you can use `cppygen` command.

```
cppygen --config_file /path/to/cppygenconfig.toml --cwd /path/to/cwd
```

This command will load config file, and parse C++ code and generate
C++ pybind11 Code.

## Config
<!-- TODO -->

## Examples
See the `examples` directry for sample projects.

## Env

```bash
PYGEN_LIBCLANG_PATH # Path to clang shared library
PYGEN_COMPILE_FLAGS # additional flags to parse file
```
