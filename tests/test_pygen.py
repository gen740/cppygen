from pygen.pygen_parser import Parser, Parser


def test_function():
    pass


def test_struct_or_class():
    struct = Parser.StructOrClass()
    struct.set_name("Person")
    struct.add_member(
        name="hoge", type="int", description="hogehoge します", private=False
    )
    struct.add_member(name="foge", type="int", private=False)
    struct.add_member(name="piyo", type="int", private=False)
    struct.add_member_func(
        name="piyo_func",
        type="int",
        args=[("x", "double"), ("y", "double")],
        private=False,
    )
    struct.set_module("hoge")
    print(struct.to_pybind_string())


def main():
    # test_struct_or_class()
    with open("./sources/test.cpp", "r") as f:
        data = f.read()
    p = Parser()
    p.parse(data, lang="cpp", flags=[])

    with open("./sources/hoge.hpp", "r") as f:
        data = f.read()
    p.parse(data, lang="hpp", flags=[])
    # print(p.to_decl_string())
    # print(p.to_submod_string())
    # print(p.to_export_string())
    # print(p.generate())
    print(p.cpp_generate())
    print(p.hpp_generate())


if __name__ == "__main__":
    main()
