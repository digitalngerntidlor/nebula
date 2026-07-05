"""Dagster resources shared across SEO GA4 assets."""

import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_gcp import BigQueryResource


@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "duckdb": DuckDBResource(database=dg.EnvVar("DUCKDB_PATH")),
            "bigquery": BigQueryResource(gcp_credentials=dg.EnvVar("GCP_SA_KEY_B64")),
        }
    )
