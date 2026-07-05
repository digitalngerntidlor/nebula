"""SEO GA4 active-user cache assets.

Replaces the month-to-date BigQuery rescan in refesh_gq4_cache.sql with a
DuckDB cache of per-day distinct user ids, refreshed from a small trailing
BigQuery window each run.
"""

from datetime import date

import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_gcp import BigQueryResource

from nebula.libs.ga4.pipeline import run_seo_active_users_refresh, run_seo_traffic_conversion_merge
from utils import date_helper


class Ga4RefreshConfig(dg.Config):
    start_date: str = None
    end_date: str = None
    interval: int = None


@dg.asset(tags={"Team": "SEO", "Run-Type": "DAILY"})
def ga4_active_seo_users(
    config: Ga4RefreshConfig,
    duckdb: DuckDBResource,
    bigquery: BigQueryResource,
) -> dg.MaterializeResult:
    start_date, end_date = date_helper.generate_start_end_date(config.start_date, config.end_date, config.interval)
    with bigquery.get_client() as client, duckdb.get_connection() as conn:
        metadata = run_seo_active_users_refresh(
            client, conn, start_date=start_date, end_date=end_date
        )
    return dg.MaterializeResult(metadata=metadata)


@dg.asset(
    tags={"Team": "SEO", "Run-Type": "DAILY"},
    deps=[ga4_active_seo_users],
)
def traffic_and_conversion_cache(
    duckdb: DuckDBResource,
    bigquery: BigQueryResource,
) -> dg.MaterializeResult:
    with bigquery.get_client() as client, duckdb.get_connection() as conn:
        metadata = run_seo_traffic_conversion_merge(client, conn)
    return dg.MaterializeResult(metadata=metadata)


ga4_daily_refresh_job = dg.define_asset_job(
    "ga4_daily_refresh_job",
    selection=[ga4_active_seo_users, traffic_and_conversion_cache],
)

ga4_daily_refresh_schedule = dg.ScheduleDefinition(
    name="ga4_daily_refresh_schedule",
    job=ga4_daily_refresh_job,
    cron_schedule="0 12 * * *",
    execution_timezone="Asia/Bangkok",
)
