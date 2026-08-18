from fastembed import TextEmbedding

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)


COLLECTION_NAME = "nexus_memory"

VECTOR_SIZE = 384


class VectorStore:

    def __init__(self):

        self.client = QdrantClient(
            path="app/memory/qdrant_data"
        )

        self.embedding_model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        self._initialize_collection()


    def _initialize_collection(self):

        collections = self.client.get_collections()

        names = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME not in names:

            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )


    def _embed(self, text: str):

        embedding = next(
            self.embedding_model.embed([text])
        )

        return embedding.tolist()


    def add_memory(
        self,
        memory_id: int,
        text: str,
    ):

        vector = self._embed(text)

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=memory_id,
                    vector=vector,
                    payload={
                        "text": text,
                    },
                )
            ],
        )


    def search(
        self,
        query: str,
        limit: int = 5,
    ):

        vector = self._embed(query)

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit,
        )

        return results.points
