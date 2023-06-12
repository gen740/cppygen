#pragma once
#include <iostream>
#include <string>
#include <vector>

namespace Shell {

/******************************************************************************
 * Simple Test
 ******************************************************************************/
void start();

// define simple function
double add(int a, int b);

// submodule
namespace impl {
/**
 * pyname: hey
 * description: this function was declared "hello" in C++.
 */
void hello();

} // namespace impl

/******************************************************************************
 * Simple Class and Inheritence
 ******************************************************************************/
class Person {
public:
  std::string name{"no_name"};
  int age{0};

  void hey() { std::cout << "Hello" << std::endl; }
  virtual void say() {
    std::cout << "I am " << name << " age is " << age << std::endl;
  }

  // Virtual Class should declare virtual destructor
  virtual ~Person() = default;
};

// Base class must be global namespace
class John : public ::Shell::Person {
public:
  John() {
    this->name = "John";
    this->age = 23;
  }

  void say() {
    std::cout << "Hello! I am " << name << " age is " << age << std::endl;
  }
};

template <class foo, class bar = int> struct FooBase {
public:
  foo th() {
    std::cout << "Foo" << std::endl;
    return foo();
  }
  int some_val = 0;
};

// You shold declare BaseClass as global namespace
class Foo : public ::Shell::FooBase<int, float> {
public:
  Foo() = default; // pybind11 から見えるのは この defaultコンストラクターのみ
  // Foo(int a, int b) : a(a), b(b) {}

  struct InnerBar {
    void barbar() { std::cout << "Hoge" << std::endl; }
  };

  void bar() {}
  void bar(int) {}

  int a = 32;
  int b = 42;
};

class Foo2 : public ::Shell::FooBase<int, float> {};

} // namespace Shell
