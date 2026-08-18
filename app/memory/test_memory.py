from app.memory.memory import MemoryService


memory = MemoryService()


memory.remember(
    "The user is learning Rust and wants to become a strong backend engineer.",
    1,
)

memory.remember(
    "The user is building NEXUS, a personal operating system agent.",
    2,
)

memory.remember(
    "NEXUS uses FastAPI, LangGraph, Groq, MCP and SQLite.",
    3,
)


results = memory.recall(
    "What is the user building?"
)


print("\nMEMORY SEARCH RESULTS\n")

for result in results:

    print(
        f"Score: {result['score']:.4f}"
    )

    print(
        f"Memory: {result['text']}\n"
    )
