from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class DoneDefinition:
    """
    Describes what it means for a task to be 'done'.

    This is intentionally generic so it can be used for:
    - debugging a recommendation incident
    - running an evaluation
    - generating documentation
    """
    must_return_fields: List[str] = field(default_factory=list)
    acceptable_error_range: float = 0.0  # for numeric metrics, if needed


@dataclass
class Constraints:
    """
    Hard limits for executing a task.
    These are enforced by the control plane, not by the model.
    """
    max_runtime_seconds: int = 60
    max_tool_calls: int = 32
    max_cost_usd: Optional[float] = None


@dataclass
class BudgetHint:
    """
    Soft hints to the model/orchestrator about how much to spend.
    These are advisory, not hard limits.
    """
    target_model_calls: int = 4
    prefer_small_models: bool = True


@dataclass
class Task:
    """
    Minimal, typed description of a unit of work.

    All higher-level workflows in this project should be expressed
    in terms of this Task schema (or a small extension of it).
    """
    id: str
    intent: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    constraints: Constraints = field(default_factory=Constraints)
    done_definition: DoneDefinition = field(default_factory=DoneDefinition)
    priority: TaskPriority = TaskPriority.NORMAL
    budget_hint: BudgetHint = field(default_factory=BudgetHint)


def example_debug_recs_task() -> Task:
    """
    Construct a sample task for debugging a recommendation incident.

    We will reuse this in tests and examples throughout the book.
    """
    return Task(
        id="debug-recs-ctr-drop-001",
        intent="Investigate CTR drop for new users in region US over the last 30 minutes.",
        inputs={
            "segment": "new_users_us",
            "metric": "ctr",
            "time_window_minutes": 30,
            "baseline_ctr": 0.12,
            "current_ctr": 0.09,
        },
        constraints=Constraints(
            max_runtime_seconds=120,
            max_tool_calls=16,
            max_cost_usd=1.0,
        ),
        done_definition=DoneDefinition(
            must_return_fields=["root_cause_candidates", "suggested_experiments"],
            acceptable_error_range=0.0,
        ),
        priority=TaskPriority.HIGH,
        budget_hint=BudgetHint(
            target_model_calls=6,
            prefer_small_models=False,
        ),
    )