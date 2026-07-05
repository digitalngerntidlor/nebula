"""Computes the BigQuery date window to refresh into the GA4 active-user cache."""

from datetime import date, timedelta

BACKFILL_START_DATE = date(2026, 7, 3)
TRAILING_WINDOW_DAYS = 4


def compute_window(today: date, backfill: bool = False) -> tuple[date, date]:
    yesterday = today - timedelta(days=1)
    if backfill:
        return BACKFILL_START_DATE, yesterday
    start_date = yesterday - timedelta(days=TRAILING_WINDOW_DAYS - 1)
    return start_date, yesterday
