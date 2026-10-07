import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a specialized assistant for currency conversions. "
    "Your sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. "
    "If the user asks about anything other than currency conversion or exchange rates, "
    "politely state that you cannot help with that topic and can only assist with currency-related queries. "
    "Do not attempt to answer unrelated questions or use tools for other purposes."
)

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
if not mcp_server_url.endswith("/mcp"):
    mcp_server_url = f"{mcp_server_url.rstrip('/')}/mcp"

logger.info(f"--- 🔧 Loading MCP tools from MCP Server at {mcp_server_url}... ---")
logger.info("--- 🤖 Creating ADK Currency Agent... ---")

root_agent = LlmAgent(
    model="gemini-3.8-flash",
    name="currency_agent",
    description="An agent that can help with currency conversions",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=mcp_server_url
            )
        )
    ],
)

# Make the agent definition pure ADK.
# Serving and A2A exposure are managed via ADK CLI (adk api_server --a2a, adk deploy cloud_run --a2a).

