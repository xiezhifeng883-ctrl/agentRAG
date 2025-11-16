"""
Vector store for efficient similarity search using FAISS.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
import pickle
import os
from pathlib import Path


class VectorStore:
    """
    FAISS-based vector store for efficient similarity search.
    """

    def __init__(self, embedding_dim: int, index_type: str = "flat"):
        """
        Initialize the vector store.

        Args:
            embedding_dim: Dimension of the embedding vectors
            index_type: Type of FAISS index to use
                       "flat" - Exact search (default)
                       "ivf" - Inverted file index (faster for large datasets)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type

        # Create FAISS index
        if index_type == "flat":
            # Exact search using L2 distance
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif index_type == "ivf":
            # Approximate search using inverted file
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")

        # Store metadata for each vector
        self.metadata: List[Dict] = []
        self.documents: List[str] = []

    def add_documents(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: Optional[List[Dict]] = None
    ):
        """
        Add documents to the vector store.

        Args:
            embeddings: Numpy array of shape (n, embedding_dim)
            texts: List of text strings
            metadata: Optional list of metadata dictionaries
        """
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dim}, "
                f"got {embeddings.shape[1]}"
            )

        if len(embeddings) != len(texts):
            raise ValueError("Number of embeddings must match number of texts")

        # Train index if needed (for IVF)
        if self.index_type == "ivf" and not self.index.is_trained:
            if len(embeddings) < 100:
                print("Warning: IVF index requires at least 100 vectors for training. "
                      "Using available vectors.")
            self.index.train(embeddings)

        # Add vectors to index
        self.index.add(embeddings)

        # Store documents and metadata
        self.documents.extend(texts)

        if metadata is None:
            metadata = [{}] * len(texts)
        self.metadata.extend(metadata)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of dictionaries with 'text', 'metadata', 'score', and 'index'
        """
        if self.index.ntotal == 0:
            return []

        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:  # Valid result
                results.append({
                    'text': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(dist),  # L2 distance (lower is better)
                    'index': int(idx)
                })

        return results

    def save(self, directory: str, name: str = "vector_store"):
        """
        Save the vector store to disk.

        Args:
            directory: Directory to save the vector store
            name: Name prefix for the saved files
        """
        os.makedirs(directory, exist_ok=True)

        # Save FAISS index
        index_path = os.path.join(directory, f"{name}.index")
        faiss.write_index(self.index, index_path)

        # Save metadata and documents
        data_path = os.path.join(directory, f"{name}.pkl")
        with open(data_path, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'documents': self.documents,
                'embedding_dim': self.embedding_dim,
                'index_type': self.index_type
            }, f)

        print(f"Vector store saved to {directory}/{name}")

    @classmethod
    def load(cls, directory: str, name: str = "vector_store") -> 'VectorStore':
        """
        Load a vector store from disk.

        Args:
            directory: Directory containing the saved vector store
            name: Name prefix of the saved files

        Returns:
            VectorStore instance
        """
        # Load metadata and documents
        data_path = os.path.join(directory, f"{name}.pkl")
        with open(data_path, 'rb') as f:
            data = pickle.load(f)

        # Create vector store
        store = cls(
            embedding_dim=data['embedding_dim'],
            index_type=data['index_type']
        )

        # Load FAISS index
        index_path = os.path.join(directory, f"{name}.index")
        store.index = faiss.read_index(index_path)

        # Restore metadata and documents
        store.metadata = data['metadata']
        store.documents = data['documents']

        print(f"Vector store loaded from {directory}/{name}")
        print(f"Total documents: {len(store.documents)}")

        return store

    def delete_all(self):
        """Clear all documents from the vector store."""
        # Reset index
        if self.index_type == "flat":
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)

        # Clear metadata and documents
        self.metadata = []
        self.documents = []

    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.documents),
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'index_type': self.index_type
        }


class HybridVectorStore(VectorStore):
    """
    Vector store with hybrid search combining semantic and keyword search.
    """

    def __init__(self, embedding_dim: int, index_type: str = "flat"):
        """Initialize the hybrid vector store."""
        super().__init__(embedding_dim, index_type)
        self.keyword_index = {}  # Simple keyword index

    def add_documents(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: Optional[List[Dict]] = None
    ):
        """Add documents and build keyword index."""
        start_idx = len(self.documents)
        super().add_documents(embeddings, texts, metadata)

        # Build keyword index
        for i, text in enumerate(texts):
            words = set(text.lower().split())
            for word in words:
                if word not in self.keyword_index:
                    self.keyword_index[word] = []
                self.keyword_index[word].append(start_idx + i)

    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search using keyword matching.

        Args:
            query: Query string
            top_k: Number of top results to return

        Returns:
            List of matching documents
        """
        query_words = set(query.lower().split())
        doc_scores = {}

        # Calculate match scores
        for word in query_words:
            if word in self.keyword_index:
                for doc_idx in self.keyword_index[word]:
                    doc_scores[doc_idx] = doc_scores.get(doc_idx, 0) + 1

        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top k
        results = []
        for doc_idx, score in sorted_docs[:top_k]:
            results.append({
                'text': self.documents[doc_idx],
                'metadata': self.metadata[doc_idx],
                'score': float(score),
                'index': doc_idx
            })

        return results

    def hybrid_search(
        self,
        query_embedding: np.ndarray,
        query_text: str,
        top_k: int = 5,
        semantic_weight: float = 0.7
    ) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword search.

        Args:
            query_embedding: Query embedding vector
            query_text: Query text for keyword search
            top_k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)

        Returns:
            List of documents ranked by combined score
        """
        # Get semantic results
        semantic_results = self.search(query_embedding, top_k * 2)

        # Get keyword results
        keyword_results = self.keyword_search(query_text, top_k * 2)

        # Combine scores
        combined_scores = {}
        keyword_weight = 1.0 - semantic_weight

        # Normalize and combine semantic scores (lower L2 distance is better)
        if semantic_results:
            max_semantic = max(r['score'] for r in semantic_results)
            for result in semantic_results:
                idx = result['index']
                # Invert and normalize L2 distance
                normalized_score = 1.0 - (result['score'] / (max_semantic + 1e-6))
                combined_scores[idx] = semantic_weight * normalized_score

        # Add keyword scores
        if keyword_results:
            max_keyword = max(r['score'] for r in keyword_results)
            for result in keyword_results:
                idx = result['index']
                normalized_score = result['score'] / max_keyword
                if idx in combined_scores:
                    combined_scores[idx] += keyword_weight * normalized_score
                else:
                    combined_scores[idx] = keyword_weight * normalized_score

        # Sort by combined score
        sorted_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top k
        results = []
        for idx, score in sorted_indices[:top_k]:
            results.append({
                'text': self.documents[idx],
                'metadata': self.metadata[idx],
                'score': float(score),
                'index': int(idx)
            })

        return results
