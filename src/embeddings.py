"""
Embedding generation for text chunks using sentence-transformers.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import os


class EmbeddingGenerator:
    """
    Generate embeddings for text using sentence-transformers models.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformers model to use
                       Default: "all-MiniLM-L6-v2" (fast and efficient)
                       Other options: "all-mpnet-base-v2" (better quality, slower)
        """
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.embedding_dim, dtype=np.float32)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar

        Returns:
            Numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([], dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        return embeddings.astype(np.float32)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.embedding_dim


class CachedEmbeddingGenerator(EmbeddingGenerator):
    """
    Embedding generator with caching to avoid recomputing embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_size: int = 10000):
        """
        Initialize the cached embedding generator.

        Args:
            model_name: Name of the sentence-transformers model
            cache_size: Maximum number of embeddings to cache
        """
        super().__init__(model_name)
        self.cache = {}
        self.cache_size = cache_size

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding with caching."""
        if not text or not text.strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)

        # Check cache
        if text in self.cache:
            return self.cache[text]

        # Generate embedding
        embedding = super().embed_text(text)

        # Add to cache if not full
        if len(self.cache) < self.cache_size:
            self.cache[text] = embedding

        return embedding

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """Generate embeddings for batch with caching."""
        if not texts:
            return np.array([], dtype=np.float32)

        # Separate cached and uncached texts
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            if text in self.cache:
                embeddings.append((i, self.cache[text]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = super().embed_batch(
                uncached_texts,
                batch_size=batch_size,
                show_progress=show_progress
            )

            # Add to cache and results
            for text, embedding, idx in zip(uncached_texts, new_embeddings, uncached_indices):
                if len(self.cache) < self.cache_size:
                    self.cache[text] = embedding
                embeddings.append((idx, embedding))

        # Sort by original index and return
        embeddings.sort(key=lambda x: x[0])
        return np.array([emb for _, emb in embeddings], dtype=np.float32)

    def clear_cache(self):
        """Clear the embedding cache."""
        self.cache.clear()
