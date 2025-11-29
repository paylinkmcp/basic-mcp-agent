# Monetized MCP Server Example

A complete example of an MCP (Model Context Protocol) server with **integrated payment processing** using PayLink.

## Overview

This server demonstrates how to:
- Create an MCP-compliant HTTP server using Starlette
- Add **monetization** to tools using the `@require_payment` decorator
- Handle wallet context from incoming requests

## Features

| Tool       | Description           | Price per Call |
|------------|----------------------|----------------|
| `add`      | Add two integers     | $0.10          |
| `subtract` | Subtract two integers| $0.20          |

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file:

```env
MCP_WALLET_CONNECTION_STRING = ""
```

### Run the Server

```bash
uv run main.py
```

Options:
```bash
uv run main.py --port 5003          # Custom port (default: 5003)
uv run main.py --log-level DEBUG    # Set log level
uv run main.py --json-response      # Enable JSON responses
```

The server will be available at `http://0.0.0.0:5003/mcp`

## How It Works

### 1. Tool Definition

Tools are defined using the MCP types system:

```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="add",
            description="Add two integers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        ),
    ]
```

### 2. Payment Integration

The `@require_payment` decorator handles payment processing:

```python
from paylink.mcp.monetize_mcp import require_payment

@app.call_tool()
@require_payment(
    {
        "add": 0.10,       # Tool name -> price mapping
        "subtract": 0.20,
    }
)
async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # Tool implementation
    ...
```

### 3. Wallet Context Extraction

The server extracts wallet information from request headers:

```python
from paylink.mcp.wallet_context import set_agent_wallet_from_scope, reset_agent_wallet

async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    token = set_agent_wallet_from_scope(scope)
    try:
        await session_manager.handle_request(scope, receive, send)
    finally:
        reset_agent_wallet(token)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/mcp/`  | StreamableHTTP endpoint for MCP communication |

## Dependencies

```toml
dependencies = [
    "mcp[cli]>=1.21.0",    # MCP protocol implementation
    "click>=8.1",          # CLI argument parsing
    "httpx>=0.27",         # HTTP client
    "paylink>=0.4.0",      # Payment integration
]
```

## Testing

Use any MCP-compatible client or test with curl:

```bash
# List tools (basic request)
curl -X POST http://localhost:5003/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

For paid tool calls, the client must include wallet credentials in headers.

## Payment Flow

```
Client Request
     │
     ▼
┌────────────────────────────┐
│ set_agent_wallet_from_scope │◄── Extracts wallet from headers
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ @require_payment           │◄── Checks if tool requires payment
│ - Validates wallet         │
│ - Processes payment        │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ Tool Execution             │◄── Only runs if payment successful
└────────────────────────────┘
     │
     ▼
Response to Client
```

## Logs

Sample log output when running:

```
INFO:     Uvicorn running on http://0.0.0.0:5003
INFO:     127.0.0.1:65106 - "POST /mcp/ HTTP/1.1" 200 OK
mcp.server.lowlevel.server - INFO - Processing request of type ListT
```

## Extending

Add more paid tools by:

1. Adding to the tool list in `list_tools()`
2. Adding pricing to `@require_payment` dictionary
3. Implementing handler in `call_tool()`

---

Part of the [PayLink MCP Monetization Example](../README.md)
