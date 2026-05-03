from py_orchestrator.agent_log import (
    AgentAction,
    AgentClassification,
    AgentContext,
    AgentIds,
    AgentLogEvent,
    AgentObservation,
    AgentSource,
    ObservationEvidence,
    to_ndjson_lines,
)


def test_agent_log_event_to_ndjson() -> None:
    event = AgentLogEvent(
        level="ERROR",
        event="gateway.echo_failed",
        ids=AgentIds(
            run_id="run_123",
            task_id="task_456",
            trace_id="trace_abc",
            span_id="span_def",
        ),
        source=AgentSource(
            service="py_orchestrator",
            component="gateway_client",
            function="GatewayClient.echo",
            env="dev",
        ),
        context=AgentContext(
            intent="investigate metric drop",
            segment="premium_users",
            layer="gateway",
            step="connectivity_smoke_test",
        ),
        observation=AgentObservation(
            summary="Gateway echo failed during planning smoke test.",
            raw_message="ReadTimeout after 3000ms",
            evidence=ObservationEvidence(
                latency_ms=3100,
                timeout_ms=3000,
                http_status=None,
                extra={"attempt": 1},
            ),
        ),
        classification=AgentClassification(
            error_code="GATEWAY_TIMEOUT",
            severity="recoverable",
            retryable=True,
            confidence=None,
        ),
        action=AgentAction(
            taken="record_error_and_continue",
            next_suggested="retry_gateway_or_continue_without_echo",
        ),
    )

    ndjson = to_ndjson_lines([event])
    lines = ndjson.splitlines()
    assert len(lines) == 1
    assert '"event":"gateway.echo_failed"' in lines[0]
    assert '"error_code":"GATEWAY_TIMEOUT"' in lines[0]
    assert '"segment":"premium_users"' in lines[0]