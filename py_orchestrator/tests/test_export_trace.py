from pathlib import Path
from tempfile import TemporaryDirectory

from py_orchestrator.agent_log import AgentLogEvent
from py_orchestrator.export_trace import (
    export_metrics_log_events_to_ndjson,
)
from py_orchestrator.state import TaskRun, TaskState, TraceEntry
from py_orchestrator.task import Task


def make_fake_run_with_metrics_event() -> TaskRun:
    task = Task(id="t1", intent="debug recs")
    run = TaskRun(run_id="run1", task=task, state=TaskState.PENDING)

    fake_event = AgentLogEvent(
        level="INFO",
        event="metrics.observed_drop",
    ).to_dict()

    run.trace.append(
        TraceEntry(
            state=TaskState.PLANNING,
            info={
                "metrics_log_event": fake_event,
            },
        )
    )
    return run


def test_export_metrics_log_events_to_ndjson() -> None:
    run = make_fake_run_with_metrics_event()

    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "metrics.ndjson"
        export_metrics_log_events_to_ndjson([run], path)

        content = path.read_text(encoding="utf-8").strip()
        lines = content.splitlines()
        assert len(lines) == 1
        assert '"event":"metrics.observed_drop"' in lines[0]