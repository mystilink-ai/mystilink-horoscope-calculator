# -*- coding: utf-8 -*-
"""BirthProfile and schema_version tests for horoscope calculator."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mystilink_horoscope.birth import parse_birth_profile
from mystilink_horoscope.natal import calculate_chart, parse_local_datetime, to_serializable

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mystilink_horoscope", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_parse_birth_profile_fixture() -> None:
    data = json.loads((FIXTURES / "birth.profile.v0.json").read_text(encoding="utf-8"))
    fields = parse_birth_profile(data)
    assert fields.datetime_str == "1990-06-15 14:30"
    assert fields.timezone == "Asia/Shanghai"
    assert fields.latitude == 31.23
    assert fields.longitude == 121.47


def test_natal_schema_version_and_planets_alias() -> None:
    local = parse_local_datetime("1990-06-15 14:30", "Asia/Shanghai")
    raw = calculate_chart(local, 31.23, 121.47, include_aspects=False)
    assert raw["schema_version"] == "mystilink.horoscope.natal/0.1"
    payload = to_serializable(raw)
    assert payload["planets"] == payload["points"]
    assert len(payload["points"]) >= 1


def test_cli_legacy_natal() -> None:
    proc = _run(
        "natal",
        "--datetime",
        "1990-06-15 14:30",
        "--timezone",
        "Asia/Shanghai",
        "--lat",
        "31.23",
        "--lon",
        "121.47",
        "--no-aspects",
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == "mystilink.horoscope.natal/0.1"
    assert data["kind"] == "natal"
    assert "planets" in data


def test_cli_birth_json_natal() -> None:
    path = FIXTURES / "birth.profile.v0.json"
    proc = _run("natal", "--birth-json", str(path), "--no-aspects")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == "mystilink.horoscope.natal/0.1"
    assert data["latitude"] == 31.23


def test_cli_version() -> None:
    proc = _run("version")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["version"] == "0.2.3"
    assert data.get("cli") == "horoscope"
