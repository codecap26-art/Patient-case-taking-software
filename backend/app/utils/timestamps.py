from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_iso(dt: datetime) -> str:
    return dt.isoformat()
