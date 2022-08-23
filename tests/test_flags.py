from pygen.pygen_parser import Parser


def main():
    with open("./sources/hoge.cpp", "r") as f:
        data = f.read()
    p = Parser()
    p.parse(data, flags=["-Isources"])
    # print(p.to_decl_string())
    # print(p.to_submod_string())
    # print(p.to_export_string())
    print(p.generate())


if __name__ == "__main__":
    main()
