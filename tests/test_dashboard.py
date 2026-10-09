import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_dashboard_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert response.headers.get("location") == "/dashboard/"

def test_dashboard_index_html(client):
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "UNEX OS" in response.text
    assert "waveform-canvas" in response.text
    assert "neural-orb" in response.text

def test_dashboard_static_assets(client):
    css_res = client.get("/dashboard/css/dashboard.css")
    assert css_res.status_code == 200
    assert "var(--cyan-primary)" in css_res.text

    viz_res = client.get("/dashboard/js/visualizer.js")
    assert viz_res.status_code == 200
    assert "VoiceVisualizer" in viz_res.text

    telemetry_res = client.get("/dashboard/js/telemetry.js")
    assert telemetry_res.status_code == 200
    assert "TelemetryManager" in telemetry_res.text

    app_res = client.get("/dashboard/js/app.js")
    assert app_res.status_code == 200
    assert "loadScreenThumbnail" in app_res.text

def test_api_metrics_telemetry(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu" in data
    assert "memory" in data
    assert "gpu" in data
    assert "process" in data

def test_api_active_window(client):
    response = client.get("/api/desktop/active-window")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data

def test_api_security_pending(client):
    response = client.get("/api/security/pending")
    assert response.status_code == 200
    data = response.json()
    assert "pending" in data

def test_api_screen_thumbnail(client):
    response = client.get("/api/vision/screen-thumbnail")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
