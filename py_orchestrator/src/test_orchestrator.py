from .orchestrator import orchestrate_once
from .state import TaskState, ErrorCode
from .task import example_debug_recs_task


def test_orchestrate_once_completes_planning() -> None:
    task = example_debug_recs_task()
    run = orchestrate_once(task)

    assert run.state == TaskState.DONE
    assert run.error_code == ErrorCode.NONE
    assert any(
        entry.state == TaskState.PLANNING for entry in run.trace
    )