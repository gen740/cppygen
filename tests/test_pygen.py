import platform

import pytest

from pygen.pygen_parser import Parser


def test_pygen_valueerror():
    with pytest.raises(ValueError):
        Parser(library_file="/usr/lib", library_path="/usr/lib")


# def test_diagnostics():
#    for diag in tu.diagnostics:
#    if diag.severity == diag.Fatal:
#       print(diag.location)
#       print(diag.spelling)
#       print(diag.option)
#


def test_pygen():
    with open("./tests/sources/test.cpp", "r") as f:
        data = f.read()

    if platform.system() == "Linux":
        p = Parser()
        p.parse(
            data,
            lang="cpp",
            flags=["-Itests/sources"],
            with_diagnostic=True,
        )
    else:
        p = Parser(library_file="/usr/local/opt/llvm/lib/libclang.dylib")
        p.parse(
            data,
            lang="cpp",
            flags=["-I/usr/local/opt/llvm/lib/clang/15.0.7/include", "-Itests/sources"],
            with_diagnostic=True,
        )

    with open("./tests/sources/test.hpp", "r") as f:
        data = f.read()

    p.parse(data, lang="hpp", flags=[], with_diagnostic=True)

    print(p.cpp_generate())
    print(p.hpp_generate())


test_pygen()
