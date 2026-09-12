#pragma once

#include "mystilink_horoscope.h"

#include <stdexcept>
#include <string>
#include <vector>

namespace mystilink {
namespace horoscope {

inline std::string run(const std::vector<std::string> &args) {
  std::vector<const char *> argv;
  argv.reserve(args.size() + 1);
  for (const auto &a : args) {
    argv.push_back(a.c_str());
  }
  argv.push_back(nullptr);

  char *out = nullptr;
  int rc = mystilink_horoscope_run(argv.data(), &out);
  std::string json = out ? out : "";
  free(out);
  if (rc != 0) {
    throw std::runtime_error(
        json.empty() ? "mystilink-horoscope CLI failed" : json);
  }
  return json;
}

inline std::string version() { return run({"version"}); }

}  // namespace horoscope
}  // namespace mystilink
