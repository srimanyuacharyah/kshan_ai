import math
import hashlib
import time
import re
from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

class BaseEmbeddingProvider(ABC):
    """Abstract base class for vector embedding generation."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string and return a normalized float vector."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        pass

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic semantic mock embedding provider for testing and local keyless development.
    Uses token-level hashing and subword projection with L2 unit normalization so that
    texts sharing semantic tokens exhibit high cosine similarity while unrelated texts exhibit near zero.
    """
    def __init__(self, dimension: Optional[int] = None):
        self.dimension = dimension or settings.EMBEDDING_DIMENSION

    def _generate_vector(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        clean_text = text.strip().lower()
        if not clean_text:
            return vec

        # Extract tokens (words and 3-grams)
        words = re.findall(r'\b\w+\b', clean_text)
        if not words:
            words = [clean_text]

        tokens = list(words)
        # Add character 3-grams for fuzzy matching
        for w in words:
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    tokens.append(w[i:i+3])

        # Project tokens onto vector dimensions
        for tok in tokens:
            hasher = hashlib.md5(tok.encode("utf-8"))
            digest = hasher.digest()
            # Distribute across 8 indices per token
            for k in range(8):
                idx = int.from_bytes(digest[k*2 : (k+1)*2], "little") % self.dimension
                val = ((digest[k] % 31) - 15) / 15.0
                vec[idx] += val

        # L2 unit normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        else:
            vec[0] = 1.0

        return vec

    async def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Production embedding provider utilizing Google GenAI SDK (Gemini embeddings).
    Validates that returned vector dimensionality matches settings.EMBEDDING_DIMENSION.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, dimension: Optional[int] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.EMBEDDING_MODEL
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured for GeminiEmbeddingProvider.")
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def embed_text(self, text: str) -> List[float]:
        start = time.perf_counter()
        try:
            client = self._get_client()
            response = client.models.embed_content(
                model=self.model,
                contents=text,
            )
            
            if hasattr(response, "embedding") and response.embedding:
                vector = response.embedding.values
            elif hasattr(response, "embeddings") and response.embeddings:
                vector = response.embeddings[0].values
            else:
                raise RuntimeError("Invalid response structure from Gemini embed_content.")

            if len(vector) != self.dimension:
                logger.warning(
                    f"Gemini embedding dimension mismatch: model returned {len(vector)}, configured {self.dimension}. Adjusting to match schema."
                )
                if len(vector) > self.dimension:
                    vector = vector[:self.dimension]
                else:
                    vector = list(vector) + [0.0] * (self.dimension - len(vector))
                
                norm = math.sqrt(sum(x * x for x in vector)) or 1.0
                vector = [x / norm for x in vector]

            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(f"Generated Gemini embedding for text ({len(text)} chars) in {elapsed_ms}ms")
            return list(vector)

        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {type(e).__name__}: {e}", exc_info=False)
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(await self.embed_text(text))
        return results

class EmbeddingService:
    """
    High-level embedding service factory and coordinator.
    Automatically chooses production Gemini provider or Mock provider based on configuration.
    """
    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None):
        if provider:
            self.provider = provider
        elif settings.GEMINI_API_KEY and not settings.DEMO_MODE:
            self.provider = GeminiEmbeddingProvider(
                api_key=settings.GEMINI_API_KEY,
                model=settings.EMBEDDING_MODEL,
                dimension=settings.EMBEDDING_DIMENSION
            )
        else:
            self.provider = MockEmbeddingProvider(dimension=settings.EMBEDDING_DIMENSION)

    async def get_embedding(self, text: str) -> List[float]:
        """Generate and return embedding vector."""
        if not text or not text.strip():
            return [0.0] * settings.EMBEDDING_DIMENSION
        return await self.provider.embed_text(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate and return embedding vectors for batch."""
        return await self.provider.embed_batch(texts)

embedding_service = EmbeddingService()
