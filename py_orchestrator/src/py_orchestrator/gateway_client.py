import json
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class GatewayConfig:
    base_url: str = "http://127.0.0.1:8080"


class GatewayClient:
    """
    Minimal HTTP client for talking to the Rust gateway.

    For now we only use /echo as a smoke test.
    Later this will be extended to a generic tool execution endpoint.
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