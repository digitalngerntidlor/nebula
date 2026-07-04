import dagster as dg

from nebula.definitions import defs


def test_defs_loads_ga4_assets():
    definitions = defs()
    asset_keys = {key.to_user_string() for key in definitions.resolve_asset_graph().get_all_asset_keys()}
    assert "ga4_active_users" in asset_keys
    assert "traffic_and_conversion_cache" in asset_keys


def test_defs_loads_daily_schedule():
    definitions = defs()
    schedules_by_name = {schedule.name: schedule for schedule in definitions.schedules}
    schedule = schedules_by_name["ga4_daily_refresh_schedule"]

    assert schedule.default_status == dg.DefaultScheduleStatus.STOPPED
    assert schedule.cron_schedule == "0 2 * * *"
    assert schedule.execution_timezone == "Asia/Bangkok"
    assert schedule.job_name == "ga4_daily_refresh_job"
