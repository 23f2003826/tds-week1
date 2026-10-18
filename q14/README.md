# Question 14: Public MCP Server Implementation

## Overview
This directory contains the Model Context Protocol (MCP) server implementation for Question 14 of IIT Madras TDS Week 1.

- **Student Email**: `23f2003826@ds.study.iitm.ac.in`
- **Protocol**: Model Context Protocol (MCP) over Streamable HTTP (JSON-RPC 2.0)
- **Tool Exposed**: `solve_challenge` (with empty input schema `{"type": "object", "properties": {}}`)
- **Required Header**: `X-Exam-Challenge` (32 lowercase hex characters)

## Protocol Lifecycle Implemented

1. **MCP Handshake (`initialize`)**:
   - Returns protocol version negotiation and declares tool capabilities.
   - Handshake confirmation handled for `notifications/initialized`.

2. **Tool Discovery (`tools/list`)**:
   - Exposes exactly one required tool named `solve_challenge`.
   - Tool input schema contains no required properties.

3. **Tool Execution (`tools/call`)**:
   - Tool: `solve_challenge`
   - Reads `X-Exam-Challenge` from incoming HTTP headers.
   - Computes:
     $$\text{response} = \text{SHA-256}(\text{challenge} : \text{normalizedEmail})[0:16]$$
   - Returns a single MCP text content block containing the 16 lowercase hex characters.

## Public Endpoint
The MCP server is deployed at:
```text
https://<your-render-domain>.onrender.com/mcp
```
*(Mounted onto the unified FastAPI gateway in `main.py`)*
