"""Natal chart calculator using Swiss Ephemeris (pyswisseph)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

try:
    import swisseph as swe
except ImportError:  # pragma: no cover - optional until installed
    swe = None  # type: ignore[assignment]


ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

ASPECTS = {
    "Conjunction": {"angle": 0.0, "orb": 8.0, "abbr": "Conj"},
    "Opposition": {"angle": 180.0, "orb": 8.0, "abbr": "Opp"},
    "Square": {"angle": 90.0, "orb": 6.0, "abbr": "Sqr"},
    "Trine": {"angle": 120.0, "orb": 6.0, "abbr": "Tri"},
    "Sextile": {"angle": 60.0, "orb": 4.0, "abbr": "Sex"},
}

HARD_ASPECTS = {"Conjunction", "Opposition", "Square"}
SOFT_ASPECTS = {"Trine", "Sextile"}

SIDEREAL_MODE_NAMES = (
    "fagan-bradley",
    "lahiri",
    "deluce",
    "raman",
    "krishnamurti",
    "djwhal-khul",
    "yukteshwar",
    "jn-bhasin",
)


def _require_swe() -> Any:
    if swe is None:
        raise RuntimeError(
            "pyswisseph is required. Install the package with: pip install -e ."
        )
    return swe


def _sidereal_modes() -> dict[str, int]:
    s = _require_swe()
    return {
        "fagan-bradley": s.SIDM_FAGAN_BRADLEY,
        "lahiri": s.SIDM_LAHIRI,
        "deluce": s.SIDM_DELUCE,
        "raman": s.SIDM_RAMAN,
        "krishnamurti": s.SIDM_KRISHNAMURTI,
        "djwhal-khul": s.SIDM_DJWHAL_KHUL,
        "yukteshwar": s.SIDM_YUKTESHWAR,
        "jn-bhasin": s.SIDM_JN_BHASIN,
    }


def _planets() -> dict[str, int]:
    s = _require_swe()
    return {
        "Sun": s.SUN,
        "Moon": s.MOON,
        "Mercury": s.MERCURY,
        "Venus": s.VENUS,
        "Mars": s.MARS,
        "Jupiter": s.JUPITER,
        "Saturn": s.SATURN,
        "Uranus": s.URANUS,
        "Neptune": s.NEPTUNE,
        "Pluto": s.PLUTO,
        "TrueNode": s.TRUE_NODE,
        "Chiron": s.CHIRON,
    }


@dataclass
class ChartPoint:
    name: str
    longitude: float
    sign: str
    sign_degree: float
    house: int


@dataclass
class Aspect:
    point_a: str
    point_b: str
    aspect: str
    aspect_abbr: str
    angle: float
    exact_angle: float
    orb: float


def normalize_longitude(value: float) -> float:
    return value % 360.0


def zodiac_from_longitude(longitude: float) -> tuple[str, float]:
    lon = normalize_longitude(longitude)
    sign_index = int(lon // 30)
    sign_degree = lon - sign_index * 30
    return ZODIAC_SIGNS[sign_index], sign_degree


def house_from_longitude(longitude: float, house_cusps: list[float]) -> int:
    lon = normalize_longitude(longitude)
    cusps = [normalize_longitude(c) for c in house_cusps]
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start <= end:
            in_house = start <= lon < end
        else:
            in_house = lon >= start or lon < end
        if in_house:
            return i + 1
    return 12


def parse_local_datetime(value: str, tz_name: str) -> datetime:
    naive_dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
    return naive_dt.replace(tzinfo=ZoneInfo(tz_name))


def calculate_equation_of_time_minutes(local_dt: datetime) -> float:
    day_of_year = local_dt.timetuple().tm_yday
    hour_fraction = local_dt.hour + local_dt.minute / 60.0 + local_dt.second / 3600.0
    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour_fraction - 12.0) / 24.0)
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2.0 * gamma)
        - 0.040849 * math.sin(2.0 * gamma)
    )


def apply_true_solar_time(local_dt: datetime, longitude: float) -> tuple[datetime, float]:
    utc_offset = local_dt.utcoffset()
    if utc_offset is None:
        raise ValueError("Timezone offset is required to compute true solar time.")
    tz_offset_hours = utc_offset.total_seconds() / 3600.0
    eq_time = calculate_equation_of_time_minutes(local_dt)
    delta_minutes = eq_time + 4.0 * longitude - 60.0 * tz_offset_hours
    adjusted = local_dt + timedelta(minutes=delta_minutes)
    return adjusted, delta_minutes


def smallest_angular_distance(a: float, b: float) -> float:
    diff = abs(normalize_longitude(a) - normalize_longitude(b))
    return min(diff, 360.0 - diff)


def calculate_aspects(points: list[ChartPoint]) -> list[Aspect]:
    aspects: list[Aspect] = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            pa = points[i]
            pb = points[j]
            exact = smallest_angular_distance(pa.longitude, pb.longitude)
            for aspect_name, cfg in ASPECTS.items():
                orb = abs(exact - cfg["angle"])
                if orb <= cfg["orb"]:
                    aspects.append(
                        Aspect(
                            point_a=pa.name,
                            point_b=pb.name,
                            aspect=aspect_name,
                            aspect_abbr=cfg["abbr"],
                            angle=cfg["angle"],
                            exact_angle=exact,
                            orb=orb,
                        )
                    )
                    break
    return aspects


def calculate_cross_aspects(
    transit_points: list[ChartPoint],
    natal_points: list[ChartPoint],
) -> list[Aspect]:
    """Aspects between transit bodies and natal bodies (no same-set pairs)."""
    aspects: list[Aspect] = []
    for tp in transit_points:
        for np in natal_points:
            exact = smallest_angular_distance(tp.longitude, np.longitude)
            for aspect_name, cfg in ASPECTS.items():
                orb = abs(exact - cfg["angle"])
                if orb <= cfg["orb"]:
                    aspects.append(
                        Aspect(
                            point_a=f"t{tp.name}",
                            point_b=f"n{np.name}",
                            aspect=aspect_name,
                            aspect_abbr=cfg["abbr"],
                            angle=cfg["angle"],
                            exact_angle=exact,
                            orb=orb,
                        )
                    )
                    break
    return aspects


def point_to_dict(p: ChartPoint) -> dict[str, Any]:
    return {
        "name": p.name,
        "longitude": p.longitude,
        "sign": p.sign,
        "sign_degree": p.sign_degree,
        "house": p.house,
    }


def aspect_to_dict(a: Aspect) -> dict[str, Any]:
    return {
        "point_a": a.point_a,
        "point_b": a.point_b,
        "aspect": a.aspect,
        "aspect_abbr": a.aspect_abbr,
        "angle": a.angle,
        "exact_angle": a.exact_angle,
        "orb": a.orb,
    }


def to_serializable(result: dict) -> dict:
    serializable = dict(result)
    serializable["points"] = [point_to_dict(p) for p in result["points"]]
    serializable["planets"] = serializable["points"]  # contract alias (mystilink.horoscope.natal)
    serializable["aspects"] = [aspect_to_dict(a) for a in result["aspects"]]
    if "schema_version" not in serializable:
        serializable["schema_version"] = "mystilink.horoscope.natal/0.1"
    # Preferred contract field; keep zodiac_mode as legacy alias
    if "zodiac_mode" in serializable and "zodiac_system" not in serializable:
        serializable["zodiac_system"] = serializable["zodiac_mode"]
    return serializable


def calculate_chart(
    local_dt: datetime,
    latitude: float,
    longitude: float,
    house_system: str = "P",
    zodiac_mode: str = "tropical",
    sidereal_mode: str = "lahiri",
    use_true_solar_time: bool = False,
    include_aspects: bool = True,
) -> dict:
    s = _require_swe()

    effective_local_dt = local_dt
    true_solar_delta_minutes = 0.0
    if use_true_solar_time:
        effective_local_dt, true_solar_delta_minutes = apply_true_solar_time(
            local_dt, longitude
        )

    utc_dt = effective_local_dt.astimezone(timezone.utc)
    jd_ut = s.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )

    zodiac_mode = zodiac_mode.lower()
    sidereal_mode = sidereal_mode.lower()
    if zodiac_mode not in {"tropical", "sidereal"}:
        raise ValueError("zodiac_mode must be 'tropical' or 'sidereal'.")

    sidereal_modes = _sidereal_modes()
    sidereal_ayanamsa = 0.0
    if zodiac_mode == "sidereal":
        if sidereal_mode not in sidereal_modes:
            available_modes = ", ".join(sorted(sidereal_modes.keys()))
            raise ValueError(
                f"Unsupported sidereal mode '{sidereal_mode}'. Available: {available_modes}"
            )
        s.set_sid_mode(sidereal_modes[sidereal_mode], 0, 0)
        sidereal_ayanamsa = s.get_ayanamsa_ut(jd_ut)

    house_system_code = house_system.upper().encode("ascii")
    houses_result = s.houses_ex(jd_ut, latitude, longitude, house_system_code)
    house_cusps_tropical = list(houses_result[0][:12])
    ascmc = houses_result[1]
    asc_tropical = normalize_longitude(ascmc[0])
    mc_tropical = normalize_longitude(ascmc[1])

    if zodiac_mode == "sidereal":
        house_cusps = [
            normalize_longitude(cusp - sidereal_ayanamsa) for cusp in house_cusps_tropical
        ]
        asc = normalize_longitude(asc_tropical - sidereal_ayanamsa)
        mc = normalize_longitude(mc_tropical - sidereal_ayanamsa)
    else:
        house_cusps = house_cusps_tropical
        asc = asc_tropical
        mc = mc_tropical

    points: list[ChartPoint] = []
    skipped_points: list[str] = []
    flags = s.FLG_SWIEPH | s.FLG_SPEED
    if zodiac_mode == "sidereal":
        flags |= s.FLG_SIDEREAL

    for name, body in _planets().items():
        try:
            position, _retflags = s.calc_ut(jd_ut, body, flags)
        except s.Error:
            # Fallback to Moshier if Swiss ephemeris files are unavailable.
            fallback_flags = (flags & ~s.FLG_SWIEPH) | s.FLG_MOSEPH
            try:
                position, _retflags = s.calc_ut(jd_ut, body, fallback_flags)
            except s.Error:
                skipped_points.append(name)
                continue
        ecl_lon = normalize_longitude(position[0])
        sign, sign_degree = zodiac_from_longitude(ecl_lon)
        house = house_from_longitude(ecl_lon, house_cusps)
        points.append(
            ChartPoint(
                name=name,
                longitude=ecl_lon,
                sign=sign,
                sign_degree=sign_degree,
                house=house,
            )
        )

    aspects = calculate_aspects(points) if include_aspects else []
    asc_sign, asc_degree = zodiac_from_longitude(asc)
    mc_sign, mc_degree = zodiac_from_longitude(mc)

    return {
        "schema_version": "mystilink.horoscope.natal/0.1",
        "local_datetime": local_dt.isoformat(),
        "effective_local_datetime": effective_local_dt.isoformat(),
        "utc_datetime": utc_dt.isoformat(),
        "julian_day_ut": jd_ut,
        "latitude": latitude,
        "longitude": longitude,
        "house_system": house_system.upper(),
        "zodiac_mode": zodiac_mode,
        "sidereal_mode": sidereal_mode if zodiac_mode == "sidereal" else None,
        "ayanamsa": sidereal_ayanamsa if zodiac_mode == "sidereal" else None,
        "true_solar_time_enabled": use_true_solar_time,
        "true_solar_time_delta_minutes": true_solar_delta_minutes,
        "asc": {"longitude": asc, "sign": asc_sign, "sign_degree": asc_degree},
        "mc": {"longitude": mc, "sign": mc_sign, "sign_degree": mc_degree},
        "house_cusps": house_cusps,
        "points": points,
        "aspects": aspects,
        "skipped_points": skipped_points,
    }
