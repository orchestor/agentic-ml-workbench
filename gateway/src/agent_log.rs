use serde::Serialize;
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Debug, Serialize)]
pub struct AgentIds {
    pub run_id: Option<String>,
    pub task_id: Option<String>,
    pub trace_id: Option<String>,
    pub span_id: Option<String>,
    pub parent_span_id: Option<String>,
}

impl Default for AgentIds {
    fn default() -> Self {
        Self {
            run_id: None,
            task_id: None,
            trace_id: None,
            span_id: None,
            parent_span_id: None,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentSource {
    pub service: String,
    pub component: String,
    pub function: Option<String>,
    pub env: String,
}

impl Default for AgentSource {
    fn default() -> Self {
        Self {
            service: "gateway".to_string(),
            component: "unknown".to_string(),
            function: None,
            env: "dev".to_string(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentContext {
    pub intent: Option<String>,
    pub segment: Option<String>,
    pub layer: Option<String>,
    pub step: Option<String>,
}

impl Default for AgentContext {
    fn default() -> Self {
        Self {
            intent: None,
            segment: None,
            layer: None,
            step: None,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct ObservationEvidence {
    pub latency_ms: Option<f64>,
    pub timeout_ms: Option<f64>,
    pub http_status: Option<i32>,
    #[serde(default)]
    pub extra: BTreeMap<String, Value>,
}

impl Default for ObservationEvidence {
    fn default() -> Self {
        Self {
            latency_ms: None,
            timeout_ms: None,
            http_status: None,
            extra: BTreeMap::new(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentObservation {
    pub summary: String,
    pub raw_message: Option<String>,
    pub evidence: ObservationEvidence,
}

impl Default for AgentObservation {
    fn default() -> Self {
        Self {
            summary: "no-summary".to_string(),
            raw_message: None,
            evidence: ObservationEvidence::default(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentClassification {
    pub error_code: Option<String>,
    pub severity: Option<String>,
    pub retryable: Option<bool>,
    pub confidence: Option<f64>,
}

impl Default for AgentClassification {
    fn default() -> Self {
        Self {
            error_code: None,
            severity: None,
            retryable: None,
            confidence: None,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentAction {
    pub taken: Option<String>,
    pub next_suggested: Option<String>,
}

impl Default for AgentAction {
    fn default() -> Self {
        Self {
            taken: None,
            next_suggested: None,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AgentLogEvent {
    pub schema_version: String,
    pub ts: String,
    pub level: String,
    pub event: String,
    pub ids: AgentIds,
    pub source: AgentSource,
    pub context: AgentContext,
    pub observation: AgentObservation,
    pub classification: AgentClassification,
    pub action: AgentAction,
}

impl Default for AgentLogEvent {
    fn default() -> Self {
        Self {
            schema_version: "agentic-ml-log.v1".to_string(),
            ts: chrono::Utc::now().to_rfc3339(),
            level: "INFO".to_string(),
            event: "generic.event".to_string(),
            ids: AgentIds::default(),
            source: AgentSource::default(),
            context: AgentContext::default(),
            observation: AgentObservation::default(),
            classification: AgentClassification::default(),
            action: AgentAction::default(),
        }
    }
}