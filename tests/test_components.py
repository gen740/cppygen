from cppygen.component import Function, StructOrClass, Submodule


def test_function():
    fun = Function()

    fun.set_name("test_function1", ["Shell", "foo"])
    assert fun._name == "test_function1"
    assert fun._namespace == ["Shell", "foo"]
    assert fun._full_name == "Shell::foo::test_function1"

    fun.set_description("this is test function1")
    assert fun._description == "this is test function1"

    fun.set_module("Shell_foo")
    assert fun._module == "Shell_foo"

    fun.set_return_type("TestClass")
    assert fun._return_type == "TestClass"

    fun.set_argument_types([("arg1", "int"), ("arg2", "std::string")])
    assert fun._arguments == [("arg1", "int"), ("arg2", "std::string")]

    assert (
        fun.to_decl_string()
        == "namespace Shell::foo { TestClass test_function1(int arg1, std::string arg2); }"
    )

    assert (
        fun.to_pybind_string()
        == """Shell_foo.def("test_function1", &Shell::foo::test_function1, "this is test function1", pybind11::arg("arg1"), pybind11::arg("arg2"));"""
    )

    fun.pyname = "__str__"

    assert (
        fun.to_pybind_string()
        == """Shell_foo.def("__str__", &Shell::foo::test_function1, "this is test function1", pybind11::arg("arg1"), pybind11::arg("arg2"));"""
    )


def test_submodule():
    submodule = Submodule()

    submodule.set_name("submodule1")
    assert submodule._name == "submodule1"

    submodule.set_description("This is submodule 1")
    assert submodule._description == "This is submodule 1"

    submodule.set_parent(["psub1", "psub2"])
    assert submodule._parents == ["psub1", "psub2"]

    assert submodule.cpp_name == "psub1_psub2_submodule1"
    assert submodule.cpp_parent_name == "psub1_psub2"

    assert (
        submodule.to_pybind_string()
        == """auto psub1_psub2_submodule1 = psub1_psub2.def_submodule("submodule1", "This is submodule 1");"""
    )


def test_submod_compare():
    submod1 = Submodule()
    submod2 = Submodule()
    submod3 = Submodule()

    submod1.set_name("foo")
    submod2.set_name("foo")
    submod3.set_name("bar")

    assert submod1 == submod2
    assert submod1 != submod3
    assert submod2 != submod3


def test_struct_or_class():
    soc = StructOrClass()

    soc.set_name("class1", ["mod1", "mod2"])
    assert soc._name == "class1"
    assert soc._namespace == ["mod1", "mod2"]
    assert soc._full_name == "mod1::mod2::class1"

    soc.set_description("this is class 1")
    assert soc._description == "this is class 1"

    soc.set_module("mod1_mod2")
    assert soc._module == "mod1_mod2"

    soc.add_member("member1", "int", "this is the member1")
    soc.add_member("member2", "std::array<int, 5>", "this is the member2")

    soc.add_member_func(
        "mfun1",
        "mfun1",
        "int",
        [("arg1", "int"), ("arg2", "std::string")],
        "this is the member1",
    )

    soc.add_member_func(
        "mfun2",
        "mfun2",
        "char",
        [("arg1", "std::string"), ("arg2", "std::vector<int>")],
        "this is the member2",
    )

    expect_members = [
        {
            "name": "member1",
            "type": "int",
            "description": "this is the member1",
            "private": False,
        },
        {
            "name": "member2",
            "type": "std::array<int, 5>",
            "description": "this is the member2",
            "private": False,
        },
    ]
    assert soc._members == expect_members

    expect_member_functions = [
        {
            "name": "mfun1",
            "pyname": "mfun1",
            "return_type": "int",
            "description": "this is the member1",
            "private": False,
            "args": [("arg1", "int"), ("arg2", "std::string")],
        },
        {
            "name": "mfun2",
            "pyname": "mfun2",
            "return_type": "char",
            "description": "this is the member2",
            "private": False,
            "args": [("arg1", "std::string"), ("arg2", "std::vector<int>")],
        },
    ]
    assert soc._member_funcs == expect_member_functions

    expect_pybind_string = (
        """pybind11::class_<::mod1::mod2::class1>(mod1_mod2, "class1")\n"""
        """\t\t.def(pybind11::init())\n"""
        """\t\t.def_readwrite("member1", &mod1::mod2::class1::member1, "this is the member1")\n"""
        """\t\t.def_readwrite("member2", &mod1::mod2::class1::member2, "this is the member2")\n"""
        """\t\t.def("mfun1", &mod1::mod2::class1::mfun1, "this is the member1")\n"""
        """\t\t.def("mfun2", &mod1::mod2::class1::mfun2, "this is the member2");"""
    )
    assert soc.to_pybind_string() == expect_pybind_string
