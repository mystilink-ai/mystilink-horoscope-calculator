# -*- coding: utf-8 -*-
"""Parse mystilink.birth/0.1 BirthProfile JSON (no runtime schema package dependency)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class BirthProfileError(ValueError):
    """Invalid BirthProfile document."""


@dataclass(frozen=True)
class BirthProfileFields:
    """Wall-clock birth fields extracted from a BirthProfile document."""

    datetime_str: str  # "YYYY-MM-DD HH:MM"
    timezone: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    true_solar_time: bool = False


def load_json_arg(raw: str) -> Dict[str, Any]:
    """Load JSON from a file path, '-' (stdin), or an inline JSON string."""
    import json
    import sys

    if raw == "-":
        text = sys.stdin.read()
    else:
        path = Path(raw)
        text = path.read_text(encoding="utf-8") if path.is_file() else raw
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BirthProfileError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise BirthProfileError("JSON root must be an object")
    return data


def parse_birth_profile(data: Dict[str, Any]) -> BirthProfileFields:
    """Accept mystilink.birth/0.1. Lat/lon from birth or place."""
    if not isinstance(data, dict):
        raise BirthProfileError("birth profile must be a JSON object")

    version = data.get("schema_version")
    if version is not None and version != "mystilink.birth/0.1":
        raise BirthProfileError(
            f"unsupported schema_version {version!r}; expected mystilink.birth/0.1"
        )

    birth = data.get("birth")
    if not isinstance(birth, dict):
        raise BirthProfileError("birth object is required")

    timezone = birth.get("timezone")
    if not timezone or not isinstance(timezone, str):
        raise BirthProfileError("birth.timezone is required (IANA name)")

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise BirthProfileError(f"unknown IANA timezone: {timezone!r}") from exc

    dt_raw = birth.get("datetime")
    if not isinstance(dt_raw, str) or not dt_raw.strip():
        raise BirthProfileError("birth.datetime is required (ISO-8601 with offset)")

    try:
        normalized = dt_raw.strip().replace("Z", "+00:00")
        instant = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise BirthProfileError(f"invalid birth.datetime: {dt_raw!r}") from exc

    if instant.tzinfo is None:
        raise BirthProfileError("birth.datetime must include a timezone offset")

    datetime_str = (
        f"{instant.year:04d}-{instant.month:02d}-{instant.day:02d} "
        f"{instant.hour:02d}:{instant.minute:02d}"
    )

    longitude: Optional[float] = None
    latitude: Optional[float] = None
    if birth.get("longitude") is not None:
        try:
            longitude = float(birth["longitude"])
        except (TypeError, ValueError) as exc:
            raise BirthProfileError("birth.longitude must be a number") from exc

    place = data.get("place")
    if isinstance(place, dict):
        if longitude is None and place.get("lon") is not None:
            try:
                longitude = float(place["lon"])
            except (TypeError, ValueError) as exc:
                raise BirthProfileError("place.lon must be a number") from exc
        if place.get("lat") is not None:
            try:
                latitude = float(place["lat"])
            except (TypeError, ValueError) as exc:
                raise BirthProfileError("place.lat must be a number") from exc

    return BirthProfileFields(
        datetime_str=datetime_str,
        timezone=timezone,
        longitude=longitude,
        latitude=latitude,
        true_solar_time=bool(birth.get("true_solar_time")),
    )
