import copy
import re
from typing import TypedDict


class CppClass:
    """
    Represent Struct or Class.
    """

    class MemberFunctionSignature(TypedDict):
        name: str
        pyname: str
        return_type: str
        args: list[tuple[str, str]]
        description: str
        call_guards: list[str]

    def __init__(self, is_template=False):
        self._name: str | None = None
        self._sanitized_name: str | None = None
        self._base_classes: list[str] = []
        self._namespace: list[str] = []
        self._members: list[dict[str, str]] = []
        self._member_funcs: list[CppClass.MemberFunctionSignature] = []
        self._module: str | None = None
        self._description = ""
        self._is_template = is_template
        # self._defined_template_classes: list[CppClass] = defined_template_classes
        self._template_parameter: list[tuple[str, str | None]] = []

    def set_name(self, name: str, namespace: list[str] | None = None):
        self._name = name
        self._sanitized_name = "_".join(filter(None, re.findall(r"\w*", self._name)))
        if namespace is not None:
            self._namespace = namespace
        self._full_name = f"{'::'.join(self._namespace)}::{name}"

    def add_member(
        self,
        name: str,
        type: str,
        description: str = "",
        private: bool = False,
    ):
        if not private:
            self._members.append(
                {
                    "name": name,
                    "type": type,
                    "description": description,
                }
            )

    def add_base_class(self, name: str):
        self._base_classes.append(name)

    def add_member_func(
        self,
        name: str,
        pyname: str | None,
        return_type: str,
        args: list[tuple[str, str]],  # list[(name, type)]
        description: str = "",
        call_guards: list[str] = [],
        private: bool = False,
    ):
        pyname = pyname or name
        if not private:
            self._member_funcs.append(
                {
                    "name": name,
                    "pyname": pyname,
                    "return_type": return_type,
                    "args": args,
                    "description": description,
                    "call_guards": call_guards,
                }
            )

    def set_module(self, module: str):
        self._module = module

    def set_description(self, description: str):
        self._description = description

    def get_members(self):
        return self._members

    def get_member_funcs(self):
        return self._member_funcs

    def to_pybind_string(self):
        if self._name == None or self._module == None:
            print("Parse Error Skipping ...")
            return ""
        return (
            # Class
            f"pybind11::class_<"
            + ", ".join([f"::{self._full_name}", *self._base_classes])
            + ">"
            + f'({self._module}, "{self._sanitized_name}")\n'
            "\t\t.def(pybind11::init())"
            # Declare members.
            + "\n".join(
                [""]
                + [
                    f'\t\t.def_readwrite("{i["name"]}",'
                    f' &{self._full_name}::{i["name"]}, "{i["description"]}")'
                    for i in self._members
                ]
            )
            # Declare member functions.
            + "\n".join(
                [""]
                + [
                    # overloaded funciton
                    f'\t\t.def("{i["pyname"]}", '
                    f'static_cast<{i["return_type"]} ({self._full_name}::*)({", ".join([j[1] for j in i["args"]])})>'
                    f'(&{self._full_name}::{i["name"]}), "{i["description"]}"'
                    f"""{f", pybind11::call_guard<{', '.join(i['call_guards'])}>()" if len(i['call_guards']) > 0 else ""})"""
                    if [j["name"] for j in self._member_funcs].count(i["name"]) > 1
                    # Non overloaded funciton
                    else f'\t\t.def("{i["pyname"]}",'
                    f' &{self._full_name}::{i["name"]}, "{i["description"]}"'
                    f"""{f", pybind11::call_guard<{', '.join(i['call_guards'])}>()" if len(i['call_guards']) > 0 else ""})"""
                    for i in self._member_funcs
                ]
            )
            + ";"
        )

    def signature(self) -> str:
        return f"{self._full_name}"

    def __eq__(self, obj):
        if isinstance(obj, CppClass):
            return self._full_name == obj._full_name
        else:
            return False
