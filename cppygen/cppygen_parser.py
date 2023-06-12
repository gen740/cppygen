import copy
import os
import re
from typing import Literal

from cppygen._clang.cindex import (
    AccessSpecifier,
    Config,
    Cursor,
    CursorKind,
    TranslationUnit,
)

from .cppclass import CppClass
from .function import Function
from .logging import get_logger
from .submodule import Submodule

logger = get_logger("parser")


class Parser:
    """
    Analyze C++ source files and Generate pybind11 C++ code.
    """

    def __init__(
        self,
        namespace: str | None = None,
        *,
        library_path: str | None = None,
        library_file: str | None = None,
        verbose: bool = False,
    ):
        self._functions: list[Function] = []
        self._submodules: list[Submodule] = []
        self._cpp_classes: list[CppClass] = []
        self._export_classes: list[CppClass] = []
        self._cpp_template_classes: list[CppClass] = []
        self._hpp_includes: list[str] = []
        self._namespace = namespace or "cppygen"
        self._verbose = verbose
        self._call_guards: list[str] = []

        if library_file != None and library_path != None:
            raise ValueError(f"Both library_path and library_file cannot be set.")
        if not library_path is None:
            if not Config.library_file:
                Config.set_library_path(library_path)
            return
        if not library_file is None:
            if not Config.library_file:
                Config.set_library_file(library_file)
            return
        if (library_file is None and library_path is None) and (
            cppygen_libclang_path := os.environ.get("CPPYGEN_LIBCLANG_PATH", None)
        ) is not None:
            if not Config.library_file:
                Config.set_library_file(cppygen_libclang_path)
            return

    def _get_tu(self, source: str, filename: str, flags=[]) -> TranslationUnit:
        if flags == None:
            flags = []
        if (cppygen_flags := os.environ.get("CPPYGEN_COMPILE_FLAGS", None)) is not None:
            flags.extend(cppygen_flags.split(" "))
        args = list(flags)
        name = filename
        return TranslationUnit.from_source(
            name,
            args,
            unsaved_files=[(name, source)],
            options=TranslationUnit.PARSE_NONE,
        )

    def _extract_functions(
        self,
        cu: Cursor,
        namespace: list[str],
        module_name: str,
        mode: Literal["source"] | Literal["header"] = "source",
    ):
        for i in list(cu.get_children()):
            i: Cursor
            if i.kind == CursorKind.FUNCTION_DECL and (i.is_definition() or mode == "header"):  # type: ignore
                func = Function()
                func.set_return_type(i.result_type.spelling)
                func.set_name(i.spelling, namespace)
                func.set_module(module_name)
                for call_guard in self._call_guards:
                    func.add_call_guard(call_guard)

                # extract comment string
                raw_comment = i.raw_comment or ""
                raw_comment = raw_comment.replace('"', '\\"')
                # print("raw_comment", raw_comment)

                pyname, description = _extract_comment_string(str(raw_comment))

                if pyname is not None:
                    func.pyname = pyname
                func.set_description(description and description or "")

                for j in list(i.get_children()):
                    j: Cursor
                    if j.kind == CursorKind.PARM_DECL:  # type: ignore
                        func.add_argument_type((j.spelling, j.type.spelling))
                if self._verbose:
                    print("\t| Function    | " + func.signature())
                if not func in self._functions:
                    self._functions.append(func)

    def _extract_struct_and_class(
        self, cu: Cursor, namespace: list[str], module_name: str
    ):
        def visit(i: Cursor, namespace: list[str], is_template):
            print(i.kind)
            cpp_class = CppClass(is_template)
            cpp_class.set_name(i.spelling, namespace)
            cpp_class.set_module(module_name)
            cpp_class.set_description(i.brief_comment or "")
            if self._verbose:
                print("\t| Class       | " + cpp_class.signature())
            for j in list(i.get_children()):
                j: Cursor
                if j.kind == CursorKind.CXX_BASE_SPECIFIER:  # type: ignore
                    if self._verbose:
                        print(
                            "\t| BaseClass   | "
                            + "::".join([*namespace, i.spelling])
                            + j.spelling
                        )
                    cpp_class.add_base_class(j.spelling)
                    teplate_declares = copy.deepcopy(
                        [j for j in self._cpp_classes if j._is_template]
                    )

                    for k in teplate_declares:
                        if k._full_name in j.spelling:
                            base_class = copy.deepcopy(k)
                            base_class.set_name(j.spelling.split("::")[-1])
                            if base_class not in self._export_classes:
                                self._export_classes.append(base_class)
                if j.kind == CursorKind.STRUCT_DECL or j.kind == CursorKind.CLASS_DECL:  # type: ignore
                    visit(j, [*namespace, i.spelling], False)
                if j.kind == CursorKind.CLASS_TEMPLATE:  # type: ignore
                    visit(j, [*namespace, i.spelling], True)
                if j.kind == CursorKind.FIELD_DECL:  # type: ignore
                    # メンバー変数の抽出
                    cpp_class.add_member(
                        j.spelling,
                        j.type.spelling,
                        j.brief_comment or "",
                        j.access_specifier == AccessSpecifier.PRIVATE,  # type: ignore
                    )
                    if self._verbose:
                        print(
                            "\t| ClassMember | "
                            + "::".join([*namespace, i.spelling])
                            + "  "
                            + j.type.spelling
                            + " "
                            + j.spelling
                        )
                elif j.kind == CursorKind.CXX_METHOD:  # type: ignore
                    # メンバー関数の抽出
                    args = []
                    for k in list(j.get_children()):
                        if k.kind == CursorKind.PARM_DECL:  # type: ignore
                            args.append((k.spelling, k.type.spelling))
                    (pyname, description) = _extract_comment_string(j.raw_comment or "")
                    cpp_class.add_member_func(
                        name=j.spelling,
                        pyname=pyname,
                        return_type=j.result_type.spelling,
                        args=args,
                        description=description or "",
                        call_guards=self._call_guards,
                        private=j.access_specifier == AccessSpecifier.PRIVATE,  # type: ignore
                    )
                    if self._verbose:
                        print(
                            "\t| ClassMethod | "
                            + "::".join([*namespace, i.spelling])
                            + "::"
                            + j.spelling
                            + "("
                            + ", ".join([f"{k[0]} {k[1]}" for k in args])
                            + ") -> "
                            + j.result_type.spelling
                        )
            self._cpp_classes.append(cpp_class)
            if not cpp_class._is_template:
                self._export_classes.append(cpp_class)

        i: Cursor
        for i in list(cu.get_children()):
            if i.kind == CursorKind.CLASS_TEMPLATE:  # type: ignore
                visit(i, namespace, True)
            if i.kind == CursorKind.STRUCT_DECL or i.kind == CursorKind.CLASS_DECL:  # type: ignore
                visit(i, namespace, False)

    def add_hpp_includes(self, hpp: str):
        self._hpp_includes.append(hpp)

    def add_call_guard(self, call_guard: str):
        self._call_guards.append(call_guard)

    def parse(
        self,
        source: str,
        filename: str,
        lang: str = "cpp",
        flags=[],
        with_diagnostic=False,
        mode: Literal["source"] | Literal["header"] = "source",
    ):
        tu: TranslationUnit = self._get_tu(source, filename, flags)
        if with_diagnostic:
            has_error = False
            for diag in tu.diagnostics:
                if diag.severity in [diag.Fatal, diag.Error]:
                    has_error = True
                    logger.error(
                        f"{diag.location.file}:{diag.location.line}:{diag.location.column}: error: {diag.spelling} [{diag.option}]"
                    )
            if has_error:
                exit(1)
        root: Cursor = tu.cursor
        for i in list(root.get_children()):
            i: Cursor

            # Recursive Function
            def visit(x: Cursor, namespace: list[str], module_name: str):
                if mode == "source":
                    if lang == "cpp":
                        self._extract_functions(x, namespace, module_name)
                    elif lang == "hpp":
                        self._extract_struct_and_class(x, namespace, module_name)
                elif mode == "header":
                    self._extract_functions(x, namespace, module_name, mode="header")
                    self._extract_struct_and_class(x, namespace, module_name)
                else:
                    raise KeyError('Mode should be "source" or "header"')
                for i in list(x.get_children()):
                    i: Cursor
                    namespace_in = copy.deepcopy(namespace)
                    if i.kind == CursorKind.NAMESPACE:  # type: ignore
                        submod = Submodule()
                        submod.set_name(i.spelling)
                        submod.set_description(i.brief_comment or "")
                        submod.set_parent(copy.deepcopy(namespace_in))
                        if not submod in self._submodules:
                            if self._verbose:
                                print(f"\t| Submodule   | {submod.cpp_name}")
                            self._submodules.append(submod)
                        namespace_in.append(i.spelling)
                        visit(i, namespace_in, submod.cpp_name)

            # Search top-level namespace
            if i.kind == CursorKind.NAMESPACE and i.spelling == self._namespace:  # type: ignore
                visit(i, [self._namespace], self._namespace)

    def parse_from_file(
        self,
        filename: str,
        lang: str = "cpp",
        flags=[],
        mode: Literal["header"] | Literal["source"] = "source",
    ):
        with open(filename, "r") as f:
            data = f.read()
        self.parse(data, filename, lang, flags, with_diagnostic=True, mode=mode)

    def to_decl_string(self):
        return (
            "/* Function Declarations Start */\n"
            + "\n".join([i.to_decl_string() for i in self._functions] + [""])
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
            + "\n".join(
                [
                    # overloaded function
                    "\t" + i.to_pybind_string(overloaded=True)
                    # Check if more than two function has same signature.
                    if [j._full_name for j in self._functions].count(i._full_name) > 1
                    # Non overloaded function
                    else "\t" + i.to_pybind_string()
                    for i in self._functions
                ]
                + [""]
            )
            + "\t/* Function Export End */\n\n"
            + "\t/* Structs and Classes Export Start */\n"
            + "\n".join(
                ["\t" + i.to_pybind_string() for i in self._export_classes] + [""]
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
            "namespace CPPyGen {\n\n"
            f"static inline void CPPyGenExport(pybind11::module_ {self._namespace})\n"
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
            '#include "cppygen_generated.hpp"\n\n'
            "#include <pybind11/cast.h>\n"
            "#include <pybind11/pybind11.h>\n"
            "#include <pybind11/pytypes.h>\n"
            "#include <pybind11/stl.h>\n\n"
            "\n"
            f"{self.to_decl_string()}\n"
            "\n"
            "namespace CPPyGen {\n\n"
            f"void CPPyGenExport(pybind11::module_ {self._namespace})\n"
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
            + "".join([f'#include "{i}"\n' for i in self._hpp_includes])
            + "/* Custom Header Include End */\n\n"
            "namespace CPPyGen {\n\n"
            f"extern void CPPyGenExport(pybind11::module_ {self._namespace});\n\n"
            "}"
        )


def _extract_comment_string(raw_comment: str) -> tuple[str | None, str | None]:
    return (
        (re.search(r"pyname: *(.*)", raw_comment) or [None, None])[1],
        (re.search(r"description: *(.*)", raw_comment) or [None, None])[1],
    )
