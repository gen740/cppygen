cmake_minimum_required(VERSION 3.20)

project(pyshell LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS on)

add_compile_options(-fPIC -std=c++20 -Wall -Wextra)

file(GLOB MAIN_SOURCES src/*.cpp)
file(GLOB SHELL_SOURCES shell/*.cpp)

find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG)

# Auto Generation
set(cppygen_generated_hpp ${CMAKE_CURRENT_BINARY_DIR}/cppygen_generated.hpp)
set(cppygen_generated_cpp ${CMAKE_CURRENT_BINARY_DIR}/cppygen_generated.cpp)
set(cppygen_config_file ${CMAKE_CURRENT_LIST_DIR}/cppygenconfig.toml)

find_program(_CPPYGEN_GENERATOR cppygen)
message(${cppygen_config_file})

add_custom_command(
  OUTPUT ${cppygen_generated_hpp} ${cppygen_generated_cpp}
  COMMAND
    ${_CPPYGEN_GENERATOR} ARGS #
    --config_file ${cppygen_config_file}#
    --cwd ${CMAKE_CURRENT_LIST_DIR} #
    --include_directories "hoeut;oetuh"
  DEPENDS ${SHELL_SOURCES} ${cppygen_config_file}
  COMMENT
    "Generating CPPyGen Code To ${cppygen_generated_hpp} and ${cppygen_generated_cpp}"
  VERBATIM)

pybind11_add_module(pyshell MODULE ${MAIN_SOURCES} ${SHELL_SOURCES}
                    ${cppygen_generated_cpp})

target_link_libraries(
  pyshell
  PUBLIC #
         pybind11::module #
         pybind11::lto #
         pybind11::windows_extras #
         ${MAIN_LINK_LIBRARIES})
target_include_directories(pyshell PRIVATE ${CMAKE_CURRENT_LIST_DIR}/shell
                                           ${CMAKE_CURRENT_BINARY_DIR})

# pybind11_extension(pyshell) pybind11_strip(pyshell)

set_target_properties(
  pyshell
  PROPERTIES #
             INTERPROCEDURAL_OPTIMIZATION ON
             CXX_VISIBILITY_PRESET "hidden"
             VISIBILITY_INLINES_HIDDEN ON)

# stub の生成も cmake を用いるといい find_program(_MYPY_STUBGEN stubgen)
# add_custom_command( TARGET pyshell POST_BUILD COMMAND ${_MYPY_STUBGEN} ARGS -p
# pyshell -o ${CMAKE_CURRENT_LIST_DIR}/python/stubs WORKING_DIRECTORY
# ${CMAKE_CURRENT_BINARY_DIR} )

# vim:sw=2
