"""
Recurrence Calculator (T029)

Calculates next occurrence dates for recurring tasks based on
recurrence rules (frequency, interval, end_date, days_of_week).

Supports:
- Daily: Every N days
- Weekly: Every N weeks (optionally on specific days)
- Monthly: Every N months (same day of month)
"""
from datetime import datetime, timedelta
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def calculate_next_occurrence(
    current_due: datetime,
    frequency: str,
    interval: int = 1,
    end_date: Optional[datetime] = None,
    days_of_week: Optional[List[int]] = None
) -> Optional[datetime]:
    """
    Calculate the next occurrence date based on recurrence rule.

    Args:
        current_due: The current/completed task's due date
        frequency: "daily", "weekly", or "monthly"
        interval: Every N units (default: 1)
        end_date: Stop recurring after this date (optional)
        days_of_week: For weekly, specific days (0=Mon..6=Sun)

    Returns:
        Next occurrence datetime, or None if recurrence has ended

    Examples:
        # Daily task
        >>> calculate_next_occurrence(
        ...     datetime(2026, 1, 23, 9, 0),
        ...     frequency="daily",
        ...     interval=1
        ... )
        datetime(2026, 1, 24, 9, 0)

        # Weekly on Mon/Wed/Fri
        >>> calculate_next_occurrence(
        ...     datetime(2026, 1, 23, 9, 0),  # Thursday
        ...     frequency="weekly",
        ...     interval=1,
        ...     days_of_week=[0, 2, 4]  # Mon, Wed, Fri
        ... )
        datetime(2026, 1, 24, 9, 0)  # Friday
    """
    if not current_due:
        current_due = datetime.utcnow()

    next_due = None

    if frequency == "daily":
        next_due = _calculate_daily(current_due, interval)

    elif frequency == "weekly":
        next_due = _calculate_weekly(current_due, interval, days_of_week)

    elif frequency == "monthly":
        next_due = _calculate_monthly(current_due, interval)

    else:
        logger.warning(f"Unknown frequency: {frequency}")
        return None

    # Check if past end date
    if end_date and next_due and next_due > end_date:
        logger.info(f"Next occurrence {next_due} is past end date {end_date}")
        return None

    return next_due


def _calculate_daily(current: datetime, interval: int) -> datetime:
    """
    Calculate next daily occurrence.

    Args:
        current: Current due date
        interval: Every N days

    Returns:
        Next due date (current + N days)
    """
    return current + timedelta(days=interval)


def _calculate_weekly(
    current: datetime,
    interval: int,
    days_of_week: Optional[List[int]] = None
) -> datetime:
    """
    Calculate next weekly occurrence.

    If days_of_week specified, finds next matching day.
    Otherwise, same day next week (or N weeks).

    Args:
        current: Current due date
        interval: Every N weeks
        days_of_week: Specific days (0=Mon..6=Sun), optional

    Returns:
        Next due date
    """
    if not days_of_week:
        # Simple weekly: same day, N weeks later
        return current + timedelta(weeks=interval)

    # Weekly on specific days
    current_dow = current.weekday()  # 0=Mon..6=Sun

    # Sort days
    days_of_week = sorted(days_of_week)

    # Find next day in current week
    for dow in days_of_week:
        if dow > current_dow:
            days_ahead = dow - current_dow
            return current + timedelta(days=days_ahead)

    # No more days this week, go to first day of next week(s)
    first_day = days_of_week[0]
    days_until_next_week = 7 - current_dow + first_day
    weeks_to_add = (interval - 1) * 7
    return current + timedelta(days=days_until_next_week + weeks_to_add)


def _calculate_monthly(current: datetime, interval: int) -> datetime:
    """
    Calculate next monthly occurrence.

    Keeps same day of month. If day doesn't exist in target month
    (e.g., Jan 31 -> Feb), uses last day of month.

    Args:
        current: Current due date
        interval: Every N months

    Returns:
        Next due date
    """
    year = current.year
    month = current.month + interval

    # Handle year rollover
    while month > 12:
        month -= 12
        year += 1

    # Try to keep same day
    day = current.day
    while True:
        try:
            return datetime(
                year=year,
                month=month,
                day=day,
                hour=current.hour,
                minute=current.minute,
                second=current.second
            )
        except ValueError:
            # Day doesn't exist in this month, try previous day
            day -= 1
            if day < 1:
                # Shouldn't happen, but safety fallback
                return datetime(year, month, 1, current.hour, current.minute, current.second)


def get_occurrence_description(
    frequency: str,
    interval: int,
    days_of_week: Optional[List[int]] = None
) -> str:
    """
    Generate human-readable recurrence description.

    Args:
        frequency: "daily", "weekly", or "monthly"
        interval: Every N units
        days_of_week: For weekly (0=Mon..6=Sun)

    Returns:
        Human-readable string like "Every day" or "Every 2 weeks on Mon, Wed, Fri"
    """
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if frequency == "daily":
        if interval == 1:
            return "Every day"
        return f"Every {interval} days"

    elif frequency == "weekly":
        prefix = "Every week" if interval == 1 else f"Every {interval} weeks"
        if days_of_week:
            days_str = ", ".join(day_names[d] for d in sorted(days_of_week))
            return f"{prefix} on {days_str}"
        return prefix

    elif frequency == "monthly":
        if interval == 1:
            return "Every month"
        return f"Every {interval} months"

    return f"Every {interval} {frequency}"
