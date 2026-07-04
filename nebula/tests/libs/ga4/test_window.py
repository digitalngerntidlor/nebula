from datetime import date

from nebula.libs.ga4.window import compute_window


def test_normal_run_uses_trailing_four_day_window():
    start_date, end_date = compute_window(date(2026, 7, 4), backfill=False)
    assert start_date == date(2026, 6, 30)
    assert end_date == date(2026, 7, 3)


def test_window_crosses_month_boundary_correctly():
    start_date, end_date = compute_window(date(2026, 7, 1), backfill=False)
    assert start_date == date(2026, 6, 27)
    assert end_date == date(2026, 6, 30)


def test_backfill_uses_full_history_start_date():
    start_date, end_date = compute_window(date(2026, 7, 4), backfill=True)
    assert start_date == date(2026, 1, 1)
    assert end_date == date(2026, 7, 3)
