from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from app.config.settings import GROQ_API_KEY

from app.agents.memory_tools import (
    remember_memory,
    recall_memory,
)


# =========================================================
# GROQ LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
)


# =========================================================
# MCP CLIENT
# =========================================================

mcp_client = MultiServerMCPClient(
    {
        "personal": {
            "command": "python",
            "args": [
                "mcp_servers/personal_server.py",
            ],
            "transport": "stdio",
            "env": {
                "PYTHONPATH": "/home/alpha/nexus",
            },
        }
    }
)


# =========================================================
# BUILD AGENT
# =========================================================

async def build_agent():

    print("Building NEXUS agent...")

    # -----------------------------------------------------
    # Load MCP tools
    # -----------------------------------------------------

    mcp_tools = await mcp_client.get_tools()

    print("\nNEXUS MCP TOOLS:")

    for tool in mcp_tools:
        print(f"  - {tool.name}")

    # -----------------------------------------------------
    # Local Qdrant memory tools
    # -----------------------------------------------------

    memory_tools = [
        remember_memory,
        recall_memory,
    ]

    print("\nNEXUS MEMORY TOOLS:")

    for tool in memory_tools:
        print(f"  - {tool.name}")

    # -----------------------------------------------------
    # Combine everything
    # -----------------------------------------------------

    tools = memory_tools + mcp_tools

    print("\nNEXUS ALL TOOLS:")

    for tool in tools:
        print(f"  - {tool.name}")

    # -----------------------------------------------------
    # Create LangGraph agent
    # -----------------------------------------------------

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=(
            "You are NEXUS, a personal operating system agent.\n\n"

            "You have access to two types of tools:\n"
            "1. Long-term semantic memory stored in Qdrant.\n"
            "2. Personal application tools provided through MCP, "
            "including task management.\n\n"

            "MEMORY RULES:\n"
            "- When the user explicitly tells you to remember "
            "personal information, use remember_memory.\n"
            "- When the user asks about something they previously "
            "told you, use recall_memory.\n"
            "- Do not invent memories.\n\n"

            "TASK RULES:\n"
            "- When the user asks to create a task, use create_task.\n"
            "- When the user asks to show, list, or view tasks, "
            "use list_tasks.\n"
            "- When the user asks to complete a task, use the "
            "appropriate task completion tool.\n"
            "- When the user asks to delete a task, use the "
            "appropriate task deletion tool.\n"
            "- Never use recall_memory to answer a task-management "
            "request when a task tool is available.\n\n"
            "FILESYSTEM RULES:\n"
            "- The filesystem is restricted to the NEXUS workspace.\n"
            "- Use list_files when the user asks what files exist.\n"
            "- Use read_file when the user asks to read a file.\n"
            "- Use create_file when the user asks to create a new file.\n"
            "- Use update_file when the user asks to modify an existing file.\n"
            "- Use delete_file when the user explicitly asks to delete a file.\n"
            "- Use search_files when the user asks to search the contents of files.\n"
            "- Never invent file contents.\n"
            "- Never attempt to access files outside the workspace.\n\n"
            "IMPORTANT:\n"
            "- Choose the appropriate tool for the user's request.\n"
            "- Do not call unrelated tools.\n"
            "- Do not repeatedly call the same tool for one request.\n"
            "- After receiving a tool result, analyze it and answer "
            "the user directly.\n"
            "- Once you have enough information, stop calling tools.\n"
            "EMAIL RULES:\n"
            "- Use list_emails when the user asks to see recent emails.\n"
            "- Use read_email when the user asks to read a specific email.\n"
            "- Use search_emails when the user asks to find an email.\n"
            "- Use send_email when the user explicitly asks to send an email.\n"
            "- Use reply_email when the user explicitly asks to reply to an email.\n"
            "- Never invent email contents.\n"
            "- Before sending an email, make sure the recipient, subject, and message are clear.\n"
            "- Do not send an email unless the user explicitly asks you to send it.\n\n"
        ),
    )

    print("\nNEXUS agent created successfully.")

    return agent
