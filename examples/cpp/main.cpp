#include <iostream>
#include <vector>

#include "mystilink_horoscope.hpp"

int main() {
  try {
    std::string json = mystilink::horoscope::run({
        "version",
    });
    std::cout << json;
    json = mystilink::horoscope::run({
        "natal",
        "--datetime",
        "1990-06-15 14:30",
        "--timezone",
        "Asia/Shanghai",
        "--lat",
        "31.2304",
        "--lon",
        "121.4737",
    });
    std::cout << json;
  } catch (const std::exception &ex) {
    std::cerr << ex.what() << std::endl;
    return 1;
  }
  return 0;
}
