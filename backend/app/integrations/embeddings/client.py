from typing import List


class EmbeddingClient:
    """
    Interface for M6 (Vector Embeddings Pipeline for pgvector/RAG).
    """

    async def generate_embedding(self, text: str) -> List[float]:
        # 1536-dim placeholder mock vector
        return [0.01] * 1536
