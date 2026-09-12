# Thin C++ wrapper around the C CLI-spawning API.
cmake_minimum_required(VERSION 3.16)
project(mystilink_horoscope_cpp LANGUAGES CXX C)

add_library(mystilink_horoscope_c STATIC
  ../c/mystilink_horoscope.c
)
target_include_directories(mystilink_horoscope_c PUBLIC ../c)

add_library(mystilink_horoscope_cpp STATIC
  mystilink_horoscope.cpp
)
target_include_directories(mystilink_horoscope_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ../c)
target_link_libraries(mystilink_horoscope_cpp PUBLIC mystilink_horoscope_c)
