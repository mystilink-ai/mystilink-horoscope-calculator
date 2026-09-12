package com.mystilink.horoscope;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Spawns mystilink-horoscope (or MYSTILINK_HOROSCOPE_CLI) and returns JSON stdout.
 */
public final class HoroscopeCli {
  private HoroscopeCli() {}

  public static String resolveCli() {
    String env = System.getenv("MYSTILINK_HOROSCOPE_CLI");
    if (env != null && !env.isBlank()) {
      return env;
    }
    return "mystilink-horoscope";
  }

  public static String run(String... args) throws Exception {
    List<String> command = new ArrayList<>();
    command.add(resolveCli());
    for (String a : args) {
      command.add(a);
    }
    ProcessBuilder pb = new ProcessBuilder(command);
    pb.redirectErrorStream(false);
    Process proc = pb.start();
    String stdout;
    String stderr;
    try (BufferedReader out = new BufferedReader(
            new InputStreamReader(proc.getInputStream(), StandardCharsets.UTF_8));
         BufferedReader err = new BufferedReader(
            new InputStreamReader(proc.getErrorStream(), StandardCharsets.UTF_8))) {
      StringBuilder sbOut = new StringBuilder();
      StringBuilder sbErr = new StringBuilder();
      String line;
      while ((line = out.readLine()) != null) {
        sbOut.append(line).append('\n');
      }
      while ((line = err.readLine()) != null) {
        sbErr.append(line).append('\n');
      }
      stdout = sbOut.toString();
      stderr = sbErr.toString();
    }
    int code = proc.waitFor();
    if (code != 0) {
      throw new IllegalStateException(stderr.isBlank() ? stdout : stderr);
    }
    return stdout;
  }

  public static String version() throws Exception {
    return run("version");
  }

  public static String natal(
      String datetime,
      String timezone,
      double lat,
      double lon,
      Map<String, String> options) throws Exception {
    List<String> args = new ArrayList<>();
    args.add("natal");
    args.add("--datetime");
    args.add(datetime);
    args.add("--timezone");
    args.add(timezone);
    args.add("--lat");
    args.add(Double.toString(lat));
    args.add("--lon");
    args.add(Double.toString(lon));
    if (options != null) {
      if (options.containsKey("houseSystem")) {
        args.add("--house-system");
        args.add(options.get("houseSystem"));
      }
      if (options.containsKey("zodiac")) {
        args.add("--zodiac");
        args.add(options.get("zodiac"));
      }
      if ("true".equalsIgnoreCase(options.getOrDefault("trueSolarTime", "false"))) {
        args.add("--true-solar-time");
      }
      if ("true".equalsIgnoreCase(options.getOrDefault("noAspects", "false"))) {
        args.add("--no-aspects");
      }
    }
    return run(args.toArray(new String[0]));
  }
}
