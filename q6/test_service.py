from fastapi.testclient import TestClient
from main import app, DEFAULTS

# Create a test client simulating requests against the FastAPI app
client = TestClient(app)

def test_default_merge_no_params():
    """Verify that all 4 layers merge correctly without query params:
    1. defaults: port 8000, workers 1, debug false, log_level info, api_key default-secret-000
    2. config.development.yaml: port 8489, workers 12, debug true
    3. .env: debug true, api_key key-a0wigr7om6
    4. OS env: port 8144, workers 11

    Expected baseline output:
    - port: 8144 (int, from OS env)
    - workers: 11 (int, from OS env)
    - debug: true (bool, from .env / yaml)
    - log_level: "info" (str, from defaults)
    - api_key: "****" (masked)
    """
    response = client.get("/effective-config")
    assert response.status_code == 200
    data = response.json()
    print("Baseline response:", data)
    assert data["port"] == 8144
    assert isinstance(data["port"], int)
    assert data["workers"] == 11
    assert isinstance(data["workers"], int)
    assert data["debug"] is True
    assert isinstance(data["debug"], bool)
    assert data["log_level"] == "info"
    assert isinstance(data["log_level"], str)
    assert data["api_key"] == "****"

def test_cli_overrides():
    """Verify that query parameter ?set=key=value overrides previous layers with highest precedence."""
    response = client.get("/effective-config?set=port=9000&set=debug=false")
    assert response.status_code == 200
    data = response.json()
    print("Overrides response:", data)
    assert data["port"] == 9000
    assert isinstance(data["port"], int)
    assert data["debug"] is False
    assert isinstance(data["debug"], bool)
    assert data["workers"] == 11
    assert data["api_key"] == "****"

def test_cli_overrides_workers_and_alias():
    """Verify NUM_WORKERS alias resolution to workers."""
    response = client.get("/effective-config?set=workers=5")
    assert response.status_code == 200
    assert response.json()["workers"] == 5

    response_alias = client.get("/effective-config?set=NUM_WORKERS=99")
    assert response_alias.status_code == 200
    assert response_alias.json()["workers"] == 99

def test_api_key_always_masked():
    """Verify secret masking rule: api_key must always appear as '****', even if overridden."""
    response = client.get("/effective-config?set=api_key=super-secret-12345")
    assert response.status_code == 200
    assert response.json()["api_key"] == "****"

def test_boolean_type_coercion():
    """Verify case-insensitive boolean coercion for true/1/yes/on."""
    for val in ["true", "1", "yes", "on", "True", "YES", "ON"]:
        res = client.get(f"/effective-config?set=debug={val}").json()
        assert res["debug"] is True, f"Failed for {val}"

    for val in ["false", "0", "no", "off", "False", "NO", "OFF"]:
        res = client.get(f"/effective-config?set=debug={val}").json()
        assert res["debug"] is False, f"Failed for {val}"

def test_cors_headers():
    """Verify that OPTIONS preflight request responds with proper CORS headers."""
    response = client.options(
        "/effective-config",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") in ["*", "https://example.com"]

if __name__ == "__main__":
    test_default_merge_no_params()
    test_cli_overrides()
    test_cli_overrides_workers_and_alias()
    test_api_key_always_masked()
    test_boolean_type_coercion()
    test_cors_headers()
    print("ALL TESTS PASSED SUCCESSFULLY!")
