# AI Agent with Monetized MCP Tools

A LangChain/LangGraph agent that connects to **monetized MCP servers** and pays for tool usage automatically via PayLink.

## Overview

This agent demonstrates how to:
- Connect to a monetized MCP server using `PayLinkTools`
- Automatically handle payments when calling paid tools
- Use LangGraph for agent orchestration
- Deploy with LangGraph Studio for development

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- OpenAI API key
- Running monetized MCP server (see `../example_mcp_server`)

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
# OpenAI for the LLM
OPENAI_API_KEY=your-openai-key

# PayLink wallet for payments
WALLET_CONNECTION_STRING=""
```

### Run the Agent

**Option 1: LangGraph Development Server**

```bash
langgraph dev
```

Access:
- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Docs: http://127.0.0.1:2024/docs

**Option 2: Interactive Notebook**

Open `notebooks/use_monitized_mcp.ipynb` in Jupyter or VS Code.

## How It Works

### 1. Connect to Monetized MCP Server

```python
from paylink.integrations.langchain_tools import PayLinkTools

# Connect to the monetized MCP server
client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# Get available tools with payment metadata
tools = client.list_tools()
```

### 2. Create LangChain Agent

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

llm = init_chat_model(model="gpt-4o-mini")

agent = create_agent(
    model=llm,
    tools=tools
)
```

### 3. Automatic Payment on Tool Calls

When the agent decides to call a tool:
1. `PayLinkTools` sends the request with wallet credentials
2. Payment is processed automatically
3. Tool result is returned to the agent

```python
# Direct tool call (for testing)
result = client.call_tool("add", {"a": 5, "b": 3})
# Payment of $0.10 processed automatically
print(result)  # 8
```

## Project Structure

```
agent/
├── src/
│   └── graph.py           # LangGraph agent definition
├── notebooks/
│   └── use_monitized_mcp.ipynb  # Interactive examples
├── langgraph.json         # LangGraph configuration
├── pyproject.toml         # Dependencies
└── .env                   # Environment variables (create this)
```

## LangGraph Configuration

`langgraph.json`:
```json
{
  "graphs": {
    "agent": "src/graph.py:agent"
  },
  "dependencies": ["."],
  "env": "./.env",
  "python_version": "3.13"
}
```

## Available Tools

Connected to the example MCP server:

| Tool       | Description            | Cost    |
|------------|------------------------|---------|
| `add`      | Add two integers       | $0.10   |
| `subtract` | Subtract two integers  | $0.20   |

## Example Interactions

### Via LangGraph Studio

1. Open Studio UI
2. Send a message: *"What is 42 plus 58?"*
3. Agent calls `add` tool (pays $0.10)
4. Returns: *"42 plus 58 equals 100"*

### Via API

```bash
curl -X POST http://127.0.0.1:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {"role": "user", "content": "Calculate 100 minus 37"}
      ]
    }
  }'
```

### Via Python

```python
from paylink.integrations.langchain_tools import PayLinkTools

client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# List tools
tools = client.list_tools()
for tool in tools:
    print(f"- {tool.name}: {tool.description}")

# Call a tool directly
result = client.call_tool("subtract", {"a": 100, "b": 37})
print(f"Result: {result}")  # 63
```

## Dependencies

```toml
dependencies = [
    "langchain>=1.1.0",
    "langchain-openai>=1.1.0",
    "langgraph>=1.0.4",
    "langgraph-cli[inmem]>=0.4.7",
    "paylink>=0.4.0",
    "ipykernel>=7.1.0",  # For notebooks
]
```

## Payment Flow

```
User Query: "What is 5 + 3?"
         │
         ▼
┌─────────────────────┐
│ LangGraph Agent     │
│ (GPT-4o-mini)       │
└─────────────────────┘
         │
         │ Decides to use "add" tool
         ▼
┌─────────────────────┐
│ PayLinkTools        │
│ - Attaches wallet   │
│   credentials       │
└─────────────────────┘
         │
         │ HTTP POST with wallet headers
         ▼
┌─────────────────────┐
│ MCP Server          │
│ - Processes payment │
│ - Executes tool     │
└─────────────────────┘
         │
         │ Result: 8
         ▼
┌─────────────────────┐
│ Agent Response      │
│ "5 + 3 = 8"         │
└─────────────────────┘
```

## Wallet Management

Ensure your agent wallet has sufficient balance:

- `add` tool costs $0.10 per call
- `subtract` tool costs $0.20 per call

Monitor your wallet balance through the PayLink dashboard.

## Troubleshooting

### "Connection refused" error
- Ensure the MCP server is running at `http://0.0.0.0:5003/mcp`
- Check if port 5003 is available

### "Insufficient balance" error
- Add funds to your agent wallet
- Verify `WALLET_CONNECTION_STRING` is correct

### "Invalid API key" error
- Check your `.env` file configuration
- Regenerate credentials from PayLink dashboard

---

Part of the [PayLink MCP Monetization Example](../README.md)
