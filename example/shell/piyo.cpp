#include "piyo.hpp"
#include "hoge.hpp"
#include <vector>

namespace Shell::piyo {
Piyoyo make_piyoyo() {
  Piyoyo tmp;
  tmp.setValue(-5);
  return tmp;
}
std::vector<double> fugafuga() { return {3, 4, 5, 6}; }

} // namespace Shell::piyo
