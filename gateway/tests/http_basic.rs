use std::process::{Child, Command};
use std::{thread, time::Duration};

use reqwest::StatusCode;

fn start_gateway() -> Child {
    Command::new("cargo")
        .args(["run", "--bin", "gateway"])
        .spawn()
        .expect("failed to start gateway")
}

#[tokio::test]
#[ignore]
async fn health_endpoint_works() {
    let mut child = start_gateway();
    // give the server a moment to start
    thread::sleep(Duration::from_millis(800));

    let client = reqwest::Client::new();
    let res = client
        .get("http://127.0.0.1:8080/health")
        .send()
        .await
        .expect("request failed");

    assert_eq!(res.status(), StatusCode::OK);
    let body = res.text().await.expect("body read failed");
    assert_eq!(body, "ok");

    let _ = child.kill();
}