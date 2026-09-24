"""Tests for health and readiness endpoints."""


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-prompt-firewall"
    assert "version" in data


def test_health_components(client):
    response = client.get("/api/health/components")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "database" in data["components"]
    assert "rule_engine" in data["components"]
    assert "ml_classifier" in data["components"]
