import pytest

from py_orchestrator.gateway_client import GatewayClient
from py_orchestrator.orchestrator import orchestrate_once
from py_orchestrator.state import TaskState, ErrorCode
from py_orchestrator.task import example_debug_recs_task


@pytest.mark.integration
def test_orchestrator_fetches_metrics_and_records_summary() -> None:
    """
    This test assumes the Rust gateway is running on 127.0.0.1:8080.
    It checks that orchestrate_once() records a metrics_summary when
    the task inputs contain metric and segment information.
    """
    task = example_debug_recs_task()
    gateway = GatewayClient()

    run = orchestrate_once(task, gateway=gateway)

    assert run.state == TaskState.DONE
    assert run.error_code == ErrorCode.NONE

    # There should be at least one PLANNING trace entry that contains metrics_summary
    planning_entries = [
        entry for entry in run.trace if entry.state == TaskState.PLANNING
    ]
    assert planning_entries, "no PLANNING entries found in trace"

    metrics_summaries = [
        entry.info.get("metrics_summary")
        for entry in planning_entries
        if "metrics_summary" in entry.info
    ]

    assert metrics_summaries, "no metrics_summary recorded in PLANNING trace entries"

    summary = metrics_summaries[-1]
    assert summary is not None
    assert summary.get("metric_name") == "ctr"
    assert summary.get("segment") == "new_users_us"
    assert summary.get("baseline_value") is not None
    assert summary.get("current_value") is not None


@pytest.mark.integration
def test_orchestrator_records_metrics_log_event() -> None:
    task = example_debug_recs_task()
    gateway = GatewayClient()

    run = orchestrate_once(task, gateway=gateway)
    # DEBUG: print the trace states and keys
    for entry in run.trace:
        print("TRACE_STATE:", entry.state, "INFO_KEYS:", list(entry.info.keys()))
        
    assert run.state == TaskState.DONE
    assert run.error_code == ErrorCode.NONE

    planning_entries = [
        entry for entry in run.trace if entry.state == TaskState.PLANNING
    ]
    assert planning_entries, "no PLANNING entries found in trace"

    log_events = [
        entry.info.get("metrics_log_event")
        for entry in planning_entries
        if "metrics_log_event" in entry.info
    ]

    assert log_events, "no metrics_log_event recorded in PLANNING trace entries"

    event = log_events[-1]
    assert event is not None
    assert event.get("event") == "metrics.observed_drop"
    assert event.get("context", {}).get("segment") == "new_users_us"
    assert event.get("observation", {}).get("summary", "").startswith(
        "Observed ctr drop"
    )