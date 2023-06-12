#include "hoge.hpp"
#include <iostream>
#include <string>

namespace Shell {

void start() { std::cout << "Example Start" << std::endl; }

double add(int a, int b) { return a + b; }

namespace impl {

void hello() { std::cout << "Hello" << std::endl; }

} // namespace Impl

} // namespace Shell
