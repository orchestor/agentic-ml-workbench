from py_orchestrator.tool_schemas.metrics import MetricsPoint, MetricsSeries


def test_metrics_series_basic_shape() -> None:
    series = MetricsSeries(
        metric_name="ctr",
        segment="new_users_us",
        baseline_window_minutes=60,
        current_window_minutes=30,
        baseline_value=0.12,
        current_value=0.09,
        absolute_drop=-0.03,
        relative_drop_percent=-25.0,
        time_series=[
            MetricsPoint(timestamp="2026-05-02T11:00:00Z", value=0.12),
            MetricsPoint(timestamp="2026-05-02T11:05:00Z", value=0.11),
        ],
    )

    assert series.metric_name == "ctr"
    assert series.segment == "new_users_us"
    assert series.absolute_drop == -0.03
    assert series.time_series[0].timestamp.startswith("2026-05-02T11:00")