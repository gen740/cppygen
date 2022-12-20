import pytest

from pygen.pygen_parser import Parser


def test_pygen_valueerror():
    with pytest.raises(ValueError):
        Parser(library_file="/usr/lib", library_path="/usr/lib")


def test_pygen():
    with open("./tests/sources/test.cpp", "r") as f:
        data = f.read()

    try:
        p = Parser()
        p.parse(data, lang="cpp", flags=[])
    except Exception as _:
        p = Parser(library_file="/usr/local/opt/llvm/lib/libclang.dylib")
        p.parse(data, lang="cpp", flags=[])

    with open("./tests/sources/hoge.hpp", "r") as f:
        data = f.read()

    p.parse(data, lang="hpp", flags=[])

    print(p.cpp_generate())
    print(p.hpp_generate())
