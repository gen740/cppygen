#pragma once
#include <vector>

namespace Shell {

void hoge();

void hoge(char);

void fuga();

int add(int a, int b);

int sub(int a, int b);

class Foo {
public:
  Foo() = default; // pybind11 から見えるのは この default コンストラクターのみ
  Foo(int a, int b) : a(a), b(b) {}

  void bar() {}
  void bar(int) {}
  int a = 32;
  int b = 42;
};

typedef std::vector<double> VectorD;

} // namespace Shell
