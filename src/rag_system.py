"""
Main RAG system interface that integrates all components.
"""

import os
from typing import List, Dict, Optional, Union
from pathlib import Path
import shutil

from .document_loaders import load_document
from .text_chunker import TextChunker, SemanticChunker
from .embeddings import EmbeddingGenerator, CachedEmbeddingGenerator
from .vector_store import VectorStore, HybridVectorStore
from .rag_engine import RAGEngine, ConversationalRAGEngine


class RAGSystem:
    """
    Complete RAG system for document upload, processing, and querying.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        claude_model: str = "claude-3-5-sonnet-20241022",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        vector_store_path: str = "./data/vector_stores",
        upload_path: str = "./data/uploads",
        use_semantic_chunking: bool = True,
        use_hybrid_search: bool = False,
        conversational: bool = False
    ):
        """
        Initialize the RAG system.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            embedding_model: Sentence-transformers model name
            claude_model: Claude model to use
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            vector_store_path: Path to save/load vector stores
            upload_path: Path to store uploaded documents
            use_semantic_chunking: Use semantic chunking (preserves structure)
            use_hybrid_search: Use hybrid vector + keyword search
            conversational: Enable conversation history
        """
        # Get API key
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide api_key parameter or set ANTHROPIC_API_KEY env var"
            )

        # Initialize components
        print("Initializing RAG system...")

        # Embedding generator
        self.embedding_generator = CachedEmbeddingGenerator(embedding_model)

        # Text chunker
        if use_semantic_chunking:
            self.chunker = SemanticChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            self.chunker = TextChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

        # Vector store
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        if use_hybrid_search:
            self.vector_store = HybridVectorStore(embedding_dim)
        else:
            self.vector_store = VectorStore(embedding_dim)

        # RAG engine
        if conversational:
            self.rag_engine = ConversationalRAGEngine(
                api_key=self.api_key,
                model=claude_model
            )
        else:
            self.rag_engine = RAGEngine(
                api_key=self.api_key,
                model=claude_model
            )

        # Paths
        self.vector_store_path = vector_store_path
        self.upload_path = upload_path
        os.makedirs(vector_store_path, exist_ok=True)
        os.makedirs(upload_path, exist_ok=True)

        # Settings
        self.use_hybrid_search = use_hybrid_search
        self.conversational = conversational

        print("RAG system initialized successfully!")

    def add_document(
        self,
        file_path: str,
        copy_to_uploads: bool = True,
        show_progress: bool = True
    ) -> Dict:
        """
        Add a document to the RAG system.

        Args:
            file_path: Path to the document file
            copy_to_uploads: Copy file to uploads directory
            show_progress: Show progress during processing

        Returns:
            Dictionary with processing statistics
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"\nProcessing document: {file_path}")

        # Copy to uploads if requested
        if copy_to_uploads:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.upload_path, filename)
            shutil.copy2(file_path, dest_path)
            print(f"Copied to: {dest_path}")

        # Load document
        print("Loading document...")
        doc_data = load_document(file_path)

        # Chunk text
        print("Chunking text...")
        chunks = self.chunker.chunk_text(
            doc_data['text'],
            metadata=doc_data['metadata']
        )
        print(f"Created {len(chunks)} chunks")

        # Generate embeddings
        print("Generating embeddings...")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_generator.embed_batch(
            chunk_texts,
            show_progress=show_progress
        )

        # Add to vector store
        print("Adding to vector store...")
        chunk_metadata = [chunk['metadata'] for chunk in chunks]
        self.vector_store.add_documents(
            embeddings,
            chunk_texts,
            chunk_metadata
        )

        stats = {
            'file_path': file_path,
            'num_chunks': len(chunks),
            'file_type': doc_data['metadata'].get('file_type', 'unknown'),
            'metadata': doc_data['metadata']
        }

        print(f"Document added successfully! ({len(chunks)} chunks)")
        return stats

    def add_documents(
        self,
        file_paths: List[str],
        copy_to_uploads: bool = True,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Add multiple documents to the RAG system.

        Args:
            file_paths: List of file paths
            copy_to_uploads: Copy files to uploads directory
            show_progress: Show progress during processing

        Returns:
            List of processing statistics for each document
        """
        results = []
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{len(file_paths)}] Processing {file_path}")
            try:
                stats = self.add_document(
                    file_path,
                    copy_to_uploads=copy_to_uploads,
                    show_progress=show_progress
                )
                results.append(stats)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                results.append({
                    'file_path': file_path,
                    'error': str(e)
                })

        return results

    def query(
        self,
        question: str,
        top_k: int = 5,
        include_sources: bool = True,
        return_context: bool = False
    ) -> Union[str, Dict]:
        """
        Query the RAG system.

        Args:
            question: Question to ask
            top_k: Number of relevant chunks to retrieve
            include_sources: Include source information
            return_context: Return full response dict (not just text)

        Returns:
            Answer string or full response dictionary
        """
        if self.vector_store.index.ntotal == 0:
            return "No documents have been added to the system yet."

        print(f"\nQuery: {question}")
        print("Retrieving relevant context...")

        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(question)

        # Retrieve relevant chunks
        if self.use_hybrid_search and isinstance(self.vector_store, HybridVectorStore):
            context_chunks = self.vector_store.hybrid_search(
                query_embedding,
                question,
                top_k=top_k
            )
        else:
            context_chunks = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )

        print(f"Retrieved {len(context_chunks)} relevant chunks")

        # Generate response
        print("Generating response...")
        if self.conversational:
            response = self.rag_engine.chat(
                question,
                context_chunks,
                reset_history=False
            )
        else:
            response = self.rag_engine.generate_response(
                question,
                context_chunks,
                include_sources=include_sources
            )

        print("Response generated!")

        if return_context:
            return response
        else:
            return response['response']

    def query_stream(
        self,
        question: str,
        top_k: int = 5
    ):
        """
        Query the RAG system with streaming response.

        Args:
            question: Question to ask
            top_k: Number of relevant chunks to retrieve

        Yields:
            Response text chunks
        """
        if self.vector_store.index.ntotal == 0:
            yield "No documents have been added to the system yet."
            return

        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(question)

        # Retrieve relevant chunks
        if self.use_hybrid_search and isinstance(self.vector_store, HybridVectorStore):
            context_chunks = self.vector_store.hybrid_search(
                query_embedding,
                question,
                top_k=top_k
            )
        else:
            context_chunks = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )

        # Stream response
        for chunk in self.rag_engine.generate_streaming_response(
            question,
            context_chunks
        ):
            yield chunk

    def save(self, name: str = "vector_store"):
        """
        Save the vector store to disk.

        Args:
            name: Name for the saved vector store
        """
        self.vector_store.save(self.vector_store_path, name)
        print(f"Vector store saved as '{name}'")

    def load(self, name: str = "vector_store"):
        """
        Load a vector store from disk.

        Args:
            name: Name of the saved vector store
        """
        VectorStoreClass = HybridVectorStore if self.use_hybrid_search else VectorStore
        self.vector_store = VectorStoreClass.load(self.vector_store_path, name)
        print(f"Vector store '{name}' loaded successfully")

    def get_stats(self) -> Dict:
        """Get statistics about the RAG system."""
        return {
            'vector_store': self.vector_store.get_stats(),
            'embedding_model': self.embedding_generator.model_name,
            'embedding_dim': self.embedding_generator.embedding_dim,
            'claude_model': self.rag_engine.model,
            'chunker_type': type(self.chunker).__name__,
            'chunk_size': self.chunker.chunk_size,
            'chunk_overlap': self.chunker.chunk_overlap,
            'use_hybrid_search': self.use_hybrid_search,
            'conversational': self.conversational
        }

    def reset(self):
        """Clear all documents from the system."""
        self.vector_store.delete_all()
        if self.conversational:
            self.rag_engine.reset_conversation()
        print("RAG system reset successfully")


def create_rag_system(
    api_key: Optional[str] = None,
    **kwargs
) -> RAGSystem:
    """
    Convenience function to create a RAG system.

    Args:
        api_key: Anthropic API key
        **kwargs: Additional arguments for RAGSystem

    Returns:
        RAGSystem instance
    """
    return RAGSystem(api_key=api_key, **kwargs)
