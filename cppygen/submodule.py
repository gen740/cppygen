from typing import Dict, List, Tuple, TypedDict


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
