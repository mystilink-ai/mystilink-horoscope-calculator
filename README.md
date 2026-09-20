# Mystilink Horoscope Calculator

> Languages: [English](README.md) | [简体中文](README.zh-CN.md)

## Overview

Computes **natal charts**, **daily transit** summaries (transit planets vs natal), and **monthly** transit overviews. Output is structured JSON. Planetary positions use Swiss Ephemeris via `pyswisseph` (Moshier fallback when ephemeris files are unavailable).

This repository is a **calculation library / CLI**. It does not produce prose fortune essays.

## Platforms and languages

| Layer | Delivery |
|-------|----------|
| Python | Installable package `mystilink-horoscope-calculator` + library API |
| CLI | `horoscope` (natal / daily / monthly / version) |
| C | Header + source that spawn the CLI (`bindings/c`) |
| C++ | Thin wrapper over the C binding (`bindings/cpp`) |
| C# | .NET library spawning the CLI (`bindings/csharp`) |
| Java | Maven-layout class spawning the CLI (`bindings/java`) |
| JavaScript | npm package: Node spawn + browser factory with injected runner (`bindings/js`) |

Examples live under `examples/{c,cpp,csharp,java,js,node,python}/`.

Language bindings resolve the executable as `MYSTILINK_HOROSCOPE_CLI` if set, otherwise `horoscope` on `PATH`. Alias `mystilink-horoscope` remains installed.

## Requirements

- Python 3.9+
- Dependency: `pyswisseph` (declared in `pyproject.toml`)

## Install

From the repository root:

```bash
pip install -e .
```

This installs the library and the `horoscope` console script.

## CLI

All subcommands print UTF-8 JSON to stdout. Non-zero exit codes write errors to stderr.

### Natal

```bash
horoscope natal \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  [--house-system P] \
  [--zodiac tropical|sidereal] \
  [--sidereal-mode lahiri] \
  [--true-solar-time] \
  [--no-aspects]

horoscope natal --birth-json tests/fixtures/birth.profile.v0.json [--no-aspects]
```

Natal JSON includes `schema_version`: `mystilink.horoscope.natal/0.1`, plus legacy `points` and contract alias `planets`.

### Daily

Natal birth data plus a target calendar date. Transit time defaults to local noon (`12:00`); override with `--transit-time HH:MM`.

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

Response highlights: `transit_points`, `aspects_to_natal`, `summary.aspect_counts`, `summary.themes`, `summary.overall_tone`.

### Monthly

Samples the 1st, mid (15th or last), and last day of the month at local noon; aggregates Sun sign path and aspect pressure.

```bash
horoscope monthly \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --year 2026 \
  --month 9
```

### Version

```bash
horoscope version
```

## Python API

```python
from mystilink_horoscope.natal import calculate_chart, parse_local_datetime, to_serializable
from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly

dt = parse_local_datetime("1990-06-15 14:30", "Asia/Shanghai")
natal = to_serializable(calculate_chart(dt, 31.2304, 121.4737))
daily = calculate_daily(
    "1990-06-15 14:30", "Asia/Shanghai", 31.2304, 121.4737, "2026-09-12"
)
monthly = calculate_monthly(
    "1990-06-15 14:30", "Asia/Shanghai", 31.2304, 121.4737, 2026, 9
)
```

Or: `python -m mystilink_horoscope ...` (same CLI).

## Bindings usage (sketch)

- **C / C++**: link `bindings/c/mystilink_horoscope.c` and call `mystilink_horoscope_run`.
- **C#**: reference `bindings/csharp` and call `HoroscopeCli.Natal(...)`.
- **Java**: compile `bindings/java` and call `HoroscopeCli.natal(...)`.
- **Node**: `import { natal } from './bindings/js/src/node.js'`.
- **Browser**: `createClient({ run })` where `run(args)` must be supplied by the host (no in-browser process spawn).
- **Python binding helper**: `bindings/python/mystilink_horoscope_binding.py` (library + `run_cli`).

See `examples/` for runnable samples (CLI must be installed for spawn-based bindings).

## Schema

JSON Schema drafts for request/response shapes are under `schema/`.

## Tests / fixtures

Sample golden inputs live in `tests/fixtures/`. Run the Python example after install:

```bash
python examples/python/example.py
```

## Limits

- Requires `pyswisseph`. Without Swiss Ephemeris data files, calculation falls back to the Moshier method when possible.
- Coordinates are geographic latitude/longitude in degrees; timezone must be a valid IANA name.
- Theme scores in daily/monthly output are structured heuristics from aspect type and orb, not interpretive text.

## License

MIT. See [LICENSE](LICENSE).
