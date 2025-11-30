# Basic MCP Server with PayLink Integration

A simple example demonstrating how to build an **MCP (Model Context Protocol) server** and connect it to an AI agent using PayLink infrastructure.

## Overview

This project showcases the integration between:
- **MCP Servers** - Tools that AI models can use
- **PayLink** - Infrastructure for connecting MCP servers to agents
- **AI Agents** - LangChain/LangGraph agents that use MCP tools

### Architecture

![How to Monetize MCP](./images/how%20to%20monitize%20mcp.png)

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
- **PayLink Account** - For wallet connection strings

### Step 1: Configure the MCP Server

```bash
# Navigate to the server directory
cd example_mcp_server

# Copy the environment template
cp .env.example .env

# Edit .env and add your MCP_WALLET_CONNECTION_STRING
# Generate this value on the PayLink platform
```

### Step 2: Start the MCP Server

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

### Step 3: Configure the AI Agent

Open a new terminal:

```bash
# Navigate to the agent directory
cd agent

# Copy the environment template
cp .env.example .env

# Edit .env and add:
# - WALLET_CONNECTION_STRING (generate on PayLink platform)
# - OPENAI_API_KEY (your OpenAI API key)
```

### Step 4: Run the AI Agent

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

## Detailed Implementation

### MCP Server (`example_mcp_server/main.py`)

The MCP server exposes simple tools via HTTP:

#### 1. Define Tools

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
        types.Tool(
            name="subtract",
            description="Subtract two integers",
            inputSchema={...},
        ),
    ]
```

#### 2. Implement Tool Handlers

```python
@app.call_tool()
async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if tool_name == "add":
        result = arguments["a"] + arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
    elif tool_name == "subtract":
        result = arguments["a"] - arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
    # ... handle other tools
```

#### 3. Set Up HTTP Server

```python
session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    json_response=json_response,
    stateless=True,
)

async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    try:
        await session_manager.handle_request(scope, receive, send)
    except Exception:
        logger.exception("Streamable HTTP error")
```

### AI Agent (`agent/src/graph.py`)

The agent uses `PayLinkTools` to connect to the MCP server:

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from paylink.integrations.langchain_tools import PayLinkTools

# Initialize the LLM
llm = init_chat_model(model="gpt-4o-mini")

# Connect to the MCP server via PayLink
client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# Get available tools
tools = client.list_tools()

# Create the agent with the tools
agent = create_agent(
    model=llm,
    tools=tools
)
```

### Using the Notebook

The interactive notebook (`agent/notebooks/use_monitized_mcp.ipynb`) demonstrates direct tool usage:

```python
from paylink.integrations.langchain_tools import PayLinkTools

# Connect to the MCP server
client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# List available tools
tools = client.list_tools()
print(tools)

# Call a tool
result = client.call_tool("add", {"a": 5, "b": 3})
print(result)  # Output: 8
```

## Environment Configuration

Both the agent and server need environment configuration. Follow these steps:

### For the MCP Server

1. Navigate to `example_mcp_server` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Generate `MCP_WALLET_CONNECTION_STRING` on the PayLink platform
4. Add it to your `.env` file:
   ```env
   MCP_WALLET_CONNECTION_STRING="your-connection-string-here"
   ```

### For the Agent

1. Navigate to `agent` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Generate `WALLET_CONNECTION_STRING` on the PayLink platform
4. Add your OpenAI API key
5. Update your `.env` file:
   ```env
   WALLET_CONNECTION_STRING="your-connection-string-here"
   OPENAI_API_KEY=your-openai-key
   ```

## Dependencies

### MCP Server

```toml
dependencies = [
    "mcp[cli]>=1.21.0",
    "click>=8.1",
    "httpx>=0.27",
    "paylink>=0.4.0",
]
```

### Agent

```toml
dependencies = [
    "langchain>=1.1.0",
    "langchain-openai>=1.1.0",
    "langgraph>=1.0.4",
    "langgraph-cli[inmem]>=0.4.7",
    "paylink>=0.4.0",
]
```

## Key Concepts

### What is MCP?

The **Model Context Protocol (MCP)** is an open standard that enables AI models to securely connect to external tools and data sources. It provides a standardized way for LLMs to:
- List available tools
- Call tools with arguments
- Receive structured responses

### What is PayLink?

**PayLink** provides infrastructure for connecting MCP servers to AI agents. It provides:
- **Wallet management** for both service providers and consumers
- **Connection infrastructure** between agents and MCP servers
- **Integration with popular frameworks** (LangChain, MCP, etc.)

### Why Use PayLink with MCP Servers?

- **Standardized connection** between agents and MCP servers
- **Secure communication** with wallet-based authentication
- **Easy integration** with LangChain and LangGraph agents
- **Foundation for monetization** when you're ready to add payment features

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

- [MCP Documentation](https://modelcontextprotocol.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [uv Documentation](https://docs.astral.sh/uv/)

## License

This example is provided for educational purposes as part of the PayLink SDK.
