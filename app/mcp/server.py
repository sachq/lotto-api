import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from app.mcp.tools import draws, predictions, ingestion, analytics

logging.basicConfig(level=logging.INFO)

server = Server("lotto-mcp")

ALL_TOOLS = draws.TOOLS + predictions.TOOLS + ingestion.TOOLS + analytics.TOOLS
ALL_HANDLERS = {
    **draws.HANDLERS,
    **predictions.HANDLERS,
    **ingestion.HANDLERS,
    **analytics.HANDLERS,
}


@server.list_tools()
async def list_tools():
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    handler = ALL_HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    result = await asyncio.to_thread(handler, arguments)
    return [TextContent(type="text", text=result)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
