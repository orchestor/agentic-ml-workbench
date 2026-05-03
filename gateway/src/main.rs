mod agent_log;

use axum::{
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tracing::{info, Level};
use tracing_subscriber::{fmt::format::FmtSpan, EnvFilter};

use crate::agent_log::{
    AgentAction, AgentClassification, AgentContext, AgentIds, AgentLogEvent, AgentObservation,
    AgentSource, ObservationEvidence,
};

#[derive(Debug, Serialize, Deserialize)]
struct EchoRequest {
    message: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct MetricsRequest {
    metric_name: String,
    segment: String,
    baseline_window_minutes: i32,
    current_window_minutes: i32,
}

#[derive(Debug, Serialize, Deserialize)]
struct MetricsPoint {
    timestamp: String,
    value: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct MetricsSeriesResponse {
    metric_name: String,
    segment: String,
    baseline_window_minutes: i32,
    current_window_minutes: i32,
    baseline_value: f64,
    current_value: f64,
    absolute_drop: f64,
    relative_drop_percent: f64,
    time_series: Vec<MetricsPoint>,
}

#[tokio::main]
async fn main() {
    init_tracing();

    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/echo", post(echo_handler))
        .route("/tools/metrics/debug_recs", post(metrics_debug_recs_handler));

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    info!("gateway listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("failed to bind");

    axum::serve(listener, app)
        .await
        .expect("server error");
}



fn init_tracing() {
    let filter =
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));

    tracing_subscriber::fmt()
        .json()
        .with_env_filter(filter)
        .with_max_level(Level::INFO)
        .with_target(true)
        .with_current_span(true)
        .with_span_events(FmtSpan::CLOSE)
        .init();
}


async fn health_handler() -> &'static str {
    // Emit a simple AgentLogEvent for the health check
    let event = AgentLogEvent {
        level: "INFO".to_string(),
        event: "gateway.health_check".to_string(),
        source: AgentSource {
            service: "gateway".to_string(),
            component: "http_server".to_string(),
            function: Some("health_handler".to_string()),
            env: "dev".to_string(),
        },
        context: AgentContext {
            layer: Some("gateway".to_string()),
            step: Some("health".to_string()),
            ..AgentContext::default()
        },
        observation: AgentObservation {
            summary: "Health check endpoint called.".to_string(),
            raw_message: None,
            evidence: ObservationEvidence::default(),
        },
        classification: AgentClassification::default(),
        action: AgentAction {
            taken: Some("return_ok".to_string()),
            next_suggested: None,
        },
        ids: AgentIds::default(),
        ..AgentLogEvent::default()
    };

    // Structured log as JSON line
    info!(agent_log = serde_json::to_string(&event).unwrap(), "agent_event");

    "ok"
}

async fn echo_handler(Json(payload): Json<EchoRequest>) -> Json<EchoRequest> {
    Json(payload)
}

async fn metrics_debug_recs_handler(
    Json(req): Json<MetricsRequest>,
) -> Json<MetricsSeriesResponse> {
    // This is a stub. In a real system, the gateway would query metrics storage.
    // For now we just construct a deterministic, fake response.

    let baseline_value = 0.12;
    let current_value = 0.09;
    let absolute_drop = current_value - baseline_value;
    let relative_drop_percent = (absolute_drop / baseline_value) * 100.0;

    let response = MetricsSeriesResponse {
        metric_name: req.metric_name,
        segment: req.segment,
        baseline_window_minutes: req.baseline_window_minutes,
        current_window_minutes: req.current_window_minutes,
        baseline_value,
        current_value,
        absolute_drop,
        relative_drop_percent,
        time_series: vec![
            MetricsPoint {
                timestamp: "2026-05-02T11:00:00Z".to_string(),
                value: baseline_value,
            },
            MetricsPoint {
                timestamp: "2026-05-02T11:15:00Z".to_string(),
                value: 0.10,
            },
            MetricsPoint {
                timestamp: "2026-05-02T11:30:00Z".to_string(),
                value: current_value,
            },
        ],
    };

    Json(response)
}