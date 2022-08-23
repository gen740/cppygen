#include <iostream>
#include <string>
#include <vector>

//! INCLUDE THIS HPP
#include "hoge.hpp"

namespace Shell {

//! hogehoge Function returns hoge
bool hogehoge(int hoge) { return hoge; }

//! SubA module is sub module of Shell
namespace subA {

struct Nyan {
  int neko;
  std::string cat;
  static int inu;
  double hoge(double x, double y) { return x + y; };
  enum HOGE { HOGE, FUGA, PIYO };
};

// 継承はなし
class Wan {
public:
  int wanwan;

private:
  int nyannyan;
};

auto return_vector(std::vector<double> a) { return a; }

int add(int x, int y) { return x + y; }

namespace subsubA {

std::string piyopiyo() { return "piyopiyo"; }

} // namespace subsubA

} // namespace subA

namespace subB {

void subBhoge() {}

} // namespace subB

void fugafuga() { std::cout << "Fuga" << std::endl; }

} // namespace Shell
