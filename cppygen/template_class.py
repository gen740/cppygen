from typing import TypedDict


class TemplateClass:
    class MemberFunctionSignature(TypedDict):
        name: str
        pyname: str
        return_type: str
        args: list[tuple[str, str]]
        description: str
        call_guards: list[str]

    def __init__(self):
        self._name: str | None = None
        self._base_classes: list[tuple[str, bool]] = []
        self._namespace: list[str] = []
        self._members: list[dict[str, str]] = []
        self._member_funcs: list[TemplateClass.MemberFunctionSignature] = []
        self._module: str | None = None
        self._description = ""

    def set_name(self, name: str, namespace: list[str]):
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
