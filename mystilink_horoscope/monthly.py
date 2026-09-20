"""Monthly fortune overview from sampled transits versus natal chart."""

from __future__ import annotations

import calendar
from collections import Counter
from typing import Any

from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.natal import HARD_ASPECTS, parse_local_datetime, zodiac_from_longitude


def _sample_days(year: int, month: int) -> list[int]:
    """Key sample days: 1st, mid (15 or last), and last day of month."""
    last = calendar.monthrange(year, month)[1]
    days = [1]
    mid = min(15, last)
    if mid not in days:
        days.append(mid)
    if last not in days:
        days.append(last)
    return days


def calculate_monthly(
    birth_datetime: str,
    timezone_name: str,
    latitude: float,
    longitude: float,
    year: int,
    month: int,
    house_system: str = "P",
    zodiac_mode: str = "tropical",
    sidereal_mode: str = "lahiri",
    use_true_solar_time: bool = False,
) -> dict[str, Any]:
    """
    Monthly overview: sample transit charts on key dates, aggregate Sun signs
    and hard-aspect pressure versus the natal chart.
    """
    if not (1 <= month <= 12):
        raise ValueError("month must be in 1..12")
    if year < 1:
        raise ValueError("year must be positive")

    # Validate birth datetime early for clearer errors.
    parse_local_datetime(birth_datetime, timezone_name)

    sample_days = _sample_days(year, month)
    samples: list[dict[str, Any]] = []
    sun_signs: list[str] = []
    aspect_totals: Counter[str] = Counter()
    hard_total = 0
    soft_total = 0
    theme_accumulator: dict[str, float] = {}

    for day in sample_days:
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        daily = calculate_daily(
            birth_datetime=birth_datetime,
            timezone_name=timezone_name,
            latitude=latitude,
            longitude=longitude,
            target_date=date_str,
            house_system=house_system,
            zodiac_mode=zodiac_mode,
            sidereal_mode=sidereal_mode,
            use_true_solar_time=use_true_solar_time,
            transit_time="12:00",
        )
        sun = next((p for p in daily["transit_points"] if p["name"] == "Sun"), None)
        sun_sign = sun["sign"] if sun else None
        if sun_sign:
            sun_signs.append(sun_sign)

        counts = daily["summary"]["aspect_counts"]
        aspect_totals.update(counts)
        hard_total += daily["summary"]["hard_aspect_count"]
        soft_total += daily["summary"]["soft_aspect_count"]

        for theme, payload in daily["summary"]["themes"].items():
            theme_accumulator[theme] = theme_accumulator.get(theme, 0.0) + float(
                payload["score"]
            )

        samples.append(
            {
                "date": date_str,
                "sun_sign": sun_sign,
                "sun_longitude": sun["longitude"] if sun else None,
                "hard_aspect_count": daily["summary"]["hard_aspect_count"],
                "soft_aspect_count": daily["summary"]["soft_aspect_count"],
                "total_aspects": daily["summary"]["total_aspects"],
                "overall_tone": daily["summary"]["overall_tone"],
                "aspect_counts": counts,
            }
        )

    # Sun sign path through the month (ordered unique progression).
    sun_path: list[str] = []
    for sign in sun_signs:
        if not sun_path or sun_path[-1] != sign:
            sun_path.append(sign)

    n = max(len(samples), 1)
    theme_averages = {
        k: round(v / n, 3) for k, v in sorted(theme_accumulator.items())
    }
    dominant_theme = (
        max(theme_averages.items(), key=lambda kv: abs(kv[1]))[0]
        if theme_averages
        else None
    )

    mid_sample = samples[len(samples) // 2] if samples else None
    mid_sun_lon = mid_sample["sun_longitude"] if mid_sample else None
    mid_sun_sign = None
    mid_sun_degree = None
    if mid_sun_lon is not None:
        mid_sun_sign, mid_sun_degree = zodiac_from_longitude(mid_sun_lon)

    return {
        "schema_version": "mystilink.horoscope.monthly/0.1",
        "kind": "monthly",
        "year": year,
        "month": month,
        "timezone": timezone_name,
        "sample_dates": [s["date"] for s in samples],
        "samples": samples,
        "sun_sign_path": sun_path,
        "mid_month_sun": {
            "sign": mid_sun_sign,
            "sign_degree": mid_sun_degree,
            "longitude": mid_sun_lon,
        },
        "summary": {
            "aspect_counts_total": dict(aspect_totals),
            "hard_aspect_count_total": hard_total,
            "soft_aspect_count_total": soft_total,
            "avg_hard_aspects_per_sample": round(hard_total / n, 3),
            "avg_soft_aspects_per_sample": round(soft_total / n, 3),
            "theme_score_averages": theme_averages,
            "dominant_theme": dominant_theme,
            "overall_tone": (
                "supportive"
                if soft_total > hard_total + len(samples)
                else "challenging"
                if hard_total > soft_total + len(samples)
                else "mixed"
            ),
            "notable_hard_aspect_pressure": hard_total >= soft_total,
        },
        "meta": {
            "house_system": house_system.upper(),
            "zodiac_mode": zodiac_mode.lower(),
            "sidereal_mode": sidereal_mode if zodiac_mode.lower() == "sidereal" else None,
            "latitude": latitude,
            "longitude": longitude,
            "birth_datetime": birth_datetime,
            "hard_aspect_names": sorted(HARD_ASPECTS),
        },
    }
