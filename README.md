# agentic-ml-workbench
Agentic control plane for real-time recommendation systems (Python orchestration + Rust gateway).

### Project layout

This repository uses a standard `src/` layout and separates library code from tests.  
The Python orchestrator lives in a dedicated package, and Rust provides the gateway service.

```text
agentic-ml-workbench/
  gateway/                   # Rust HTTP gateway (tools, safety, observability)
    src/
      main.rs                # Axum/Tokio HTTP server, /health, /echo, and tool stubs
      agent_log.rs           # Rust-side AgentLogEvent NDJSON schema
    tests/                   # Rust-side tests (unit + optional HTTP integration)
    Cargo.toml
    Cargo.lock

  py_orchestrator/           # Python orchestration layer (Task, state machine, clients)
    pyproject.toml
    uv.lock

    src/
      py_orchestrator/
        __init__.py
        core.py              # Simple examples used early in the book
        task.py              # Task schema (intent, inputs, constraints, done_definition, etc.)
        state.py             # TaskRun, TaskState, ErrorCode, trace entries
        orchestrator.py      # Minimal state-machine orchestrator
        gateway_client.py    # HTTP client for talking to the Rust gateway
        agent_log.py         # AgentLogEvent NDJSON schema for LLM-friendly observations
        export_trace.py      # Helpers to export TaskRun.trace metrics events to NDJSON
        tool_schemas/
          __init__.py
          metrics.py         # Typed request/response schemas for the metrics tool

    tests/
      test_core.py           # Basic unit tests for the early core examples
      test_task.py           # Tests for Task schema and example_debug_recs_task
      test_state.py          # (optional) Tests for TaskRun and state transitions (if added later)
      test_orchestrator.py   # Tests for the minimal orchestrator state transitions
      test_gateway_client.py # Tests for GatewayClient (unit + integration-style)
      test_agent_log.py      # Tests for AgentLogEvent and NDJSON helper
      test_export_trace.py   # Tests for metrics_log_event NDJSON export helpers
      tool_schemas/
        test_metrics.py      # Tests for the metrics tool schemas
```

The intent is:

- **Python (`py_orchestrator`)** is the orchestration and reasoning layer:  
  it defines Tasks, state machines, and how agents interact with the system.  
- **Rust (`gateway`)** is the control plane:  
  it exposes a small HTTP surface area, enforces constraints, and emits structured logs.

Code that is part of the public surface area lives under `src/py_orchestrator/`.  
Tests live under `py_orchestrator/tests/` and never leak into the package itself.

***

### How to run tests locally

Python and Rust each have their own test workflows.  
Python uses `uv` for environment and dependency management; Rust uses the standard Cargo tooling.

#### Python unit tests (orchestrator, Task, logging)

From the `py_orchestrator/` directory:

```bash
# Create / reuse a virtual environment managed by uv
uv venv

# Install the package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run all unit tests (excluding integration tests)
uv run pytest -m "not integration"
```

This will run the unit tests for:

- `Task` schema and example tasks  
- `TaskRun` and the minimal orchestrator state machine  
- the `GatewayClient` interface (without requiring a running gateway)  
- the `AgentLogEvent` NDJSON helper

#### Python integration tests (require a running gateway)

Integration tests are marked with `@pytest.mark.integration` and are **not** run in CI by default.  
They assume the Rust gateway is already running on `127.0.0.1:8080`.

In one terminal:

```bash
cd gateway
cargo run
```

In a second terminal:

```bash
cd py_orchestrator
uv venv
uv pip install -e ".[dev]"
uv run pytest -m integration
```

This will exercise the full Python → HTTP → Rust path via `GatewayClient.echo()`.

#### Rust tests

From the `gateway/` directory:

```bash
# Run Rust unit tests
cargo test
```

The HTTP integration test in `gateway/tests/http_basic.rs` is currently marked as `#[ignore]`  
so that the default CI pipeline stays fast and deterministic.  
It can be executed manually with:

```bash
cargo test --test http_basic -- --include-ignored
```

after ensuring no other process is bound to `127.0.0.1:8080`.

***

### CI expectations

GitHub Actions runs the following on every push and pull request to `main`:

- Python: `uv venv` → `uv pip install -e ".[dev]"` → `uv run pytest -m "not integration"`  
- Rust: `cargo test --verbose`

Integration tests are intentionally excluded from the default pipeline so that:

- the core orchestrator and gateway contracts stay stable and fast to validate, and  
- port binding and process-lifecycle issues do not interfere with CI.

This mirrors how the project is used in the book:  
unit tests serve as the “safety net” for the core abstractions,  
while integration tests are used during deeper, end-to-end exercises.


### Metrics trace export to NDJSON

During planning, the orchestrator calls the Rust metrics gateway and records structured observations inside `TaskRun.trace`.  
For each observed metrics drop, a serialized `AgentLogEvent` is stored under the `metrics_log_event` key on a trace entry.

The helper `export_metrics_log_events_to_ndjson` in `py_orchestrator.export_trace` turns these trace entries into a newline-delimited JSON (`.ndjson`) file that can be consumed by LLMs or offline analysis tools.

```python
from pathlib import Path

from py_orchestrator.gateway_client import GatewayClient
from py_orchestrator.orchestrator import orchestrate_once
from py_orchestrator.task import example_debug_recs_task
from py_orchestrator.export_trace import export_metrics_log_events_to_ndjson

gateway = GatewayClient()

# Run the orchestrator a few times and collect TaskRun objects.
runs = []
for i in range(3):
    task = example_debug_recs_task()
    task.id = f"debug-recs-{i}"
    run = orchestrate_once(task, gateway=gateway)
    runs.append(run)

# Export all metrics_log_event entries across these runs to an NDJSON file.
output_path = Path("metrics_observations.ndjson")
export_metrics_log_events_to_ndjson(runs, output_path)
print(f"Wrote {output_path}")
```

Each line of `metrics_observations.ndjson` is a single JSON object representing one `AgentLogEvent`.  
This matches the typical newline-delimited JSON (NDJSON) format, where each line is an independent JSON document separated by newlines, which makes it convenient for log processing pipelines and LLM training/evaluation datasets.

> In other words: the orchestrator writes structured metrics observations into the trace, and `export_metrics_log_events_to_ndjson` turns those observations into an NDJSON “case file” that can be fed directly into downstream tools or models.