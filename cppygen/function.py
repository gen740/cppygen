class Function(object):
    """
    Function を表すクラス。
    必要な情報を詰め込み、 to_pybind_string で生成する。
    """

    def __init__(self):
        self._return_type: str = ""
        self._arguments: list[tuple[str, str]] = []
        self._name: str | None = None
        self._full_name: str | None = None
        self._namespace: list[str] = []
        self._description = ""
        self._module: str | None = None
        self._pyname: str | None = None
        self._call_guards: list[str] = []

    def set_name(self, name: str, namespace: list[str]):
        self._name = name
        self._namespace = namespace
        self._full_name = f"{'::'.join(namespace)}::{name}"

    def set_return_type(self, type: str):
        self._return_type = type

    def add_call_guard(self, call_guard: str):
        self._call_guards.append(call_guard)

    def set_argument_types(self, types: list[tuple[str, str]]):
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

    def add_argument_type(self, type: tuple[str, str]):
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
