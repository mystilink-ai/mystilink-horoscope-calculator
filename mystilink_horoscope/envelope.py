"""Optional mystilink.envelope/0.1 wrapping helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


ENVELOPE_VERSION = "mystilink.envelope/0.1"
BIRTH_VERSION = "mystilink.birth/0.1"


def build_subject(
    *,
    birth_profile: Optional[Dict[str, Any]] = None,
    datetime_iso: Optional[str] = None,
    timezone_name: Optional[str] = None,
    gender: Optional[str] = None,
    longitude: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    if isinstance(birth_profile, dict) and birth_profile.get("schema_version") == BIRTH_VERSION:
        return birth_profile
    if not datetime_iso or not timezone_name:
        return None
    birth: Dict[str, Any] = {
        "datetime": datetime_iso,
        "timezone": timezone_name,
    }
    if longitude is not None:
        birth["longitude"] = longitude
    subject: Dict[str, Any] = {
        "schema_version": BIRTH_VERSION,
        "birth": birth,
    }
    if gender in ("male", "female", "unspecified"):
        subject["gender"] = gender
    return subject


def wrap_envelope(
    *,
    system: str,
    chart: Dict[str, Any],
    subject: Optional[Dict[str, Any]] = None,
    calendar_basis: Optional[Dict[str, Any]] = None,
    locale: Optional[str] = None,
    produced_by: Optional[str] = None,
    interpretation: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "schema_version": ENVELOPE_VERSION,
        "system": system,
        "chart": chart,
    }
    if subject is not None:
        out["subject"] = subject
    if calendar_basis is not None:
        out["calendar_basis"] = calendar_basis
    if locale:
        out["locale"] = locale
    if interpretation is not None:
        out["interpretation"] = interpretation
    meta: Dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    if produced_by:
        meta["produced_by"] = produced_by
    if request_id:
        meta["request_id"] = request_id
    out["meta"] = meta
    return out


def structured_error(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        err["details"] = details
    return {"error": err}
