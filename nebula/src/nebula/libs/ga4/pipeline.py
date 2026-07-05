"""Orchestrates the GA4 active-user refresh and BigQuery merge using injected clients."""

from datetime import date
from typing import Any

import duckdb
from google.cloud import bigquery

from nebula.libs.ga4.cache import compute_month_aggregates, refresh_seo_active_users
from nebula.libs.ga4.query import build_ACTIVE_SEO_USERS_QUERY, build_merge_query
from nebula.libs.ga4.window import compute_window


def run_seo_active_users_refresh(
    client: bigquery.Client,
    conn: duckdb.DuckDBPyConnection,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("suffix_start", "STRING", start_date.replace("-", "")),
            bigquery.ScalarQueryParameter("suffix_end", "STRING", end_date.replace("-", "")),
        ]
    )
    print(build_ACTIVE_SEO_USERS_QUERY())
    query_job = client.query(build_ACTIVE_SEO_USERS_QUERY(), job_config=job_config)
    rows = [
        (row.event_date, row.site, row.segment, row.user_pseudo_id) for row in query_job.result()
    ]

    refresh_seo_active_users(conn, start_date, end_date, rows)

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "rows_cached": len(rows),
    }


def run_seo_traffic_conversion_merge(
    client: bigquery.Client,
    conn: duckdb.DuckDBPyConnection,
) -> dict[str, Any]:
    month_rows = compute_month_aggregates(conn)
    if not month_rows:
        return {"months_merged": 0}

    struct_params = [
        bigquery.StructQueryParameter(
            None,
            bigquery.ScalarQueryParameter("year_str", "STRING", row["year_str"]),
            bigquery.ScalarQueryParameter("month_str", "STRING", row["month_str"]),
            bigquery.ScalarQueryParameter(
                "active_users_article_heygoody", "INT64", row["active_users_article_heygoody"]
            ),
            bigquery.ScalarQueryParameter(
                "active_users_product_heygoody", "INT64", row["active_users_product_heygoody"]
            ),
            bigquery.ScalarQueryParameter(
                "active_users_article_tidlor", "INT64", row["active_users_article_tidlor"]
            ),
            bigquery.ScalarQueryParameter(
                "active_users_product_tidlor", "INT64", row["active_users_product_tidlor"]
            ),
            bigquery.ScalarQueryParameter(
                "active_users_article_tidloh", "INT64", row["active_users_article_tidloh"]
            ),
            bigquery.ScalarQueryParameter(
                "active_users_product_tidloh", "INT64", row["active_users_product_tidloh"]
            ),
        )
        for row in month_rows
    ]
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("rows", "STRUCT", struct_params)]
    )
    client.query(build_merge_query(), job_config=job_config).result()

    return {"months_merged": len(month_rows)}
