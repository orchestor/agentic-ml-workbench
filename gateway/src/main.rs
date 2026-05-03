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

#[tokio::main]
async fn main() {
    init_tracing();

    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/echo", post(echo_handler));

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