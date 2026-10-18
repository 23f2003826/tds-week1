import hashlib
import secrets
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from q14.mcp_server import router, solve_challenge_hash, REGISTERED_EMAIL

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def run_grader_simulation():
    print("=== STARTING MCP GRADER SIMULATION ===")
    
    # 1. Step 1: initialize
    print("\n[Step 1] Sending initialize request...")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "exam-grader",
                "version": "1.0.0"
            }
        }
    }
    resp = client.post("/mcp", json=init_payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "capabilities" in data["result"]
    assert "tools" in data["result"]["capabilities"]
    print("  -> Initialize handshake SUCCESSFUL:", data["result"])

    # 2. Step 2: notifications/initialized
    print("\n[Step 2] Sending notifications/initialized...")
    notify_payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    resp = client.post("/mcp", json=notify_payload)
    assert resp.status_code in (200, 204), f"Expected 200/204, got {resp.status_code}"
    print("  -> notifications/initialized SUCCESSFUL")

    # 3. Step 3: tools/list
    print("\n[Step 3] Calling tools/list...")
    list_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = client.post("/mcp", json=list_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 2
    tools = data["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "solve_challenge" in tool_names, f"solve_challenge not in {tool_names}"
    assert len(tools) == 1, f"Expected exactly 1 tool, got {len(tools)}"
    solve_tool = tools[0]
    # Check inputSchema has no required properties
    assert solve_tool.get("inputSchema", {}).get("required", []) == [], "inputSchema must have no required properties"
    print("  -> tools/list SUCCESSFUL. Found tool:", solve_tool)

    # 4. Step 4: Call solve_challenge 5 times with fresh random challenges
    print("\n[Step 4] Calling solve_challenge 5 times with fresh 32-char hex challenges...")
    for i in range(1, 6):
        fresh_challenge = secrets.token_hex(16) # 32 hex chars
        expected_hash = hashlib.sha256(f"{fresh_challenge}:{REGISTERED_EMAIL}".encode()).hexdigest()[:16]

        call_payload = {
            "jsonrpc": "2.0",
            "id": 10 + i,
            "method": "tools/call",
            "params": {
                "name": "solve_challenge",
                "arguments": {}
            }
        }
        headers = {
            "X-Exam-Challenge": fresh_challenge,
            "X-Exam-Timestamp": "1792340000000",
            "X-Exam-Signature": "fake-sig-for-testing"
        }

        resp = client.post("/mcp", json=call_payload, headers=headers)
        assert resp.status_code == 200, f"Call {i} failed with status {resp.status_code}"
        res_data = resp.json()
        assert res_data["id"] == 10 + i
        content = res_data["result"]["content"]
        assert len(content) == 1, f"Expected single content block, got {len(content)}"
        assert content[0]["type"] == "text"
        actual_text = content[0]["text"]

        assert actual_text == expected_hash, f"Call {i} hash mismatch: {actual_text} vs {expected_hash}"
        print(f"  -> Call {i}/5 PASS: challenge={fresh_challenge} -> response={actual_text} (expected={expected_hash})")

    # 5. Step 5: Test trailing slash /mcp/
    print("\n[Step 5] Testing trailing slash /mcp/ endpoint...")
    resp_slash = client.post("/mcp/", json=list_payload)
    assert resp_slash.status_code == 200
    print("  -> Trailing slash /mcp/ PASS")

    print("\n🎉 ALL MCP GRADER SIMULATION TESTS PASSED SUCCESSFULLY! 🎉\n")

if __name__ == "__main__":
    run_grader_simulation()
