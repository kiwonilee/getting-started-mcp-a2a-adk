"""Script to generate agent.json for currency_agent.

This script creates the A2A Agent Card file (agent.json) required by ADK
for serving over A2A (e.g. via `adk api_server --a2a` or `adk deploy cloud_run --a2a`).

NOTE:
    Before running this script, make sure the Currency MCP Server is running:
    - Locally: `uv run python currency_mcp_server/server.py`
    - Or on Cloud Run: pass `MCP_SERVER_URL="https://.../mcp"`
    
    AgentCardBuilder inspects the active MCP tools (e.g. get_exchange_rate)
    to populate the agent's skills in the generated Agent Card.
"""

import argparse
import asyncio
import logging
from pathlib import Path

from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from google.protobuf.json_format import MessageToJson

from currency_agent.agent import root_agent

logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_agent_card(rpc_url: str, output_path: Path) -> None:
    logger.info("Generating Agent Card for '%s'...", root_agent.name)
    logger.info("Configured RPC URL: %s", rpc_url)

    builder = AgentCardBuilder(
        agent=root_agent,
        rpc_url=rpc_url,
    )

    card = await builder.build()
    json_str = MessageToJson(card, preserving_proto_field_name=False, indent=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(json_str)

    logger.info("✅ Successfully generated Agent Card at: %s", output_path.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate A2A agent.json card for currency_agent")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8081/a2a/currency_agent",
        help="The public or local RPC URL where the agent will be served (default: http://localhost:8081/a2a/currency_agent)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(__file__).parent / "agent.json"),
        help="Path where agent.json should be saved (default: currency_agent/agent.json)",
    )
    args = parser.parse_args()

    asyncio.run(generate_agent_card(rpc_url=args.url, output_path=Path(args.output)))


if __name__ == "__main__":
    main()
