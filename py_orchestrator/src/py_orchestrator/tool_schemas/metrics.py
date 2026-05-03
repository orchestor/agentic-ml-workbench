from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class FetchRecentMetricsRequest:
    metric_name: str
    segment: str
    baseline_window_minutes: int
    current_window_minutes: int


@dataclass
class MetricsPoint:
    timestamp: str  # ISO 8601
    value: float


@dataclass
class MetricsSeries:
    metric_name: str
    segment: str
    baseline_window_minutes: int
    current_window_minutes: int
    baseline_value: float
    current_value: float
    absolute_drop: float
    relative_drop_percent: float
    time_series: List[MetricsPoint] = field(default_factory=list)