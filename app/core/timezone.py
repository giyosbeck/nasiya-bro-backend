from datetime import datetime, timezone, timedelta
from typing import Optional

# Uzbekistan timezone (UTC+5)
UZBEKISTAN_TZ = timezone(timedelta(hours=5))

def uzbekistan_now() -> datetime:
    """Get current datetime in Uzbekistan timezone"""
    return datetime.now(UZBEKISTAN_TZ)

def uzbekistan_now_utc() -> datetime:
    """Get current Uzbekistan time but stored as UTC (for SQLite compatibility)"""
    # Get current time in Uzbekistan, then convert to UTC for storage
    uz_time = datetime.now(UZBEKISTAN_TZ)
    return uz_time.astimezone(timezone.utc)

def to_uzbekistan_time(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert datetime to Uzbekistan timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(UZBEKISTAN_TZ)

def from_uzbekistan_time(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert from Uzbekistan timezone to UTC"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume Uzbekistan timezone if no timezone info
        dt = dt.replace(tzinfo=UZBEKISTAN_TZ)
    return dt.astimezone(timezone.utc)