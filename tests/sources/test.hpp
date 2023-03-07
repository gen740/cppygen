#pragma once
#include <string>

namespace cppygen {

void foo();
void foo(int);
void bar();

struct Hoge {
public:
  Hoge() {}

  /**
   *
   **/
  void foo();
  void foo(int);
  void bar();

  /**
   * pyname: __str__
   * description: String Conversion Function
   **/
  std::string to_str() { return ""; }

  int a = 3;

private:
  int b = 3;
};

} // namespace cppygen
