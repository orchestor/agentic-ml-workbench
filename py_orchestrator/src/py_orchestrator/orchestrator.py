import uuid
from typing import Dict, Any

from .state import TaskRun, TaskState, ErrorCode
from .task import Task

from .gateway_client import GatewayClient
from .tool_schemas.metrics import FetchRecentMetricsRequest, MetricsSeries
from .agent_log import (
    AgentAction,
    AgentClassification,
    AgentContext,
    AgentIds,
    AgentLogEvent,
    AgentObservation,
    AgentSource,
    ObservationEvidence,
)

def build_metrics_log_event(
    run: TaskRun,
    metrics: MetricsSeries,
) -> AgentLogEvent:
    """
    Build an AgentLogEvent that describes the metrics observation
    for this run.

    This is what we want to feed into LLMs and downstream evaluators.
    """
    evidence = ObservationEvidence(
        latency_ms=None,
        timeout_ms=None,
        http_status=None,
        extra={
            "baseline_value": metrics.baseline_value,
            "current_value": metrics.current_value,
            "absolute_drop": metrics.absolute_drop,
            "relative_drop_percent": metrics.relative_drop_percent,
        },
    )

    observation = AgentObservation(
        summary=(
            f"Observed {metrics.metric_name} drop for segment "
            f"{metrics.segment}: baseline={metrics.baseline_value:.4f}, "
            f"current={metrics.current_value:.4f}, "
            f"relative_drop_percent={metrics.relative_drop_percent:.2f}."
        ),
        raw_message=None,
        evidence=evidence,
    )

    return AgentLogEvent(
        level="INFO",
        event="metrics.observed_drop",
        ids=AgentIds(
            run_id=run.run_id,
            task_id=run.task.id,
            trace_id=None,
            span_id=None,
            parent_span_id=None,
        ),
        source=AgentSource(
            service="py_orchestrator",
            component="orchestrator",
            function="orchestrate_once",
            env="dev",
        ),
        context=AgentContext(
            intent=run.task.intent,
            segment=metrics.segment,
            layer="planning",
            step="fetch_recent_metrics",
        ),
        observation=observation,
        classification=AgentClassification(
            error_code=None,
            severity="info",
            retryable=None,
            confidence=None,
        ),
        action=AgentAction(
            taken="record_metrics_summary",
            next_suggested="use_series_for_root_cause_analysis",
        ),
    )

def new_run(task: Task) -> TaskRun:
    return TaskRun(run_id=str(uuid.uuid4()), task=task)


def simple_planning(task: Task) -> Dict[str, Any]:
    """
    A placeholder planning step.

    For now, it just echoes the task intent and marks a single 'step'.
    Later we will replace this with a real LLM-based planner.
    """
    return {
        "plan_summary": f"Investigate: {task.intent}",
        "steps": [
            "inspect_recent_metrics",
            "inspect_logs",
            "generate_hypotheses",
        ],
    }


def orchestrate_once(task: Task, gateway: GatewayClient | None = None) -> TaskRun:
    """
    Minimal orchestrator: PENDING -> PLANNING -> DONE or FAILED.

    Optionally talks to the gateway for:
    - a simple echo (connectivity smoke test)
    - a stubbed metrics fetch for recommendation incidents
    and records an AgentLogEvent-style metrics observation.
    """
    run = new_run(task)
    gw = gateway or GatewayClient()

    try:
        run.record(TaskState.PLANNING, {"message": "Planning started"})
        plan = simple_planning(task)

        # Connectivity smoke test via /echo
        echo_message = f"planning-run-{run.run_id}"
        try:
            echoed = gw.echo(echo_message)
        except Exception as echo_exc:  # noqa: BLE001
            echoed = f"gateway-error: {echo_exc}"

        # Optional: fetch recent metrics if the task provides enough context
        metrics_summary: Dict[str, Any] | None = None
        metrics_log_event_dict: Dict[str, Any] | None = None

        if "metric" in task.inputs and "segment" in task.inputs:
            try:
                metrics_req = FetchRecentMetricsRequest(
                    metric_name=str(task.inputs["metric"]),
                    segment=str(task.inputs["segment"]),
                    baseline_window_minutes=int(
                        task.inputs.get("baseline_window_minutes", 60)
                    ),
                    current_window_minutes=int(
                        task.inputs.get("time_window_minutes", 30)
                    ),
                )
                metrics_series: MetricsSeries = gw.fetch_recent_metrics(metrics_req)
                metrics_summary = {
                    "metric_name": metrics_series.metric_name,
                    "segment": metrics_series.segment,
                    "baseline_value": metrics_series.baseline_value,
                    "current_value": metrics_series.current_value,
                    "absolute_drop": metrics_series.absolute_drop,
                    "relative_drop_percent": metrics_series.relative_drop_percent,
                }

                # Build an AgentLogEvent-style observation for this metrics series
                metrics_log_event = build_metrics_log_event(run, metrics_series)
                metrics_log_event_dict = metrics_log_event.to_dict()
            except Exception as metrics_exc:  # noqa: BLE001
                metrics_summary = {
                    "error": f"metrics-fetch-error: {metrics_exc}",
                }
                metrics_log_event_dict = None

        run.record(
            TaskState.PLANNING,
            {
                "plan": plan,
                "gateway_echo": echoed,
                "metrics_summary": metrics_summary,
                "metrics_log_event": metrics_log_event_dict,
            },
        )

        run.record(TaskState.DONE, {"message": "Planning completed"})
        return run
    except Exception as exc:  # noqa: BLE001
        run.error_code = ErrorCode.UNKNOWN
        run.error_message = str(exc)
        run.record(TaskState.FAILED, {"message": "Unexpected error"})
        return run