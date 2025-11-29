from langchain.agents import create_agent

from langchain.chat_models import init_chat_model

from paylink.integrations.langchain_tools import PayLinkTools

llm = init_chat_model(model="gpt-4o-mini")


client = PayLinkTools(base_url="http://0.0.0.0:5003/mcp")

tools = client.list_tools()

agent = create_agent(
    model=llm,
    tools=tools
)