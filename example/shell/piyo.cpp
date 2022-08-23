#include "hoge.hpp"
#include "piyo.hpp"
#include <vector>

namespace Shell
{
Piyoyo make_piyoyo()
{
    Piyoyo tmp;
    tmp.setValue(-5);
    return tmp;
}
std::vector<double> fugafuga()
{
    return {3, 4, 5, 6};
}


}  // namespace Shell
