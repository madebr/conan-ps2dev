cmake_minimum_required(VERSION 3.7)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_executable(cube cube.c)
target_link_libraries(cube PRIVATE draw graph math3d packet dma)

add_erl_executable(cube)
