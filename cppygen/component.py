from typing import Dict, List, Tuple, TypedDict, cast


class Function(object):
    """
    Function を表すクラス。
    必要な情報を詰め込み、 to_pybind_string で生成する。
    """

    def __init__(self):
        self._return_type: str = ""
        self._arguments: List[Tuple[str, str]] = []
        self._name: str | None = None
        self._full_name: str | None = None
        self._namespace: List[str] = []
        self._description = ""
        self._module: str | None = None
        self._pyname: str | None = None
        self._call_guards: List[str] = []

    def set_name(self, name: str, namespace: List[str]):
        self._name = name
        self._namespace = namespace
        self._full_name = f"{'::'.join(namespace)}::{name}"

    def set_return_type(self, type: str):
        self._return_type = type

    def add_call_guard(self, call_guard: str):
        self._call_guards.append(call_guard)

    def set_argument_types(self, types: List[Tuple[str, str]]):
        """
        parameter: [(name, type),]
        """
        self._arguments = types

    @property
    def pyname(self):
        self._pyname

    @pyname.setter
    def pyname(self, python_name: str):
        self._pyname = python_name

    def add_argument_type(self, type: Tuple[str, str]):
        """
        parameter: (name, type)
        """
        self._arguments.append(type)

    def set_description(self, description: str):
        self._description = description

    def set_module(self, module: str):
        self._module = module

    def to_pybind_string(self, overloaded=False):
        if self._name == None or self._full_name == None or self._module == None:
            print("Parse Error Skipping ...")
            return ""
        args = [f', pybind11::arg("{i[0]}")' for i in self._arguments]
        self._pyname = self._pyname or self._name
        if overloaded:
            return (
                f'{self._module}.def("{self._pyname}", '
                f'static_cast<{self._return_type} (*)({", ".join([i[1] for i in self._arguments])})>'
                f'(&{self._full_name}), "{self._description}"'
                f"""{"".join(args)}{f", pybind11::call_guard<{', '.join(self._call_guards)}>()" if len(self._call_guards) > 0 else ""});"""
            )
        else:
            return (
                f'{self._module}.def("{self._pyname}", &{self._full_name}, "{self._description}"'
                f"""{"".join(args)}{f", pybind11::call_guard<{', '.join(self._call_guards)}>()" if len(self._call_guards) > 0 else ""});"""
            )

    def to_decl_string(self):
        if self._name == None or self._full_name == None or self._module == None:
            print("Parse Error Skipping ...")
            return ""
        args = [f"{i[1]}" for i in self._arguments]
        return (
            f'namespace {"::".join(self._namespace)} '
            f'{{ {self._return_type} {self._name}({", ".join(args)}); }}'
        )

    def signature(self, with_return_type=True) -> str:
        args = [f"{i[1]}" for i in self._arguments]
        if with_return_type:
            return f'{"::".join(self._namespace)}::{self._name}({", ".join(args)}) -> {self._return_type}'
        else:
            return f'{"::".join(self._namespace)}::{self._name}({", ".join(args)})'

    def __eq__(self, obj):
        if isinstance(obj, Function):
            return self.signature(with_return_type=False) == obj.signature(
                with_return_type=False
            )
        else:
            return False


class StructOrClass:
    """
    Represent Struct or Class.
    """

    class MemberFunctionSignature(TypedDict):
        name: str
        pyname: str
        return_type: str
        args: List[Tuple[str, str]]
        description: str
        call_guards: List[str]

    def __init__(self):
        self._name: str | None = None
        self._namespace: List[str] = []
        self._members: list[Dict[str, str]] = []
        self._member_funcs: list[StructOrClass.MemberFunctionSignature] = []
        self._module: str | None = None
        self._description = ""

    def set_name(self, name: str, namespace: List[str]):
        self._name = name
        self._namespace = namespace
        self._full_name = f"{'::'.join(namespace)}::{name}"

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

    def add_member_func(
        self,
        name: str,
        pyname: str | None,
        return_type: str,
        args: List[Tuple[str, str]],  # list[(name, type)]
        description: str = "",
        call_guards: List[str] = [],
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
            f'pybind11::class_<::{self._full_name}>({self._module}, "{self._name}")\n'
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


class Submodule:
    """
    Represent Submodule.
    """

    def __init__(self):
        self._name: str | None = None
        self._description = ""
        self._parents: List[str] = []

    @property
    def cpp_name(self) -> str:
        if self._name == None:
            print("Parse Error Skipping ...")
            return ""
        return "_".join(self._parents) + "_" + self._name

    @property
    def cpp_parent_name(self) -> str:
        if self._name == None:
            print("Parse Error Skipping ...")
            return ""
        return "_".join(self._parents)

    def set_name(self, name: str):
        self._name = name

    def set_description(self, description: str):
        self._description = description

    def set_parent(self, parents: List[str]):
        self._parents = parents

    def to_pybind_string(self):
        if self._name == None:
            print("Parse Error Skipping ...")
            return ""
        return f'auto {self.cpp_name} = {self.cpp_parent_name}.def_submodule("{self._name}", "{self._description}");'

    def __eq__(self, obj):
        if isinstance(obj, Submodule):
            return self.cpp_name == obj.cpp_name
        else:
            return False
