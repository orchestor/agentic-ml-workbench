import pytest

from py_orchestrator.gateway_client import GatewayClient
from py_orchestrator.tool_schemas.metrics import FetchRecentMetricsRequest


@pytest.mark.integration
def test_gateway_echo_roundtrip() -> None:
    client = GatewayClient()
    msg = "hello-from-py-orchestrator"
    echoed = client.echo(msg)
    assert echoed == msg


@pytest.mark.integration
def test_fetch_recent_metrics_stub() -> None:
    client = GatewayClient()
    req = FetchRecentMetricsRequest(
        metric_name="ctr",
        segment="new_users_us",
        baseline_window_minutes=60,
        current_window_minutes=30,
    )
    series = client.fetch_recent_metrics(req)

    assert series.metric_name == "ctr"
    assert series.segment == "new_users_us"
    assert series.baseline_window_minutes == 60
    assert series.current_window_minutes == 30
    assert series.absolute_drop != 0.0
    assert len(series.time_series) >= 1