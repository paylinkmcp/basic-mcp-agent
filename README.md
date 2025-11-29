# 💰 How to Monetize MCP Servers

A complete example demonstrating how developers can **monetize MCP (Model Context Protocol) servers** using PayLink, and how AI agents can consume these paid services.

## 📖 Overview

This project showcases the integration between:
- **MCP Servers** - Tools that AI models can use
- **PayLink** - A payment layer that enables monetization
- **AI Agents** - LangChain/LangGraph agents that pay to use tools

### Architecture

![How to Monetize MCP](./images/how%20to%20monitize%20mcp.png)

The diagram above illustrates the complete payment flow:

1. **Agent** initiates a call to a monetized MCP tool
2. **PayLink Infrastructure** validates the payment:
   - Checks if the Agent Wallet has sufficient balance
   - Transfers funds from Agent Wallet → MCP Wallet
3. **On Success**: Request is forwarded to the Monetized MCP Server, which executes the tool and returns the result
4. **On Failure** (Out of Credits): The agent is notified to request user funding

### How Payment Works

1. **Agent** calls a tool via `PayLinkTools`
2. **PayLink** intercepts the request and attaches the agent's wallet credentials
3. **MCP Server** receives the request with wallet context via `set_agent_wallet_from_scope()`
4. **@require_payment** decorator checks if payment is required and processes it
5. Payment is transferred from agent's wallet to server's wallet
6. **Tool executes** and returns the result

## 📁 Project Structure

```
how_to_monitize_mcp/
├── README.md                    # This file
├── example_mcp_server/          # The monetized MCP server
│   ├── main.py                  # Server implementation
│   ├── pyproject.toml           # Dependencies
│   └── README.md
└── agent/                       # The AI agent consumer
    ├── src/
    │   └── graph.py             # LangGraph agent definition
    ├── notebooks/
    │   └── use_monitized_mcp.ipynb  # Interactive example
    ├── langgraph.json           # LangGraph configuration
    ├── pyproject.toml           # Dependencies
    └── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **OpenAI API Key** - For the AI agent (set as `OPENAI_API_KEY`)
- **PayLink Account** - For wallet credentials

### Step 1: Start the Monetized MCP Server

```bash
# Navigate to the server directory
cd example_mcp_server

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Run the server
uv run main.py
```

The server will start at `http://0.0.0.0:5003/mcp`

### Step 2: Run the AI Agent

Open a new terminal:

```bash
# Navigate to the agent directory
cd agent

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Run the LangGraph development server
langgraph dev
```

The agent will be available at `http://127.0.0.1:2024` with Studio UI.

## 📝 Detailed Implementation

### Monetized MCP Server (`example_mcp_server/main.py`)

The MCP server exposes tools that **require payment** before execution:

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

#### 2. Add Payment Requirements with `@require_payment`

```python
from paylink.mcp.monetize_mcp import require_payment

@app.call_tool()
@require_payment(
    {
        "add": 0.10,       # $0.10 per call
        "subtract": 0.20,  # $0.20 per call
    }
)
async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if tool_name == "add":
        result = arguments["a"] + arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
    # ... handle other tools
```

#### 3. Extract Wallet Context from Requests

```python
from paylink.mcp.wallet_context import set_agent_wallet_from_scope, reset_agent_wallet

async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    # Extract wallet info from request headers
    token = set_agent_wallet_from_scope(scope)
    
    try:
        await session_manager.handle_request(scope, receive, send)
    finally:
        reset_agent_wallet(token)
```

### AI Agent (`agent/src/graph.py`)

The agent uses `PayLinkTools` to connect to monetized MCP servers:

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from paylink.integrations.langchain_tools import PayLinkTools

# Initialize the LLM
llm = init_chat_model(model="gpt-4o-mini")

# Connect to the monetized MCP server
client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# Get available tools (includes payment metadata)
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

# Connect to the monetized server
client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

# List available tools
tools = client.list_tools()
print(tools)

# Call a paid tool (payment is automatic)
result = client.call_tool("add", {"a": 5, "b": 3})
print(result)  # Output: 8
```

## 💳 Wallet Configuration

Both the agent and server need wallet configuration. Set up your `.env` file:

### For the MCP Server

```env
# Server receives payments to this wallet
MCP_WALLET_CONNECTION_STRING = ""
```

### For the Agent

```env
# Agent pays from this wallet
WALLET_CONNECTION_STRING=""
OPENAI_API_KEY=your-openai-key
```

## 🔧 Dependencies

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

## 🎯 Key Concepts

### What is MCP?

The **Model Context Protocol (MCP)** is an open standard that enables AI models to securely connect to external tools and data sources. It provides a standardized way for LLMs to:
- List available tools
- Call tools with arguments
- Receive structured responses

### What is PayLink?

**PayLink** is a payment layer that enables monetization of AI services. It provides:
- **Wallet management** for both service providers and consumers
- **Automatic payment processing** via decorators
- **Integration with popular frameworks** (LangChain, MCP, etc.)

### Why Monetize MCP Servers?

- **Tool developers** can earn revenue from their creations
- **Fair compensation** for computational resources and API calls
- **Sustainable ecosystem** for AI tool development
- **Pay-per-use model** that scales with actual usage

## 📊 Example Flow

```
User: "What is 15 plus 27?"

1. Agent receives the query
2. LLM decides to use the "add" tool
3. PayLinkTools sends request to MCP server
   - Includes wallet credentials in headers
4. MCP server's @require_payment checks:
   - Tool "add" costs $0.10
   - Agent wallet has sufficient balance
5. Payment is processed ($0.10 transferred)
6. Tool executes: 15 + 27 = 42
7. Result returned to agent
8. Agent responds: "15 plus 27 equals 42"
```

## 🛠 Customization

### Adding New Paid Tools

1. Add the tool definition in `list_tools()`
2. Add the pricing in `@require_payment` decorator
3. Implement the tool logic in `call_tool()`

```python
@require_payment(
    {
        "add": 0.10,
        "subtract": 0.20,
        "multiply": 0.15,      # New tool
        "divide": 0.25,        # New tool
    }
)
async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # ... existing logic
    elif tool_name == "multiply":
        result = arguments["a"] * arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
```

### Dynamic Pricing

You can also implement dynamic pricing based on:
- Input complexity
- Resource usage
- Time of day
- User tier

## 🔗 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [uv Documentation](https://docs.astral.sh/uv/)

## 📄 License

This example is provided for educational purposes as part of the PayLink SDK.

---

**Built with ❤️ using PayLink, MCP, and LangChain**

