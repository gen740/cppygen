import pytest

from cppygen.cppygen_parser import Parser


def test_cppygen_valueerror():
    with pytest.raises(ValueError):
        Parser(library_file="/usr/lib", library_path="/usr/lib")


def test_cppygen_source_mode():
    p = Parser()

    p.parse_from_file(
        "./tests/sources/test.cpp",
        lang="cpp",
    )
    p.parse_from_file(
        "./tests/sources/test.hpp",
        lang="hpp",
    )
    p.add_hpp_includes("foo.hpp")
    p.add_hpp_includes("bar.hpp")

    with open("./tests/expect_out/header", "r") as f:
        assert f.read() == f"{p.hpp_generate()}\n"

    with open("./tests/expect_out/impl", "r") as f:
        assert f.read() == f"{p.cpp_generate()}\n"


def test_cppygen_header_mode():
    p = Parser()

    p.parse_from_file("./tests/sources/test.hpp", lang="hpp", mode="header")
    p.add_hpp_includes("foo.hpp")
    p.add_hpp_includes("bar.hpp")

    with open("./tests/expect_out/header", "r") as f:
        assert f.read() == f"{p.hpp_generate()}\n"

    with open("./tests/expect_out/impl2", "r") as f:
        assert f.read() == f"{p.cpp_generate()}\n"
