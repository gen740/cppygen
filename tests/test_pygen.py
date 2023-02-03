import platform

import pytest

from pygen.pygen_parser import Parser


def test_pygen_valueerror():
    with pytest.raises(ValueError):
        Parser(library_file="/usr/lib", library_path="/usr/lib")


def test_pygen():
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


test_pygen()
