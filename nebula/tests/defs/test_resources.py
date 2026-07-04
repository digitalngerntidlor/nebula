from nebula.defs.resources import resources


def test_resources_definitions_expose_duckdb_and_bigquery():
    defs = resources()
    assert set(defs.resources.keys()) == {"duckdb", "bigquery"}
