from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

                                               
                                                                    
                                           
MCP_SERVERS: dict[str, StdioServerParameters] = {
    "pubmed": StdioServerParameters(
        command="uv",
        args=["run", "--project", "mcp_servers/pubmed_server", "python", "mcp_servers/pubmed_server/server.py"],
    ),
    "drugdata": StdioServerParameters(
        command="uv",
        args=["run", "--project", "mcp_servers/drugdata_server", "python", "mcp_servers/drugdata_server/server.py"],
    ),
    "vectorstore": StdioServerParameters(
        command="uv",
        args=["run", "--project", "mcp_servers/vectorstore_server", "python", "mcp_servers/vectorstore_server/server.py"],
    ),
}

@asynccontextmanager
async def mcp_session(server_name: str):
    params = MCP_SERVERS[server_name]
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call_mcp_tool(server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
    try:
        async with mcp_session(server_name) as session:
            result = await session.call_tool(tool_name, arguments=arguments)
                                                                           
                                                               
            texts = [block.text for block in result.content if hasattr(block, "text")]
            return texts[0] if texts else None
    except Exception as exc:                
        print(f"[mcp_client] error calling {server_name}.{tool_name}: {exc}", file=sys.stderr)
        return None
