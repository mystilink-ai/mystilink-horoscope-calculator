"""Python binding that re-exports the library and optional CLI spawn helpers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Sequence

from mystilink_horoscope import __version__
from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly
from mystilink_horoscope.natal import calculate_chart, parse_local_datetime, to_serializable


def resolve_cli() -> str:
    env = os.environ.get("MYSTILINK_HOROSCOPE_CLI", "").strip()
    return env or "mystilink-horoscope"


def run_cli(args: Sequence[str]) -> dict[str, Any]:
    """Spawn CLI and parse JSON stdout."""
    proc = subprocess.run(
        [resolve_cli(), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "CLI failed")
    return json.loads(proc.stdout)


def version_via_cli() -> dict[str, Any]:
    return run_cli(["version"])


__all__ = [
    "__version__",
    "calculate_chart",
    "calculate_daily",
    "calculate_monthly",
    "parse_local_datetime",
    "resolve_cli",
    "run_cli",
    "to_serializable",
    "version_via_cli",
]
