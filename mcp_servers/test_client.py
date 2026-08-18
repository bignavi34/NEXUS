import asyncio

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=[
            "mcp_servers/personal_server.py"
        ],
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            print("Initializing MCP connection...")

            await session.initialize()

            print("MCP connection established!")

            tools = await session.list_tools()

            print("\nAvailable tools:")

            for tool in tools.tools:
                print(
                    f"- {tool.name}: "
                    f"{tool.description}"
                )

            print("\nTesting get_current_time...")

            result = await session.call_tool(
                "get_current_time",
                {}
            )

            print("Result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
