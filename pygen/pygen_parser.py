from clang.cindex import Cursor, CursorKind, TranslationUnit, AccessSpecifier
from typing import Dict, List, Tuple, Union

# Config.set_library_path("")
#


class Parser:
    """
    PyGen はヘッダーを解析し、pybind11 用の関数を自動で作り出すコードジェネレー
    タです。
    """

    class Function(object):
        """
        Function を表すクラス。
        必要な情報を詰め込み、 to_pybind_string で生成する。
        """

        def __init__(self):
            self._return_type: str = ""
            self._arguments: List[Tuple[str, str]] = []
            self._name: Union[str, None] = None
            self._full_name: Union[str, None] = None
            self._namespace: List[str] = []
            self._description = ""
            self._module: Union[str, None] = None

        def set_function_name(self, name: str, namespace: List[str]):
            self._name = name
            self._namespace = namespace
            self._full_name = f"{'::'.join(namespace)}::{name}"

        def set_return_type(self, type: str):
            self._return_type = type

        def set_argument_type(self, type: str):
            self._return_type = type

        def add_argument_type(self, type: Tuple[str, str]):
            """
            (name, type)
            """
            self._arguments.append(type)

        def set_description(self, description: str):
            self._description = description

        def set_module(self, module: str):
            self._module = module

        def to_pybind_string(self):
            if self._name == None or self._full_name == None or self._module == None:
                print("Parse Error Skipping ...")
                return ""
            args = [f', pybind11::arg("{i[0]}")' for i in self._arguments]
            return (
                f'{self._module}.def("{self._name}", &{self._full_name}, "{self._description}"'
                f'{"".join(args)});'
            )

        def to_decl_string(self):
            if self._name == None or self._full_name == None or self._module == None:
                print("Parse Error Skipping ...")
                return ""
            args = [f"{i[1]} {i[0]}" for i in self._arguments]
            return (
                f'namespace {"::".join(self._namespace)} '
                f'{{ {self._return_type} {self._name}({", ".join(args)}); }}'
            )

    class Submodule:
        """
        Submodule を表すクラス
        必要な情報を詰め込み、 to_pybind_string で生成する。
        """

        def __init__(self):
            self._name: Union[str, None] = None
            self._description = ""
            self._parent: Union[str, None] = None

        def set_name(self, name: str):
            self._name = name

        def set_description(self, description: str):
            self._description = description

        def set_parent(self, parent: str):
            self._parent = parent

        def to_pybind_string(self):
            if self._name == None:
                print("Parse Error Skipping ...")
                return ""
            return f'auto {self._name} = {self._parent}.def_submodule("{self._name}", "{self._description}");'

    class StructOrClass:
        """
        Submodule を表すクラス
        必要な情報を詰め込み、 to_pybind_string で生成する。
        """

        def __init__(self):
            self._name: Union[str, None] = None
            self._namespace: List[str] = []
            self._members: list[Dict[str, Union[bool, str]]] = []
            self._member_funcs: list[
                Dict[str, Union[bool, str, List[Tuple[str, str]]]]
            ] = []
            self._module: Union[str, None] = None
            self._description = ""

        def set_name(self, name: str):
            self._name = name

        def add_member(
            self, name: str, type: str, description: str = "", private: bool = False
        ):
            self._members.append(
                {
                    "name": name,
                    "type": type,
                    "description": description,
                    "private": private,
                }
            )

        def add_member_func(
            self,
            name: str,
            type: str,
            args: List[Tuple[str, str]],  # list[(name, type)]
            description: str = "",
            private: bool = False,
        ):
            self._member_funcs.append(
                {
                    "name": name,
                    "return_type": type,
                    "description": description,
                    "private": private,
                    "args": args,
                }
            )

        def set_module(self, module: str):
            self._module = module

        def set_description(self, description: str):
            self._description = description

        def set_namespace(self, namespace: List[str]):
            self._namespace = namespace

        def get_members(self):
            return self._members

        def get_member_funcs(self):
            return self._member_funcs

        def to_pybind_string(self):
            if self._name == None or self._module == None:
                print("Parse Error Skipping ...")
                return ""
            return (
                f'pybind11::class_<::{"::".join(self._namespace + [self._name])}>({self._module}, "{self._name}")\n'
                "\t\t.def(pybind11::init())"
                ## Member 変数の宣言
                + "\n".join(
                    [""]
                    + [
                        f'\t\t.def_readwrite("{i["name"]}",'
                        f' &{"::".join(self._namespace + [self._name])}::{i["name"]}, "{i["description"]}")'
                        for i in self._members
                        if not i["private"]
                    ]
                )
                ## Member 関数の宣言
                + "\n".join(
                    [""]
                    + [
                        f'\t\t.def("{i["name"]}",'
                        f' &{"::".join(self._namespace + [self._name])}::{i["name"]}, "{i["description"]}")'
                        for i in self._member_funcs
                        if not i["private"]
                    ]
                )
                + ";"
            )

    def __init__(self):
        self._funcitons: List[Parser.Function] = []
        self._submodules: List[Parser.Submodule] = []
        self._structs_and_classes: List[Parser.StructOrClass] = []
        self._hpp_includes: List[str] = []

    def _get_tu(self, source: str, lang: str = "c", flags=[]) -> TranslationUnit:
        if flags == None:
            flags = []
        args = list(flags)
        name = "t.c"
        if lang == "cpp":
            name = "t.cpp"
            # args.append("-std=c++11")
        if lang == "hpp":
            name = "t.hpp"
            # args.append("-std=c++11")
        return TranslationUnit.from_source(
            name,
            args,
            unsaved_files=[(name, source)],
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
        )

    def _extract_functions(self, cu: Cursor, namespace: List[str]):
        """
        cu 以下にある関数を抽出する
        """
        for i in list(cu.get_children()):
            i: Cursor
            if i.kind == CursorKind.FUNCTION_DECL and i.is_definition():  # type: ignore
                func = Parser.Function()
                func.set_return_type(i.result_type.spelling)
                func.set_function_name(i.spelling, namespace)
                func.set_module(namespace[-1])
                func.set_description(i.brief_comment or "")
                for j in list(i.get_children()):
                    j: Cursor
                    if j.kind == CursorKind.PARM_DECL:  # type: ignore
                        func.add_argument_type((j.spelling, j.type.spelling))
                self._funcitons.append(func)

    def _exract_struct_and_class(self, cu: Cursor, namespace: List[str]):
        """
        cu 以下にある構造体を抽出する
        """
        for i in list(cu.get_children()):
            i: Cursor
            # print(i.kind, i.spelling)
            if i.kind == CursorKind.STRUCT_DECL or i.kind == CursorKind.CLASS_DECL:  # type: ignore
                struct_or_class = Parser.StructOrClass()
                struct_or_class.set_name(i.spelling)
                struct_or_class.set_module(namespace[-1])
                struct_or_class.set_namespace(namespace)
                struct_or_class.set_description(i.brief_comment or "")
                for j in list(i.get_children()):
                    j: Cursor
                    if j.kind == CursorKind.FIELD_DECL:  # type: ignore
                        # メンバー変数の抽出
                        struct_or_class.add_member(
                            j.spelling,
                            j.type.spelling,
                            j.brief_comment or "",
                            j.access_specifier == AccessSpecifier.PRIVATE,  # type: ignore
                        )
                    elif j.kind == CursorKind.CXX_METHOD:  # type: ignore
                        # メンバー関数の抽出
                        args = []
                        for k in list(j.get_children()):
                            if k.kind == CursorKind.PARM_DECL:  # type: ignore
                                args.append((k.spelling, k.type.spelling))
                        struct_or_class.add_member_func(
                            j.spelling,
                            j.result_type.spelling,
                            args,
                            j.brief_comment or "",
                            j.access_specifier == AccessSpecifier.PRIVATE,  # type: ignore
                        )
                self._structs_and_classes.append(struct_or_class)

    def add_hpp_includes(self, hpp: str):
        self._hpp_includes.append(hpp)

    def parse(self, source: str, lang: str = "cpp", flags=[]):
        root: Cursor = self._get_tu(source, lang, flags).cursor
        for i in list(root.get_children()):
            i: Cursor

            # 再起的に関数を抽出する。
            def visit(x: Cursor, namespace):
                if lang == "cpp":
                    self._extract_functions(x, namespace)
                elif lang == "hpp":  # ヘッダーでのみクラスを抽出する。
                    self._exract_struct_and_class(x, namespace)
                for i in list(x.get_children()):
                    i: Cursor
                    namespace_in = list(namespace)
                    if i.kind == CursorKind.NAMESPACE:  # type: ignore
                        submod = Parser.Submodule()
                        submod.set_name(i.spelling)
                        submod.set_description(i.brief_comment or "")
                        self._submodules.append(submod)
                        submod.set_parent(namespace_in[-1])
                        namespace_in.append(i.spelling)
                        visit(i, namespace_in)

            # トップレベルの Shell namespace を探す
            if i.kind == CursorKind.NAMESPACE and i.spelling == "Shell":  # type: ignore
                visit(i, ["Shell"])

    def parse_from_file(self, filename: str, lang: str = "cpp", flags=[]):
        with open(filename, "r") as f:
            data = f.read()
        self.parse(data, lang, flags)

    def to_decl_string(self):
        return (
            "/* Function Declarations Start */\n"
            + "\n".join([i.to_decl_string() for i in self._funcitons] + [""])
            + "/* Function Declarations End */\n\n"
        )

    def to_submod_string(self):
        return (
            "\t/* Submodule Declarations Start */\n"
            + "\n".join(["\t" + i.to_pybind_string() for i in self._submodules] + [""])
            + "\t/* Submodule Declarations End */\n\n"
        )

    def to_export_string(self):
        return (
            "\t/* Function Export Start */\n"
            + "\n".join(["\t" + i.to_pybind_string() for i in self._funcitons] + [""])
            + "\t/* Function Export End */\n\n"
            "\t/* Structs and Classes Export Start */\n"
            + "\n".join(
                ["\t" + i.to_pybind_string() for i in self._structs_and_classes] + [""]
            )
            + "\t/* Structs and Classes Export End */\n\n"
        )

    def generate(self) -> str:
        """
        inline 関数を実装した、 header only なコードを自動生成する関数
        """
        return (
            "#pragma once\n\n"
            "#include <pybind11/cast.h>\n"
            "#include <pybind11/pybind11.h>\n"
            "#include <pybind11/pytypes.h>\n"
            "#include <pybind11/stl.h>\n\n"
            "/* Custom Header Include Start */\n"
            + "\n".join([f'#include "{i}"' for i in self._hpp_includes])
            + "/* Custom Header Include End */\n\n"
            f"{self.to_decl_string()}\n"
            "\n"
            "namespace PyGen {\n\n"
            "static inline void PyGenExport(pybind11::module_ Shell)\n"
            "{\n\n"
            f"{self.to_submod_string()}\n\n"
            f"{self.to_export_string()}\n\n"
            "};\n"
            "}"
        )

    def cpp_generate(self) -> str:
        """
        hpp_generate と対になる。 Export の関数の実装部分を自動生成するコード
        """
        return (
            '#include "pygen_generated.hpp"\n\n'
            "#include <pybind11/cast.h>\n"
            "#include <pybind11/pybind11.h>\n"
            "#include <pybind11/pytypes.h>\n"
            "#include <pybind11/stl.h>\n\n"
            "\n"
            f"{self.to_decl_string()}\n"
            "\n"
            "namespace PyGen {\n\n"
            "void PyGenExport(pybind11::module_ Shell)\n"
            "{\n\n"
            f"{self.to_submod_string()}\n\n"
            f"{self.to_export_string()}\n\n"
            "};\n"
            "}"
        )

    def hpp_generate(self) -> str:
        """
        Header で関数を宣言したりし実際に利用しやすいコードにする。
        """
        return (
            "#pragma once\n\n"
            "#include <pybind11/cast.h>\n"
            "#include <pybind11/pybind11.h>\n"
            "#include <pybind11/pytypes.h>\n"
            "#include <pybind11/stl.h>\n\n"
            "/* Custom Header Include Start */\n"
            + "\n".join([f'#include "{i}"' for i in self._hpp_includes])
            + "/* Custom Header Include End */\n\n"
            "namespace PyGen {\n\n"
            "extern void PyGenExport(pybind11::module_ Shell);\n\n"
            "}"
        )
