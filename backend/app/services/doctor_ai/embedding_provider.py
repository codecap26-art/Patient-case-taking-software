import os
import logging
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Configurable Embedding provider ported from DoctorAI repository.
    Generates dense vector embeddings for clinical documents & knowledge base queries.
    """

    def __init__(self):
        self.api_key = (
            os.getenv("EMBEDDING_API_KEY")
            or getattr(settings, "AI_API_KEY", None)
            or os.getenv("AI_API_KEY")
            or "dummy-key"
        )
        self.base_url = os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=15.0,
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for the given clinical text.
        Falls back to deterministic normalized pseudo-embedding if API is unreachable.
        """
        try:
            response = await self.client.embeddings.create(
                input=[text],
                model=self.model,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning("External embedding API error (%s); using fallback vector", e)
            # Deterministic 1536-dim fallback vector based on hash for offline/dev operation
            import hashlib
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
            import random
            rng = random.Random(seed)
            vec = [rng.uniform(-0.1, 0.1) for _ in range(1536)]
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            return [x / norm for x in vec]


embedding_provider = EmbeddingProvider()
