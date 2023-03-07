#include "hoge.hpp"
#include <iostream>
#include <string>

namespace Shell {

void start(std::string arg = "", std::string tty = "none") {
  std::cout << "This is dummy start function with arg = " << arg << std::endl;
  std::cout << "tty = " << tty << std::endl;
}

// このようなユーザー定義のクラスを用いている場合は
// PyGen はデフォルトでは Header
// の場所を探しきれず、ただしく、これがユーザー定義
// のクラスを返す変数であることを認識できないので、 flag を渡して
// Header の位置を教えてあげる必要がある。
Foo make_foo() { return Foo(1, 2); }

void hoge() { std::cout << "Hello" << std::endl; }

void hoge(char) { std::cout << "Hello" << std::endl; }

void fuga() { std::cout << "Hello Fuga" << std::endl; }

int add(int a, int b) { return a + b; }

int sub(int a, int b) { return a - b; }

namespace hogehoge {

/// Piyopiyo!!!
namespace piyo {

/// Comment!!!
int add_piyo(int x, int y) { return x + y; }

int add_(int x, int y) { return x + y; }

} // namespace piyo

} // namespace hogehoge

Shell::VectorD return_vector(Shell::VectorD a) { return a; }

} // namespace Shell
