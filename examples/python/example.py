#!/usr/bin/env python3
"""Minimal Python example using the installed package API."""

from __future__ import annotations

import json

from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly
from mystilink_horoscope.natal import calculate_chart, parse_local_datetime, to_serializable


def main() -> None:
    birth = "1990-06-15 14:30"
    tz = "Asia/Shanghai"
    lat, lon = 31.2304, 121.4737

    natal = to_serializable(
        calculate_chart(parse_local_datetime(birth, tz), lat, lon)
    )
    natal["kind"] = "natal"
    print(json.dumps({"sample": "natal_sun", "sun": next(
        p for p in natal["points"] if p["name"] == "Sun"
    )}, ensure_ascii=False, indent=2))

    daily = calculate_daily(birth, tz, lat, lon, "2026-09-12")
    print(json.dumps({
        "sample": "daily_summary",
        "summary": daily["summary"],
    }, ensure_ascii=False, indent=2))

    monthly = calculate_monthly(birth, tz, lat, lon, 2026, 9)
    print(json.dumps({
        "sample": "monthly_summary",
        "sun_sign_path": monthly["sun_sign_path"],
        "summary": monthly["summary"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
