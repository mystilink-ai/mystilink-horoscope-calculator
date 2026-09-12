"""Daily fortune from transit positions versus natal chart."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from mystilink_horoscope.natal import (
    HARD_ASPECTS,
    SOFT_ASPECTS,
    Aspect,
    ChartPoint,
    aspect_to_dict,
    calculate_chart,
    calculate_cross_aspects,
    parse_local_datetime,
    point_to_dict,
    to_serializable,
)


THEME_KEYS = (
    "identity",
    "emotion",
    "communication",
    "relationship",
    "drive",
    "expansion",
    "structure",
)

PLANET_THEME = {
    "Sun": "identity",
    "Moon": "emotion",
    "Mercury": "communication",
    "Venus": "relationship",
    "Mars": "drive",
    "Jupiter": "expansion",
    "Saturn": "structure",
    "Uranus": "structure",
    "Neptune": "emotion",
    "Pluto": "drive",
    "TrueNode": "identity",
    "Chiron": "emotion",
}


def _strip_prefix(name: str, prefix: str) -> str:
    return name[len(prefix) :] if name.startswith(prefix) else name


def _aspect_counts(aspects: list[Aspect]) -> dict[str, int]:
    counts = Counter(a.aspect for a in aspects)
    return {name: int(counts.get(name, 0)) for name in (
        "Conjunction",
        "Opposition",
        "Square",
        "Trine",
        "Sextile",
    )}


def _theme_scores(aspects: list[Aspect]) -> dict[str, dict[str, Any]]:
    scores: dict[str, float] = {k: 0.0 for k in THEME_KEYS}
    hits: dict[str, int] = {k: 0 for k in THEME_KEYS}

    for a in aspects:
        natal_name = _strip_prefix(a.point_b, "n")
        theme = PLANET_THEME.get(natal_name, "identity")
        # Prefer tighter orbs; clamp weight into a stable range.
        weight = max(0.15, min(1.0, 1.0 - a.orb / 10.0))
        if a.aspect in HARD_ASPECTS:
            scores[theme] -= weight
        elif a.aspect in SOFT_ASPECTS:
            scores[theme] += weight
        hits[theme] += 1

    return {
        key: {
            "score": round(scores[key], 3),
            "aspect_hits": hits[key],
            "tone": (
                "supportive"
                if scores[key] > 0.35
                else "challenging"
                if scores[key] < -0.35
                else "mixed"
            ),
        }
        for key in THEME_KEYS
    }


def _parse_target_date(
    date_str: str,
    timezone_name: str,
    time_str: str | None = None,
) -> datetime:
    """Parse YYYY-MM-DD at noon (default) or HH:MM in the given timezone."""
    clock = time_str or "12:00"
    return parse_local_datetime(f"{date_str} {clock}", timezone_name)


def calculate_daily(
    birth_datetime: str,
    timezone_name: str,
    latitude: float,
    longitude: float,
    target_date: str,
    house_system: str = "P",
    zodiac_mode: str = "tropical",
    sidereal_mode: str = "lahiri",
    use_true_solar_time: bool = False,
    transit_time: str | None = None,
) -> dict[str, Any]:
    """
    Compute natal chart, transit sky for target date, and cross aspects.

    ``target_date`` is ``YYYY-MM-DD``. Transit time defaults to local noon
    unless ``transit_time`` (``HH:MM``) is provided.
    """
    natal_dt = parse_local_datetime(birth_datetime, timezone_name)
    transit_dt = _parse_target_date(target_date, timezone_name, transit_time)

    natal = calculate_chart(
        natal_dt,
        latitude,
        longitude,
        house_system=house_system,
        zodiac_mode=zodiac_mode,
        sidereal_mode=sidereal_mode,
        use_true_solar_time=use_true_solar_time,
        include_aspects=True,
    )
    transit = calculate_chart(
        transit_dt,
        latitude,
        longitude,
        house_system=house_system,
        zodiac_mode=zodiac_mode,
        sidereal_mode=sidereal_mode,
        use_true_solar_time=False,
        include_aspects=False,
    )

    natal_points: list[ChartPoint] = natal["points"]
    transit_points: list[ChartPoint] = transit["points"]
    aspects_to_natal = calculate_cross_aspects(transit_points, natal_points)
    counts = _aspect_counts(aspects_to_natal)
    themes = _theme_scores(aspects_to_natal)

    hard_count = sum(counts[k] for k in ("Conjunction", "Opposition", "Square"))
    soft_count = sum(counts[k] for k in ("Trine", "Sextile"))

    return {
        "kind": "daily",
        "target_date": target_date,
        "transit_datetime": transit["local_datetime"],
        "timezone": timezone_name,
        "natal": {
            "local_datetime": natal["local_datetime"],
            "asc": natal["asc"],
            "mc": natal["mc"],
            "points": [point_to_dict(p) for p in natal_points],
            "skipped_points": natal["skipped_points"],
        },
        "transit_points": [point_to_dict(p) for p in transit_points],
        "transit_asc": transit["asc"],
        "transit_mc": transit["mc"],
        "aspects_to_natal": [aspect_to_dict(a) for a in aspects_to_natal],
        "summary": {
            "aspect_counts": counts,
            "hard_aspect_count": hard_count,
            "soft_aspect_count": soft_count,
            "total_aspects": len(aspects_to_natal),
            "themes": themes,
            "overall_tone": (
                "supportive"
                if soft_count > hard_count + 1
                else "challenging"
                if hard_count > soft_count + 1
                else "mixed"
            ),
        },
        "meta": {
            "house_system": house_system.upper(),
            "zodiac_mode": zodiac_mode.lower(),
            "sidereal_mode": sidereal_mode if zodiac_mode.lower() == "sidereal" else None,
            "latitude": latitude,
            "longitude": longitude,
        },
    }


def natal_full_for_reference(
    birth_datetime: str,
    timezone_name: str,
    latitude: float,
    longitude: float,
    **kwargs: Any,
) -> dict[str, Any]:
    """Helper used by tests / callers that want the full natal payload."""
    natal_dt = parse_local_datetime(birth_datetime, timezone_name)
    return to_serializable(
        calculate_chart(natal_dt, latitude, longitude, **kwargs)
    )
