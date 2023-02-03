import platform

import pytest

from cppygen.cppygen_parser import Parser


def test_cppygen_valueerror():
    with pytest.raises(ValueError):
        Parser(library_file="/usr/lib", library_path="/usr/lib")


def test_cppygen():
    p = Parser()

    p.parse_from_file(
        "./tests/sources/test.cpp",
        lang="cpp",
    )
    p.parse_from_file(
        "./tests/sources/test.hpp",
        lang="hpp",
    )

    print(p.cpp_generate())
    print(p.hpp_generate())


test_cppygen()
