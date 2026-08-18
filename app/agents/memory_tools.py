from langchain_core.tools import tool

from app.memory.vector_store import VectorStore


vector_store = VectorStore()


@tool
def remember_memory(text: str) -> str:
    """
    Store an important piece of information about the user
    in NEXUS long-term memory.
    """

    # Temporary ID generation
    existing = vector_store.client.count(
        collection_name="nexus_memory"
    )

    memory_id = existing.count + 1

    vector_store.add_memory(
        memory_id=memory_id,
        text=text,
    )

    print(f"[MEMORY] Stored: {text}")

    return f"Memory stored successfully: {text}"


@tool
def recall_memory(query: str) -> str:
    """
    Search long-term memory for information relevant
    to the user's query.
    """

    results = vector_store.search(
        query=query,
        limit=5,
    )

    print(f"[MEMORY] Recall query: {query}")
    print(f"[MEMORY] Found {len(results)} memories")

    if not results:
        return "No relevant memories found."

    memories = []

    for result in results:

        text = result.payload.get("text")

        if text:
            memories.append(text)

    if not memories:
        return "No relevant memories found."

    return (
        "Relevant memories from long-term memory:\n"
        + "\n".join(
            f"- {memory}"
            for memory in memories
        )
    )
