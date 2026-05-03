import json
from dataclasses import dataclass
from typing import Optional

import requests

from .tool_schemas.metrics import (
    FetchRecentMetricsRequest,
    MetricsPoint,
    MetricsSeries,
)


@dataclass
class GatewayConfig:
    base_url: str = "http://127.0.0.1:8080"


class GatewayClient:
    """
    Minimal HTTP client for talking to the Rust gateway.

    For now we use:
    - /echo as a connectivity smoke test
    - /tools/metrics/debug_recs as a stubbed metrics tool
    """

    def __init__(self, config: Optional[GatewayConfig] = None) -> None:
        self.config = config or GatewayConfig()

    def echo(self, message: str) -> str:
        url = f"{self.config.base_url}/echo"
        payload = {"message": message}
        resp = requests.post(url, json=payload, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]

    def fetch_recent_metrics(
        self, req: FetchRecentMetricsRequest
    ) -> MetricsSeries:
        """
        Call the stubbed metrics tool on the gateway.

        This is a simple POST to /tools/metrics/debug_recs that returns
        a JSON payload matching MetricsSeries.
        """
        url = f"{self.config.base_url}/tools/metrics/debug_recs"
        payload = {
            "metric_name": req.metric_name,
            "segment": req.segment,
            "baseline_window_minutes": req.baseline_window_minutes,
            "current_window_minutes": req.current_window_minutes,
        }
        resp = requests.post(url, json=payload, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()

        points = [
            MetricsPoint(timestamp=p["timestamp"], value=p["value"])
            for p in data.get("time_series", [])
        ]

        return MetricsSeries(
            metric_name=data["metric_name"],
            segment=data["segment"],
            baseline_window_minutes=data["baseline_window_minutes"],
            current_window_minutes=data["current_window_minutes"],
            baseline_value=data["baseline_value"],
            current_value=data["current_value"],
            absolute_drop=data["absolute_drop"],
            relative_drop_percent=data["relative_drop_percent"],
            time_series=points,
        )