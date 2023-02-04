#include <string>
#include <vector>

//! INCLUDE THIS HPP
#include "test.hpp"

namespace cppygen {

/**
 * description: foo
 **/
void f() {}

/**
 * pyname: pyg
 **/
int g(int a, int b) { return 0; }

// std check

auto h(std::string) {}

auto i(std::vector<double>) {}

} // namespace cppygen
