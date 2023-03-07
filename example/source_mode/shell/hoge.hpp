#pragma once
#include <vector>

namespace Shell {
class Foo {
public:
  Foo() = default; // pybind11 から見えるのは この default コンストラクターのみ
  Foo(int a, int b) : a(a), b(b) {}

  void bar() {}
  void bar(int) {}
  int a = 32;
  int b = 42;

private:
  int c = 88;
};

typedef std::vector<double> VectorD;

} // namespace Shell
