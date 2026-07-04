"""DuckDB-backed cache of per-day distinct GA4 user ids."""

from datetime import date

import duckdb

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ga4_active_users (
    event_date DATE NOT NULL,
    site VARCHAR NOT NULL,
    segment VARCHAR NOT NULL,
    user_pseudo_id VARCHAR NOT NULL,
    PRIMARY KEY (event_date, site, segment, user_pseudo_id)
)
"""

MONTHLY_AGGREGATE_SQL = """
WITH monthly_counts AS (
    SELECT
        SUBSTR(CAST(event_date AS VARCHAR), 1, 4) AS year_str,
        SUBSTR(CAST(event_date AS VARCHAR), 6, 2) AS month_str,
        site,
        segment,
        COUNT(DISTINCT user_pseudo_id) AS active_users
    FROM ga4_active_users
    GROUP BY 1, 2, 3, 4
)
SELECT
    year_str,
    month_str,
    COALESCE(MAX(CASE WHEN site = 'heygoody' AND segment = 'article' THEN active_users END), 0) AS active_users_article_heygoody,
    COALESCE(MAX(CASE WHEN site = 'heygoody' AND segment = 'product' THEN active_users END), 0) AS active_users_product_heygoody,
    COALESCE(MAX(CASE WHEN site = 'tidlor'   AND segment = 'article' THEN active_users END), 0) AS active_users_article_tidlor,
    COALESCE(MAX(CASE WHEN site = 'tidlor'   AND segment = 'product' THEN active_users END), 0) AS active_users_product_tidlor,
    COALESCE(MAX(CASE WHEN site = 'tidloh'   AND segment = 'article' THEN active_users END), 0) AS active_users_article_tidloh,
    COALESCE(MAX(CASE WHEN site = 'tidloh'   AND segment = 'product' THEN active_users END), 0) AS active_users_product_tidloh
FROM monthly_counts
GROUP BY year_str, month_str
ORDER BY year_str, month_str
"""


def ensure_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(CREATE_TABLE_SQL)


def refresh_active_users(
    conn: duckdb.DuckDBPyConnection,
    start_date: date,
    end_date: date,
    rows: list[tuple[date, str, str, str]],
) -> None:
    ensure_schema(conn)
    conn.execute("BEGIN TRANSACTION")
    try:
        conn.execute(
            "DELETE FROM ga4_active_users WHERE event_date BETWEEN ? AND ?",
            [start_date, end_date],
        )
        if rows:
            conn.executemany(
                "INSERT INTO ga4_active_users VALUES (?, ?, ?, ?)",
                rows,
            )
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def compute_month_aggregates(conn: duckdb.DuckDBPyConnection) -> list[dict]:
    ensure_schema(conn)
    result = conn.execute(MONTHLY_AGGREGATE_SQL)
    columns = [d[0] for d in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]
