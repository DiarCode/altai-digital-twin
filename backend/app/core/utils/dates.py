from __future__ import annotations
from datetime import datetime, date, time, timezone
from typing import Optional


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def date_to_datetime_min(d: date) -> datetime:
    return datetime.combine(d, time.min).replace(tzinfo=timezone.utc)


def date_to_datetime_max(d: date) -> datetime:
    return datetime.combine(d, time.max).replace(tzinfo=timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return to_utc(dt).isoformat()
