from app.memory.vector_store import VectorStore


class MemoryService:

    def __init__(self):

        self.vector_store = VectorStore()

    def remember(
        self,
        text: str,
        memory_id: int,
    ):

        self.vector_store.add_memory(
            memory_id=memory_id,
            text=text,
        )

        return {
            "status": "stored",
            "text": text,
        }

    def recall(
        self,
        query: str,
        limit: int = 5,
    ):

        results = self.vector_store.search(
            query=query,
            limit=limit,
        )

        memories = []

        for result in results:

            memories.append(
                {
                    "score": result.score,
                    "text": result.payload["text"],
                }
            )

        return memories
