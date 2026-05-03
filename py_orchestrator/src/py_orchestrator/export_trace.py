from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from .agent_log import AgentLogEvent, to_ndjson_lines
from .state import TaskRun


def extract_metrics_log_events_from_run(run: TaskRun) -> List[AgentLogEvent]:
    """
    Extract all metrics_log_event dicts from a TaskRun.trace and convert
    them back into AgentLogEvent objects.

    This assumes orchestrator stored metrics_log_event as a dict produced
    by AgentLogEvent.to_dict().
    """
    events: List[AgentLogEvent] = []

    for entry in run.trace:
        info = entry.info
        raw = info.get("metrics_log_event")
        if not raw:
            continue

        # raw is a dict produced by AgentLogEvent.to_dict()
        event = AgentLogEvent(
            schema_version=raw.get("schema_version", "agentic-ml-log.v1"),
            ts=raw.get("ts", ""),
            level=raw.get("level", "INFO"),
            event=raw.get("event", "metrics.observed_drop"),
            ids=raw.get("ids", {}),  # will be normalized below
            source=raw.get("source", {}),
            context=raw.get("context", {}),
            observation=raw.get("observation", {}),
            classification=raw.get("classification", {}),
            action=raw.get("action", {}),
        )

        # A bit of normalization: if nested parts are plain dicts, wrap them via asdict()
        # or leave them as-is; for now we keep it simple and rely on to_dict() later.
        events.append(event)

    return events


def export_metrics_log_events_to_ndjson(
    runs: Iterable[TaskRun],
    output_path: Path,
) -> None:
    """
    Collect all metrics_log_event entries from the given TaskRuns and write
    them to an NDJSON file.

    Each line in the file is a JSON object representing one AgentLogEvent.
    """
    all_events: List[AgentLogEvent] = []
    for run in runs:
        all_events.extend(extract_metrics_log_events_from_run(run))

    if not all_events:
        # Nothing to write; create an empty file to be explicit.
        output_path.write_text("", encoding="utf-8")
        return

    ndjson = to_ndjson_lines(all_events)
    output_path.write_text(ndjson + "\n", encoding="utf-8")