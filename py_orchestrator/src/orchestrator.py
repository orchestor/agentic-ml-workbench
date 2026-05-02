import uuid
from typing import Dict, Any

from .state import TaskRun, TaskState, ErrorCode
from .task import Task


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


def orchestrate_once(task: Task) -> TaskRun:
    """
    Minimal orchestrator: PENDING -> PLANNING -> DONE or FAILED.

    This is intentionally simple:
    - it constructs a TaskRun
    - records a planning step
    - marks the run as DONE if planning succeeds
    """
    run = new_run(task)

    try:
        run.record(TaskState.PLANNING, {"message": "Planning started"})
        plan = simple_planning(task)
        run.record(TaskState.PLANNING, {"plan": plan})

        run.record(TaskState.DONE, {"message": "Planning completed"})
        return run
    except Exception as exc:
        run.error_code = ErrorCode.UNKNOWN
        run.error_message = str(exc)
        run.record(TaskState.FAILED, {"message": "Unexpected error"})
        return run