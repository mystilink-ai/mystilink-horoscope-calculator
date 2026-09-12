package com.mystilink.horoscope.example;

import com.mystilink.horoscope.HoroscopeCli;

public class Main {
  public static void main(String[] args) throws Exception {
    System.out.println(HoroscopeCli.version());
    System.out.println(
        HoroscopeCli.natal(
            "1990-06-15 14:30",
            "Asia/Shanghai",
            31.2304,
            121.4737,
            null));
  }
}
