from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def mcp_session():

    server_params = StdioServerParameters(
        command="python",
        args=[
            "mcp_servers/personal_server.py",
        ],
        env={
            "PYTHONPATH": "/home/alpha/nexus",
        },
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            yield session
