#include <pybind11/cast.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>

#include "pygen_generated.hpp"

void main_impl([[maybe_unused]] int argc, [[maybe_unused]] char *argv[]) {}

PYBIND11_MODULE(pyshell, m) {
  PyGen::PyGenExport(m);
}
