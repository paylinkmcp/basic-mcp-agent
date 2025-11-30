# Basic MCP Server with PayLink Integration

A simple example demonstrating how to build an **MCP (Model Context Protocol) server** and connect it to an AI agent using PayLink infrastructure.

## Overview

This project showcases the integration between:
- **MCP Servers** - Tools that AI models can use
- **PayLink** - Infrastructure for connecting MCP servers to agents
- **AI Agents** - LangChain/LangGraph agents that use MCP tools


This example demonstrates a basic MCP server setup:

1. **MCP Server** exposes tools (add, subtract) via HTTP
2. **AI Agent** connects to the MCP server using `PayLinkTools`
3. **PayLink** provides the connection infrastructure between agent and server
4. **Tools execute** and return results to the agent

## Project Structure

```
basic-mcp+agent/
├── README.md                    # This file
├── example_mcp_server/          # The MCP server
│   ├── main.py                  # Server implementation
│   ├── pyproject.toml           # Dependencies
│   ├── .env.example             # Environment variable template
│   └── README.md
└── agent/                       # The AI agent consumer
    ├── src/
    │   └── graph.py             # LangGraph agent definition
    ├── notebooks/
    │   └── use_monitized_mcp.ipynb  # Interactive example
    ├── langgraph.json           # LangGraph configuration
    ├── pyproject.toml           # Dependencies
    ├── .env.example             # Environment variable template
    └── README.md
```

## Quick Start

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **OpenAI API Key** - For the AI agent


### Step 1: Start the MCP Server

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Run the server
uv run main.py
```

The server will start at `http://0.0.0.0:5003/mcp`

### Step 2: Configure the AI Agent

Open a new terminal:

```bash
# Navigate to the agent directory
cd agent

# Copy the environment template
cp .env.example .env

# Edit .env and replace the values with your custom values:
# - WALLET_CONNECTION_STRING (generate on PayLink platform)
# - OPENAI_API_KEY (your OpenAI API key)
```

### Step 3: Run the AI Agent

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Run the LangGraph development server
langgraph dev
```

The agent will be available at `http://127.0.0.1:2024` with Studio UI.

## Example Flow

```
User: "What is 15 plus 27?"

1. Agent receives the query
2. LLM decides to use the "add" tool
3. PayLinkTools sends request to MCP server
   - Includes wallet credentials in headers
4. MCP server receives the request
5. Tool executes: 15 + 27 = 42
6. Result returned to agent
7. Agent responds: "15 plus 27 equals 42"
```

## Customization

### Adding New Tools

1. Add the tool definition in `list_tools()`
2. Implement the tool logic in `call_tool()`

```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # ... existing tools
        types.Tool(
            name="multiply",
            description="Multiply two integers",
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

@app.call_tool()
async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # ... existing logic
    elif tool_name == "multiply":
        result = arguments["a"] * arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
```

## Resources

- [PayLink Documentation](https://paylink-c15dc1ba.mintlify.app/)

## License

This example is provided for educational purposes as part of the PayLink SDK.
