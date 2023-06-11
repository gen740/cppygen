#pragma once
#include <iostream>
#include <vector>

namespace Shell {

void hoge();

void hoge(char);

void fuga();

int add(int a, int b);

int sub(int a, int b);

template <class foo, class bar> class FooBase0 {
public:
  int some_val = 0;
};

class Foo : public ::Shell::FooBase0<int, float> {
public:
  Foo() = default; // pybind11 から見えるのは この default コンストラクターのみ
  Foo(int a, int b) : a(a), b(b) {}


  struct InnerBar {
    void barbar() { std::cout << "Hoge" << std::endl; }
  };

  void bar() {}
  void bar(int) {}

  int a = 32;
  int b = 42;
};

} // namespace Shell
