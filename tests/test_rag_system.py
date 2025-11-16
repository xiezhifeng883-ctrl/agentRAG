"""
Tests for the RAG system.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.document_loaders import (
    load_document, TXTLoader, PDFLoader, DOCXLoader,
    MarkdownLoader
)
from src.text_chunker import TextChunker, SemanticChunker
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore


class TestDocumentLoaders(unittest.TestCase):
    """Test document loaders."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_txt_loader(self):
        """Test TXT file loading."""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        test_content = "This is a test document.\nIt has multiple lines."

        with open(test_file, 'w') as f:
            f.write(test_content)

        # Load the document
        result = load_document(test_file)

        self.assertEqual(result['text'], test_content)
        self.assertEqual(result['metadata']['file_type'], 'txt')
        self.assertEqual(result['file_path'], test_file)

    def test_markdown_loader(self):
        """Test Markdown file loading."""
        test_file = os.path.join(self.test_dir, "test.md")
        test_content = "# Test Document\n\nThis is a **test** document."

        with open(test_file, 'w') as f:
            f.write(test_content)

        result = load_document(test_file)

        self.assertEqual(result['text'], test_content)
        self.assertEqual(result['metadata']['file_type'], 'markdown')

    def test_unsupported_format(self):
        """Test that unsupported formats raise an error."""
        test_file = os.path.join(self.test_dir, "test.xyz")

        with open(test_file, 'w') as f:
            f.write("test")

        with self.assertRaises(ValueError):
            load_document(test_file)


class TestTextChunker(unittest.TestCase):
    """Test text chunking."""

    def test_basic_chunking(self):
        """Test basic text chunking."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)

        text = "This is a test. " * 20  # Create a long text
        chunks = chunker.chunk_text(text)

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)
            self.assertIn('chunk_index', chunk)

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)

        text = "A" * 250  # Long text
        chunks = chunker.chunk_text(text)

        self.assertGreater(len(chunks), 1)

    def test_semantic_chunker(self):
        """Test semantic chunking."""
        chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)

        text = """# Introduction

This is the introduction.

# Methods

This is the methods section."""

        chunks = chunker.chunk_text(text)

        self.assertGreater(len(chunks), 0)

    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("")

        self.assertEqual(len(chunks), 0)


class TestEmbeddings(unittest.TestCase):
    """Test embedding generation."""

    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        # Use a small model for testing
        cls.embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

    def test_single_embedding(self):
        """Test generating a single embedding."""
        text = "This is a test sentence."
        embedding = self.embedder.embed_text(text)

        self.assertEqual(len(embedding.shape), 1)
        self.assertEqual(embedding.shape[0], self.embedder.embedding_dim)

    def test_batch_embeddings(self):
        """Test batch embedding generation."""
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence."
        ]
        embeddings = self.embedder.embed_batch(texts, show_progress=False)

        self.assertEqual(embeddings.shape[0], len(texts))
        self.assertEqual(embeddings.shape[1], self.embedder.embedding_dim)

    def test_empty_text_embedding(self):
        """Test embedding empty text."""
        embedding = self.embedder.embed_text("")

        self.assertEqual(len(embedding.shape), 1)
        self.assertEqual(embedding.shape[0], self.embedder.embedding_dim)


class TestVectorStore(unittest.TestCase):
    """Test vector store functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.store = VectorStore(self.embedding_dim)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_add_documents(self):
        """Test adding documents to vector store."""
        import numpy as np

        embeddings = np.random.rand(5, self.embedding_dim).astype(np.float32)
        texts = [f"Document {i}" for i in range(5)]
        metadata = [{'index': i} for i in range(5)]

        self.store.add_documents(embeddings, texts, metadata)

        stats = self.store.get_stats()
        self.assertEqual(stats['total_documents'], 5)
        self.assertEqual(stats['total_vectors'], 5)

    def test_search(self):
        """Test searching the vector store."""
        import numpy as np

        # Add some documents
        embeddings = np.random.rand(10, self.embedding_dim).astype(np.float32)
        texts = [f"Document {i}" for i in range(10)]

        self.store.add_documents(embeddings, texts)

        # Search
        query_embedding = np.random.rand(self.embedding_dim).astype(np.float32)
        results = self.store.search(query_embedding, top_k=3)

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('text', result)
            self.assertIn('score', result)
            self.assertIn('index', result)

    def test_save_and_load(self):
        """Test saving and loading vector store."""
        import numpy as np

        # Add documents
        embeddings = np.random.rand(5, self.embedding_dim).astype(np.float32)
        texts = [f"Document {i}" for i in range(5)]

        self.store.add_documents(embeddings, texts)

        # Save
        self.store.save(self.test_dir, "test_store")

        # Load
        loaded_store = VectorStore.load(self.test_dir, "test_store")

        # Verify
        stats = loaded_store.get_stats()
        self.assertEqual(stats['total_documents'], 5)
        self.assertEqual(len(loaded_store.documents), 5)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete RAG system."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

        # Create a test document
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("""Machine Learning Introduction

Machine learning is a subset of artificial intelligence.
It focuses on building systems that learn from data.

Types of Machine Learning:
1. Supervised Learning
2. Unsupervised Learning
3. Reinforcement Learning

Applications include image recognition, natural language processing, and more.""")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_end_to_end_without_api(self):
        """Test document loading, chunking, and embedding (no API calls)."""
        # Load document
        doc_data = load_document(self.test_file)
        self.assertIn('text', doc_data)
        self.assertIn('metadata', doc_data)

        # Chunk text
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text(
            doc_data['text'],
            metadata=doc_data['metadata']
        )
        self.assertGreater(len(chunks), 0)

        # Generate embeddings
        embedder = EmbeddingGenerator()
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = embedder.embed_batch(chunk_texts, show_progress=False)
        self.assertEqual(len(embeddings), len(chunks))

        # Add to vector store
        store = VectorStore(embedder.get_embedding_dimension())
        chunk_metadata = [chunk['metadata'] for chunk in chunks]
        store.add_documents(embeddings, chunk_texts, chunk_metadata)

        # Search
        query_embedding = embedder.embed_text("What is machine learning?")
        results = store.search(query_embedding, top_k=3)
        self.assertGreater(len(results), 0)
        self.assertIn('machine learning', results[0]['text'].lower())


def run_tests():
    """Run all tests."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentLoaders))
    suite.addTests(loader.loadTestsFromTestCase(TestTextChunker))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddings))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStore))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
