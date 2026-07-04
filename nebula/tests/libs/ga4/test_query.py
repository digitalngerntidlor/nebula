from nebula.libs.ga4.query import build_active_users_query, build_merge_query


def test_active_users_query_has_bind_params_and_all_property_segments():
    query = build_active_users_query()
    assert "@suffix_start" in query
    assert "@suffix_end" in query
    assert query.count("SELECT DISTINCT") == 6
    assert "'heygoody' AS site" in query
    assert "'tidlor' AS site" in query
    assert "'tidloh' AS site" in query
    assert "'article' AS segment" in query
    assert "'product' AS segment" in query
    assert "heygoody-450609.analytics_327162452.events_*" in query
    assert "ngerntidlor-440109.analytics_232252865.events_*" in query
    assert "ngerntidlor-440109.analytics_415907532.events_*" in query


def test_merge_query_targets_existing_cache_table_and_uses_rows_param():
    query = build_merge_query()
    assert "heygoody-450609.SEO.Traffic_and_Conversion_All_ga4_cache" in query
    assert "UNNEST(@rows)" in query
    assert "WHEN MATCHED THEN UPDATE" in query
    assert "WHEN NOT MATCHED THEN INSERT" in query
