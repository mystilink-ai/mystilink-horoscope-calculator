# -*- coding: utf-8 -*-
"""Validate horoscope outputs against shared mystilink-metaphysics-schema when present."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly
from mystilink_horoscope.natal import calculate_chart, to_serializable

SCHEMA_ROOT = (
    Path(__file__).resolve().parents[2] / "mystilink-metaphysics-schema" / "schemas" / "v0"
)


def _shared_available() -> bool:
    return (SCHEMA_ROOT / "systems" / "horoscope.natal.schema.json").is_file()


def _registry_and_validator(name: str):
    pytest.importorskip("jsonschema")
    pytest.importorskip("referencing")
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    registry = Registry()
    for path in SCHEMA_ROOT.rglob("*.schema.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            data["$id"],
            Resource.from_contents(data, default_specification=DRAFT202012),
        )
    schema = json.loads((SCHEMA_ROOT / "systems" / name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=registry)


@pytest.mark.skipif(not _shared_available(), reason="sibling mystilink-metaphysics-schema not present")
def test_natal_validates_shared_schema() -> None:
    local = datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    out = to_serializable(calculate_chart(local, 31.2, 121.5))
    out["kind"] = "natal"
    assert out["zodiac_system"] == out["zodiac_mode"] == "tropical"
    _registry_and_validator("horoscope.natal.schema.json").validate(out)


@pytest.mark.skipif(not _shared_available(), reason="sibling mystilink-metaphysics-schema not present")
def test_daily_validates_shared_schema() -> None:
    out = calculate_daily(
        birth_datetime="1990-05-15 14:30",
        timezone_name="Asia/Shanghai",
        latitude=31.2,
        longitude=121.5,
        target_date="2024-06-01",
    )
    _registry_and_validator("horoscope.daily.schema.json").validate(out)


@pytest.mark.skipif(not _shared_available(), reason="sibling mystilink-metaphysics-schema not present")
def test_monthly_validates_shared_schema() -> None:
    out = calculate_monthly(
        birth_datetime="1990-05-15 14:30",
        timezone_name="Asia/Shanghai",
        latitude=31.2,
        longitude=121.5,
        year=2024,
        month=6,
    )
    _registry_and_validator("horoscope.monthly.schema.json").validate(out)
