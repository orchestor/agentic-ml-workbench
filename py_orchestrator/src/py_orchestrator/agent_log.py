from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "agentic-ml-log.v1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentIds:
    run_id: Optional[str] = None
    task_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None


@dataclass
class AgentSource:
    service: str = "py_orchestrator"
    component: str = "unknown"
    function: Optional[str] = None
    env: str = "dev"


@dataclass
class AgentContext:
    intent: Optional[str] = None
    segment: Optional[str] = None
    layer: Optional[str] = None
    step: Optional[str] = None


@dataclass
class ObservationEvidence:
    latency_ms: Optional[float] = None
    timeout_ms: Optional[float] = None
    http_status: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentObservation:
    summary: str
    raw_message: Optional[str] = None
    evidence: ObservationEvidence = field(default_factory=ObservationEvidence)


@dataclass
class AgentClassification:
    error_code: Optional[str] = None
    severity: Optional[str] = None  # e.g. "recoverable" / "fatal" / "info"
    retryable: Optional[bool] = None
    confidence: Optional[float] = None  # for LLM-assigned classifications


@dataclass
class AgentAction:
    taken: Optional[str] = None
    next_suggested: Optional[str] = None


@dataclass
class AgentLogEvent:
    """
    LLM-friendly observation event, designed to be emitted as NDJSON.

    This structure mirrors how we want agents to see logs and metrics:
    each line answers:
    - when did it happen?
    - for which run/task?
    - from which service/component?
    - at which step?
    - what happened?
    - what evidence do we have?
    - what action was taken or suggested?
    """

    schema_version: str = SCHEMA_VERSION
    ts: str = field(default_factory=utc_now_iso)
    level: str = "INFO"
    event: str = "generic.event"

    ids: AgentIds = field(default_factory=AgentIds)
    source: AgentSource = field(default_factory=AgentSource)
    context: AgentContext = field(default_factory=AgentContext)
    observation: AgentObservation = field(
        default_factory=lambda: AgentObservation(summary="no-summary")
    )
    classification: AgentClassification = field(
        default_factory=AgentClassification
    )
    action: AgentAction = field(default_factory=AgentAction)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def to_ndjson_lines(events: List[AgentLogEvent]) -> str:
    """
    Convert a list of AgentLogEvent objects into an NDJSON string.

    Each line is a JSON object.
    """
    import json

    lines: List[str] = []
    for event in events:
        lines.append(json.dumps(event.to_dict(), separators=(",", ":")))
    return "\n".join(lines)