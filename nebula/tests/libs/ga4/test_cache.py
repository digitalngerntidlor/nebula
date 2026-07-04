from datetime import date

import duckdb
import pytest

from nebula.libs.ga4.cache import compute_month_aggregates, refresh_active_users


def _connection():
    return duckdb.connect(":memory:")


def test_refresh_active_users_replaces_overlapping_window():
    conn = _connection()
    refresh_active_users(
        conn,
        date(2026, 6, 27),
        date(2026, 6, 30),
        [
            (date(2026, 6, 28), "heygoody", "article", "stale-user"),
        ],
    )
    refresh_active_users(
        conn,
        date(2026, 6, 30),
        date(2026, 7, 3),
        [
            (date(2026, 7, 1), "heygoody", "article", "u1"),
            (date(2026, 7, 1), "heygoody", "article", "u2"),
        ],
    )

    rows = conn.execute(
        "SELECT event_date, site, segment, user_pseudo_id FROM ga4_active_users "
        "ORDER BY event_date, user_pseudo_id"
    ).fetchall()

    assert rows == [
        (date(2026, 6, 28), "heygoody", "article", "stale-user"),
        (date(2026, 7, 1), "heygoody", "article", "u1"),
        (date(2026, 7, 1), "heygoody", "article", "u2"),
    ]


def test_refresh_active_users_is_idempotent_for_same_window():
    conn = _connection()
    rows_in = [(date(2026, 7, 1), "tidlor", "product", "u1")]
    refresh_active_users(conn, date(2026, 7, 1), date(2026, 7, 1), rows_in)
    refresh_active_users(conn, date(2026, 7, 1), date(2026, 7, 1), rows_in)

    count = conn.execute("SELECT COUNT(*) FROM ga4_active_users").fetchone()[0]
    assert count == 1


def test_compute_month_aggregates_pivots_distinct_counts_per_site_segment():
    conn = _connection()
    refresh_active_users(
        conn,
        date(2026, 7, 1),
        date(2026, 7, 2),
        [
            (date(2026, 7, 1), "heygoody", "article", "u1"),
            (date(2026, 7, 1), "heygoody", "article", "u2"),
            (date(2026, 7, 2), "heygoody", "article", "u1"),
            (date(2026, 7, 1), "heygoody", "product", "u3"),
            (date(2026, 7, 1), "tidlor", "article", "u4"),
        ],
    )

    rows = compute_month_aggregates(conn)

    assert rows == [
        {
            "year_str": "2026",
            "month_str": "07",
            "active_users_article_heygoody": 2,
            "active_users_product_heygoody": 1,
            "active_users_article_tidlor": 1,
            "active_users_product_tidlor": None,
            "active_users_article_tidloh": None,
            "active_users_product_tidloh": None,
        }
    ]


def test_refresh_active_users_rolls_back_on_constraint_violation():
    conn = _connection()
    refresh_active_users(
        conn,
        date(2026, 7, 1),
        date(2026, 7, 1),
        [(date(2026, 7, 1), "heygoody", "article", "existing-user")],
    )

    with pytest.raises(duckdb.Error):
        refresh_active_users(
            conn,
            date(2026, 7, 1),
            date(2026, 7, 1),
            [
                (date(2026, 7, 1), "heygoody", "article", "dup-user"),
                (date(2026, 7, 1), "heygoody", "article", "dup-user"),
            ],
        )

    rows = conn.execute(
        "SELECT event_date, site, segment, user_pseudo_id FROM ga4_active_users"
    ).fetchall()
    assert rows == [(date(2026, 7, 1), "heygoody", "article", "existing-user")]
