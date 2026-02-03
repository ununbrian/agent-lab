from __future__ import annotations

import os
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "agent_memory")


class MemoryStore:
    def __init__(self):
        # Qdrant running on localhost:6333
        self.client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.dim = 384

        # Create collection if not exists
        existing = {c.name for c in self.client.get_collections().collections}
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def save(self, query: str, answer: str, sources: List[str]) -> None:
        vec = self.embed(answer)

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "query": query,
                "answer": answer,
                "sources": sources,
            },
        )

        self.client.upsert(collection_name=COLLECTION_NAME, points=[point])

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        vec = self.embed(query)

        res = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vec,
            limit=top_k,
            with_payload=True,
        )

        hits = res.points or []
        return [h.payload for h in hits if h.payload]
