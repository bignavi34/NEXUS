import asyncio

from app.mcp.client import mcp_session


async def main():

    async with mcp_session() as session:

        tools = await session.list_tools()

        print("\nNEXUS MCP TOOLS\n")

        for tool in tools.tools:
            print(
                f"- {tool.name}"
            )

        print("\nTesting tool...\n")

        result = await session.call_tool(
            "get_current_time",
            {}
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())
