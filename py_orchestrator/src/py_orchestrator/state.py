from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .task import Task


class TaskState(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    DONE = "DONE"
    FAILED = "FAILED"


class ErrorCode(str, Enum):
    NONE = "NONE"
    PLAN_ERROR = "PLAN_ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class TraceEntry:
    state: TaskState
    info: Dict[str, Any]


@dataclass
class TaskRun:
    """
    One execution attempt of a Task.

    This is the core execution record we will persist and replay.
    """
    run_id: str
    task: Task
    state: TaskState = TaskState.PENDING
    error_code: ErrorCode = ErrorCode.NONE
    error_message: Optional[str] = None
    trace: List[TraceEntry] = field(default_factory=list)

    def record(self, state: TaskState, info: Dict[str, Any]) -> None:
        self.state = state
        self.trace.append(TraceEntry(state=state, info=info))