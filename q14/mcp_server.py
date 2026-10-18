import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)

router = APIRouter()

REGISTERED_EMAIL = "23f2003826@ds.study.iitm.ac.in".strip().lower()

def solve_challenge_hash(challenge: str, email: str = REGISTERED_EMAIL) -> str:
    """Computes the first 16 lowercase hex characters of SHA-256(challenge:email)."""
    normalized_email = email.strip().lower()
    raw = f"{challenge.strip()}:{normalized_email}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].lower()

def handle_jsonrpc_request(req: Dict[str, Any], headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Handles an individual JSON-RPC 2.0 request or notification."""
    jsonrpc_ver = req.get("jsonrpc", "2.0")
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {}) or {}

    logger.info(f"Incoming MCP method: {method}, id: {req_id}")

    # 1. MCP Handshake: initialize
    if method == "initialize":
        client_proto = params.get("protocolVersion", "2024-11-05")
        return {
            "jsonrpc": jsonrpc_ver,
            "id": req_id,
            "result": {
                "protocolVersion": client_proto,
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "solve-challenge-server",
                    "version": "1.0.0"
                }
            }
        }

    # 2. MCP Notification: notifications/initialized
    elif method == "notifications/initialized":
        logger.info("Received notifications/initialized handshake completion")
        if req_id is not None:
            return {
                "jsonrpc": jsonrpc_ver,
                "id": req_id,
                "result": {}
            }
        return None

    # 3. Tool Discovery: tools/list
    elif method == "tools/list":
        return {
            "jsonrpc": jsonrpc_ver,
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "solve_challenge",
                        "description": "Solves the exam challenge using X-Exam-Challenge header",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }

    # 4. Tool Execution: tools/call
    elif method == "tools/call":
        tool_name = params.get("name")
        if tool_name != "solve_challenge":
            return {
                "jsonrpc": jsonrpc_ver,
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found. Expected 'solve_challenge'"
                }
            }

        # Header extraction: X-Exam-Challenge
        # HTTP headers are case-insensitive
        challenge = (
            headers.get("x-exam-challenge")
            or headers.get("X-Exam-Challenge")
            or params.get("arguments", {}).get("challenge", "")
        )

        logger.info(f"Solving challenge for header challenge: '{challenge}'")
        res_hash = solve_challenge_hash(challenge)

        return {
            "jsonrpc": jsonrpc_ver,
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": res_hash
                    }
                ]
            }
        }

    # 5. MCP Ping
    elif method == "ping":
        return {
            "jsonrpc": jsonrpc_ver,
            "id": req_id,
            "result": {}
        }

    # Unknown method
    else:
        logger.warning(f"Unknown JSON-RPC method requested: {method}")
        if req_id is not None:
            return {
                "jsonrpc": jsonrpc_ver,
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        return None

@router.api_route("/mcp", methods=["GET", "POST", "OPTIONS"])
@router.api_route("/mcp/", methods=["GET", "POST", "OPTIONS"])
async def mcp_endpoint(request: Request):
    # Handle GET requests (healthcheck / browser / SSE status)
    if request.method == "GET":
        accept_header = request.headers.get("accept", "")
        if "text/event-stream" in accept_header:
            # Provide standard MCP SSE handshake event
            async def sse_stream():
                yield "event: endpoint\ndata: /mcp\n\n"
            from starlette.responses import StreamingResponse
            return StreamingResponse(sse_stream(), media_type="text/event-stream")
        return {
            "status": "online",
            "protocol": "Model Context Protocol (MCP)",
            "endpoint": "/mcp",
            "tools": ["solve_challenge"]
        }

    # Handle POST requests (JSON-RPC)
    try:
        body = await request.json()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
        )

    headers = dict(request.headers)

    # Batch JSON-RPC or single request
    if isinstance(body, list):
        responses = []
        for item in body:
            resp = handle_jsonrpc_request(item, headers)
            if resp is not None:
                responses.append(resp)
        return JSONResponse(content=responses)
    elif isinstance(body, dict):
        resp = handle_jsonrpc_request(body, headers)
        if resp is None:
            # Notification with no response needed
            return Response(status_code=204)
        return JSONResponse(content=resp)
    else:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: expected object or array"
                }
            }
        )
