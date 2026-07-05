# nebula

## Getting started

### Installing dependencies

**Option 1: uv**

Ensure [`uv`](https://docs.astral.sh/uv/) is installed following their [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

Create a virtual environment, and install the required dependencies using _sync_:

```bash
uv sync
```

Then, activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

**Option 2: pip**

Install the python dependencies with [pip](https://pypi.org/project/pip/):

```bash
python3 -m venv .venv
```

Then activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

Install the required dependencies:

```bash
pip install -e ".[dev]"
```

### Running Dagster

Start the Dagster UI web server:

```bash
dg dev
```

Open http://localhost:3000 in your browser to see the project.

## Learn more

To learn more about this template and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)

## GA4 active-user cache cutover

Before the `ga4_daily_refresh_schedule` replaces the legacy `traffic-cache-refresh` Cloud Run Job (`refesh_gq4_cache.sql`), complete this one-time sequence:

1. Set the required environment: `DUCKDB_PATH` (a persistent local path for the DuckDB cache file) and `GOOGLE_APPLICATION_CREDENTIALS` (service account key with BigQuery access).
2. Materialize `ga4_active_seo_users` **once** with run config `backfill: true` to populate the DuckDB cache with full history (from 2026-01-01) before any daily run — since DuckDB starts empty, a normal trailing-4-day run before this would only see the last 4 days and overwrite the legacy table's correct month-to-date values with an undercount.
3. Disable/decommission the legacy `traffic-cache-refresh` Cloud Run Job — both systems `MERGE` into the same BigQuery table (`heygoody-450609.SEO.Traffic_and_Conversion_All_ga4_cache`), so running both concurrently causes them to overwrite each other's writes.
4. Only after 1–3, enable the `ga4_daily_refresh_schedule` schedule in the Dagster UI (it deploys in a stopped state by default).
