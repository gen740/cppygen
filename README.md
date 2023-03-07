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
cppygen --config_file /path/to/cppygenconfig.toml --cwd /path/to/cwd [--verbose] [--include_directories INCLUDE_DIRECTORIES] [--flags FLAGS]
```

This command will load config file, and parse C++ code and generate
C++ pybind11 Code.

After generating the code. Include the generated header to your program and
just write in pybind11 manner. Be sure to link the generated cpp code.

```cpp
PYBIND11_MODULE(pyshell, m) {
  CPPyGen::CPPyGenExport(m);
}
```

### CMake

Use `add_custom_command` to auto generate.

```cmake
set(cppygen_generated_hpp ${CMAKE_CURRENT_BINARY_DIR}/cppygen_generated.hpp)
set(cppygen_generated_cpp ${CMAKE_CURRENT_BINARY_DIR}/cppygen_generated.cpp)

find_program(_CPPYGEN_GENERATOR cppygen)

add_custom_command(
  OUTPUT ${cppygen_generated_hpp} ${cppygen_generated_cpp}
  COMMAND
    ${_CPPYGEN_GENERATOR} ARGS #
    --config_file ${CMAKE_CURRENT_LIST_DIR}/cppygenconfig.toml #
    --cwd ${CMAKE_CURRENT_LIST_DIR} #
    --verbose
  DEPENDS ${SHELL_SOURCES}
  COMMENT
    "Generating CPPyGen Code To ${cppygen_generated_hpp} and ${cppygen_generated_cpp}"
  VERBATIM)
```

## Config
`cppygen` command does not work without configuration.
Use toml format configuration file.

**mode** ["header" or "source"]
cppygen parse strategy. "source" would parse source files for functions,
"header" would parse headers for functions. This option would only affect
function export. "header" would be faster.

**sources** [array of path, **required**(if soruce mode is on)]
Paths with `cppygen` will parse. `cppygen` can extract functions from
sources.

**headers** [array of path, **required**]
Paths with `cppygen` will parse.`cppygen` can extract structs or classes from
headers.

**output_dir** [path, **required**]
Output directory of generated code.

**search_namespace** [string, optional]
Default is "cppygen", this option will define the namespace witch
will be parsed by `cppygen`. Outside of this namespace would be ignored.

**include_directories** [array of dir, optional]
These directories will be passed as absolute paths to parser include flags.
Same as `flags =["-I/abs_path/to/dir"]`

**flags** [array of string, optional]
Parser compile options.

**libclang_path** [path, optional]
Path to `libclang` shared library.

**include_headers** [array of filename, optional]
**deprecated** `cppygen` does not resolve include paths, thus if you want to export C++
classes you should specify include filenames.


## Examples
See the `examples` directry for sample projects.

### Function
```cpp
namespace cppygen {
/**
 * pyname: py_foo
 * description: some description
 **/
void foo() {

}

}
```
This function will export to python as "py_foo".
`description` would be python docstring.


## Env

```bash
PYGEN_LIBCLANG_PATH # Path to clang shared library
PYGEN_COMPILE_FLAGS # additional flags to parse file
```
