from datetime import date

import duckdb

from nebula.libs.ga4.cache import refresh_active_users
from nebula.libs.ga4.pipeline import run_active_users_refresh, run_traffic_conversion_merge


class _FakeRow:
    def __init__(self, event_date, site, segment, user_pseudo_id):
        self.event_date = event_date
        self.site = site
        self.segment = segment
        self.user_pseudo_id = user_pseudo_id


class _FakeQueryJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class _FakeBigQueryClient:
    def __init__(self, rows):
        self._rows = rows
        self.calls = []

    def query(self, query, job_config=None):
        self.calls.append((query, job_config))
        return _FakeQueryJob(self._rows)


def test_run_active_users_refresh_caches_rows_and_reports_window():
    conn = duckdb.connect(":memory:")
    fake_rows = [
        _FakeRow(date(2026, 7, 3), "heygoody", "article", "u1"),
        _FakeRow(date(2026, 7, 3), "heygoody", "article", "u2"),
    ]
    client = _FakeBigQueryClient(fake_rows)

    metadata = run_active_users_refresh(client, conn, today=date(2026, 7, 4), backfill=False)

    assert metadata == {
        "start_date": "2026-06-30",
        "end_date": "2026-07-03",
        "rows_cached": 2,
    }
    cached = conn.execute("SELECT COUNT(*) FROM ga4_active_users").fetchone()[0]
    assert cached == 2

    query, job_config = client.calls[0]
    assert "@suffix_start" in query
    param_values = {p.name: p.value for p in job_config.query_parameters}
    assert param_values == {"suffix_start": "20260630", "suffix_end": "20260703"}


def test_run_active_users_refresh_backfill_uses_full_history_window():
    conn = duckdb.connect(":memory:")
    client = _FakeBigQueryClient([])

    metadata = run_active_users_refresh(client, conn, today=date(2026, 7, 4), backfill=True)

    assert metadata["start_date"] == "2026-01-01"
    assert metadata["end_date"] == "2026-07-03"


def test_run_traffic_conversion_merge_sends_pivoted_struct_rows():
    conn = duckdb.connect(":memory:")
    refresh_active_users(
        conn,
        date(2026, 7, 1),
        date(2026, 7, 1),
        [
            (date(2026, 7, 1), "heygoody", "article", "u1"),
            (date(2026, 7, 1), "heygoody", "article", "u2"),
        ],
    )
    client = _FakeBigQueryClient([])

    metadata = run_traffic_conversion_merge(client, conn)

    assert metadata == {"months_merged": 1}
    query, job_config = client.calls[0]
    assert "MERGE" in query
    array_param = job_config.query_parameters[0]
    assert array_param.name == "rows"
    assert len(array_param.values) == 1
    struct_values = array_param.values[0].struct_values
    assert struct_values["year_str"] == "2026"
    assert struct_values["month_str"] == "07"
    assert struct_values["active_users_article_heygoody"] == 2
    assert struct_values["active_users_product_heygoody"] == 0


def test_run_traffic_conversion_merge_no_op_when_no_cached_rows():
    conn = duckdb.connect(":memory:")
    client = _FakeBigQueryClient([])

    metadata = run_traffic_conversion_merge(client, conn)

    assert metadata == {"months_merged": 0}
    assert client.calls == []
