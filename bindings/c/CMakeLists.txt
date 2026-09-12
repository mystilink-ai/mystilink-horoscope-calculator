# Optional CMake build for the C binding static library.
cmake_minimum_required(VERSION 3.16)
project(mystilink_horoscope_c LANGUAGES C)

add_library(mystilink_horoscope STATIC mystilink_horoscope.c)
target_include_directories(mystilink_horoscope PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
