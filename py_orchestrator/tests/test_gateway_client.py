import pytest

from py_orchestrator.gateway_client import GatewayClient


@pytest.mark.integration
def test_gateway_echo_roundtrip() -> None:
    """
    This test assumes the Rust gateway is running locally on 127.0.0.1:8080.
    It is marked as 'integration' so we can choose when to run it.
    """
    client = GatewayClient()
    msg = "hello-from-py-orchestrator"
    echoed = client.echo(msg)
    assert echoed == msg