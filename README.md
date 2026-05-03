# agentic-ml-workbench
Agentic control plane for real-time recommendation systems (Python orchestration + Rust gateway).


### Project layout

This repository uses a standard `src/` layout and separates library code from tests.  
The Python orchestrator lives in a dedicated package, and Rust provides the gateway service.

```text
agentic-ml-workbench/
  gateway/                   # Rust HTTP gateway (tools, safety, observability)
    src/
      main.rs                # Axum/Tokio HTTP server, /health and /echo
      agent_log.rs           # Rust-side AgentLogEvent NDJSON schema
    tests/
      http_basic.rs          # (ignored in CI) example HTTP integration test
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

    tests/
      test_core.py           # Basic unit tests for core examples
      test_task.py           # Tests for Task schema and example_debug_recs_task
      test_orchestrator.py   # Tests for the minimal orchestrator state transitions
      test_gateway_client.py # Integration-style test for GatewayClient (marked as integration)
      test_agent_log.py      # Tests for AgentLogEvent and NDJSON helper
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