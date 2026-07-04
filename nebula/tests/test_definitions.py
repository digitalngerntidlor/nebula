from nebula.definitions import defs


def test_defs_loads_ga4_assets():
    definitions = defs()
    asset_keys = {key.to_user_string() for key in definitions.resolve_asset_graph().get_all_asset_keys()}
    assert "ga4_active_users" in asset_keys
    assert "traffic_and_conversion_cache" in asset_keys
