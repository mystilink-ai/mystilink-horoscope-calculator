"""CLI for natal, daily, and monthly horoscope calculations. JSON on stdout."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional, Tuple

from mystilink_horoscope import __version__
from mystilink_horoscope.birth import BirthProfileError, load_json_arg, parse_birth_profile
from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly
from mystilink_horoscope.natal import (
    SIDEREAL_MODE_NAMES,
    calculate_chart,
    parse_local_datetime,
    to_serializable,
)


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _emit_error(message: str, code: int = 2) -> int:
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    return code


def _add_birth_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--datetime",
        required=False,
        default=None,
        help='Birth local datetime "YYYY-MM-DD HH:MM" (required unless --birth-json)',
    )
    parser.add_argument(
        "--timezone",
        required=False,
        default=None,
        help="IANA timezone name (required unless --birth-json)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        required=False,
        default=None,
        help="Latitude degrees (required unless BirthProfile place.lat)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        required=False,
        default=None,
        help="Longitude degrees east positive (required unless BirthProfile)",
    )
    parser.add_argument(
        "--house-system",
        default="P",
        help="House system code (default: P Placidus)",
    )
    parser.add_argument(
        "--zodiac",
        choices=["tropical", "sidereal"],
        default="tropical",
        help="Zodiac mode (default: tropical)",
    )
    parser.add_argument(
        "--sidereal-mode",
        default="lahiri",
        choices=list(SIDEREAL_MODE_NAMES),
        help="Sidereal ayanamsa when --zodiac sidereal (default: lahiri)",
    )
    parser.add_argument(
        "--true-solar-time",
        action="store_true",
        help="Apply true solar time correction to birth time",
    )
    parser.add_argument(
        "--birth-json",
        type=str,
        default=None,
        help=(
            "BirthProfile JSON (mystilink.birth/0.1): file path, '-' for stdin, "
            "or inline JSON"
        ),
    )


def _resolve_birth(
    args: argparse.Namespace,
) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[float], bool, Optional[str]]:
    """Return (datetime, timezone, lat, lon, true_solar, error)."""
    datetime_str = args.datetime
    timezone = args.timezone
    lat = args.lat
    lon = args.lon
    true_solar = bool(args.true_solar_time)

    if args.birth_json:
        try:
            profile = parse_birth_profile(load_json_arg(args.birth_json))
        except (BirthProfileError, OSError) as exc:
            return None, None, None, None, False, str(exc)
        datetime_str = profile.datetime_str
        if timezone is None:
            timezone = profile.timezone
        if lat is None:
            lat = profile.latitude
        if lon is None:
            lon = profile.longitude
        if profile.true_solar_time:
            true_solar = True

    if not datetime_str or not timezone:
        return None, None, None, None, False, (
            "either --datetime/--timezone/--lat/--lon or --birth-json is required"
        )
    if lat is None or lon is None:
        return None, None, None, None, False, (
            "latitude and longitude are required (CLI flags or BirthProfile place/birth)"
        )
    return datetime_str, timezone, lat, lon, true_solar, None


def _cmd_natal(args: argparse.Namespace) -> int:
    datetime_str, timezone, lat, lon, true_solar, err = _resolve_birth(args)
    if err:
        return _emit_error(err)

    try:
        local_dt = parse_local_datetime(datetime_str, timezone)  # type: ignore[arg-type]
    except Exception as exc:
        return _emit_error(f"Invalid datetime/timezone: {exc}")

    try:
        result = calculate_chart(
            local_dt,
            lat,  # type: ignore[arg-type]
            lon,  # type: ignore[arg-type]
            house_system=args.house_system,
            zodiac_mode=args.zodiac,
            sidereal_mode=args.sidereal_mode,
            use_true_solar_time=true_solar,
            include_aspects=not args.no_aspects,
        )
    except Exception as exc:
        return _emit_error(f"Calculation failed: {exc}", code=1)

    payload = to_serializable(result)
    payload["kind"] = "natal"
    _emit(payload)
    return 0


def _cmd_daily(args: argparse.Namespace) -> int:
    datetime_str, timezone, lat, lon, true_solar, err = _resolve_birth(args)
    if err:
        return _emit_error(err)
    try:
        payload = calculate_daily(
            birth_datetime=datetime_str,  # type: ignore[arg-type]
            timezone_name=timezone,  # type: ignore[arg-type]
            latitude=lat,  # type: ignore[arg-type]
            longitude=lon,  # type: ignore[arg-type]
            target_date=args.date,
            house_system=args.house_system,
            zodiac_mode=args.zodiac,
            sidereal_mode=args.sidereal_mode,
            use_true_solar_time=true_solar,
            transit_time=args.transit_time,
        )
    except Exception as exc:
        return _emit_error(f"Calculation failed: {exc}", code=1)
    _emit(payload)
    return 0


def _cmd_monthly(args: argparse.Namespace) -> int:
    datetime_str, timezone, lat, lon, true_solar, err = _resolve_birth(args)
    if err:
        return _emit_error(err)
    try:
        payload = calculate_monthly(
            birth_datetime=datetime_str,  # type: ignore[arg-type]
            timezone_name=timezone,  # type: ignore[arg-type]
            latitude=lat,  # type: ignore[arg-type]
            longitude=lon,  # type: ignore[arg-type]
            year=args.year,
            month=args.month,
            house_system=args.house_system,
            zodiac_mode=args.zodiac,
            sidereal_mode=args.sidereal_mode,
            use_true_solar_time=true_solar,
        )
    except Exception as exc:
        return _emit_error(f"Calculation failed: {exc}", code=1)
    _emit(payload)
    return 0


def _cmd_version(_: argparse.Namespace) -> int:
    _emit({"name": "mystilink-horoscope-calculator", "version": __version__, "cli": "horoscope"})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="horoscope",
        description="Natal chart, daily transit, and monthly overview calculator.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_natal = sub.add_parser("natal", help="Calculate natal chart JSON")
    _add_birth_args(p_natal)
    p_natal.add_argument(
        "--no-aspects",
        action="store_true",
        help="Omit major natal aspects",
    )
    p_natal.set_defaults(func=_cmd_natal)

    p_daily = sub.add_parser(
        "daily",
        help="Transit sky for a date vs natal; aspects and theme scores",
    )
    _add_birth_args(p_daily)
    p_daily.add_argument(
        "--date",
        required=True,
        help="Target date YYYY-MM-DD",
    )
    p_daily.add_argument(
        "--transit-time",
        default=None,
        help="Optional transit local time HH:MM (default: 12:00)",
    )
    p_daily.set_defaults(func=_cmd_daily)

    p_monthly = sub.add_parser(
        "monthly",
        help="Monthly overview from sampled transits vs natal",
    )
    _add_birth_args(p_monthly)
    p_monthly.add_argument("--year", type=int, required=True, help="Target year")
    p_monthly.add_argument("--month", type=int, required=True, help="Target month 1-12")
    p_monthly.set_defaults(func=_cmd_monthly)

    p_ver = sub.add_parser("version", help="Print version JSON")
    p_ver.set_defaults(func=_cmd_version)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
