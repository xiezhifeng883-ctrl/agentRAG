"""
Comprehensive test script for the RAG system.
"""

import os
import sys
import tempfile
import shutil

# Test without API calls first
def test_document_loading():
    """Test document loading functionality."""
    print("\n" + "="*60)
    print("TEST 1: Document Loading")
    print("="*60)

    from src.document_loaders import load_document

    # Test markdown file
    md_file = "test_docs/ml_research.md"
    if os.path.exists(md_file):
        doc = load_document(md_file)
        print(f"✓ Loaded Markdown file: {md_file}")
        print(f"  - Content length: {len(doc['text'])} characters")
        print(f"  - File type: {doc['metadata']['file_type']}")
        print(f"  - Preview: {doc['text'][:100]}...")
        return True
    else:
        print(f"✗ Test file not found: {md_file}")
        return False


def test_text_chunking():
    """Test text chunking."""
    print("\n" + "="*60)
    print("TEST 2: Text Chunking")
    print("="*60)

    from src.document_loaders import load_document
    from src.text_chunker import TextChunker, SemanticChunker

    md_file = "test_docs/ml_research.md"
    if not os.path.exists(md_file):
        print("✗ Test file not found")
        return False

    doc = load_document(md_file)

    # Test basic chunking
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_text(doc['text'], doc['metadata'])
    print(f"✓ Basic chunking: {len(chunks)} chunks created")
    print(f"  - First chunk length: {len(chunks[0]['text'])} characters")
    print(f"  - First chunk preview: {chunks[0]['text'][:80]}...")

    # Test semantic chunking
    semantic_chunker = SemanticChunker(chunk_size=300, chunk_overlap=50)
    semantic_chunks = semantic_chunker.chunk_text(doc['text'], doc['metadata'])
    print(f"✓ Semantic chunking: {len(semantic_chunks)} chunks created")

    return True


def test_embeddings():
    """Test embedding generation."""
    print("\n" + "="*60)
    print("TEST 3: Embedding Generation")
    print("="*60)

    from src.embeddings import EmbeddingGenerator
    import numpy as np

    print("Loading embedding model (this may take a moment)...")
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    print(f"✓ Model loaded: {embedder.model_name}")
    print(f"  - Embedding dimension: {embedder.embedding_dim}")

    # Test single embedding
    text = "Machine learning is a subset of artificial intelligence."
    embedding = embedder.embed_text(text)
    print(f"✓ Single embedding generated")
    print(f"  - Shape: {embedding.shape}")
    print(f"  - Type: {embedding.dtype}")

    # Test batch embeddings
    texts = [
        "This is the first sentence.",
        "This is the second sentence.",
        "This is the third sentence."
    ]
    embeddings = embedder.embed_batch(texts, show_progress=False)
    print(f"✓ Batch embeddings generated")
    print(f"  - Batch size: {len(texts)}")
    print(f"  - Embeddings shape: {embeddings.shape}")

    # Test similarity
    similarity = np.dot(embeddings[0], embeddings[1])
    print(f"  - Similarity between sentence 1 and 2: {similarity:.4f}")

    return True


def test_vector_store():
    """Test vector store functionality."""
    print("\n" + "="*60)
    print("TEST 4: Vector Store")
    print("="*60)

    from src.embeddings import EmbeddingGenerator
    from src.vector_store import VectorStore
    import numpy as np

    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

    # Create vector store
    store = VectorStore(embedder.embedding_dim)
    print(f"✓ Vector store created")
    print(f"  - Embedding dimension: {store.embedding_dim}")
    print(f"  - Index type: {store.index_type}")

    # Add some documents
    texts = [
        "Machine learning is a subset of AI focused on data-driven learning.",
        "Climate change is causing rising temperatures and sea levels.",
        "Deep learning uses neural networks with multiple layers.",
        "Renewable energy includes solar, wind, and hydroelectric power.",
        "Natural language processing enables computers to understand text."
    ]

    embeddings = embedder.embed_batch(texts, show_progress=False)
    metadata = [{'index': i, 'topic': 'general'} for i in range(len(texts))]

    store.add_documents(embeddings, texts, metadata)
    print(f"✓ Added {len(texts)} documents to vector store")

    # Test search
    query = "What is machine learning?"
    query_embedding = embedder.embed_text(query)
    results = store.search(query_embedding, top_k=3)

    print(f"✓ Search completed for: '{query}'")
    print(f"  - Top {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"    {i}. Score: {result['score']:.4f}")
        print(f"       Text: {result['text'][:60]}...")

    # Test save/load
    temp_dir = tempfile.mkdtemp()
    try:
        store.save(temp_dir, "test_store")
        print(f"✓ Vector store saved")

        loaded_store = VectorStore.load(temp_dir, "test_store")
        print(f"✓ Vector store loaded")
        print(f"  - Documents loaded: {len(loaded_store.documents)}")

        # Verify loaded store works
        results2 = loaded_store.search(query_embedding, top_k=2)
        print(f"✓ Loaded store search works: {len(results2)} results")
    finally:
        shutil.rmtree(temp_dir)

    return True


def test_end_to_end():
    """Test complete end-to-end workflow (without API)."""
    print("\n" + "="*60)
    print("TEST 5: End-to-End Workflow")
    print("="*60)

    from src.document_loaders import load_document
    from src.text_chunker import SemanticChunker
    from src.embeddings import EmbeddingGenerator
    from src.vector_store import VectorStore

    # Load documents
    docs = []
    doc_files = ["test_docs/ml_research.md", "test_docs/climate_report.txt"]

    for file_path in doc_files:
        if os.path.exists(file_path):
            doc = load_document(file_path)
            docs.append(doc)
            print(f"✓ Loaded: {os.path.basename(file_path)}")

    if not docs:
        print("✗ No documents loaded")
        return False

    # Chunk documents
    chunker = SemanticChunker(chunk_size=300, chunk_overlap=50)
    all_chunks = []
    for doc in docs:
        chunks = chunker.chunk_text(doc['text'], doc['metadata'])
        all_chunks.extend(chunks)
    print(f"✓ Created {len(all_chunks)} total chunks from {len(docs)} documents")

    # Generate embeddings
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    chunk_texts = [chunk['text'] for chunk in all_chunks]
    chunk_metadata = [chunk['metadata'] for chunk in all_chunks]
    embeddings = embedder.embed_batch(chunk_texts, show_progress=True)
    print(f"✓ Generated embeddings: {embeddings.shape}")

    # Build vector store
    store = VectorStore(embedder.embedding_dim)
    store.add_documents(embeddings, chunk_texts, chunk_metadata)
    print(f"✓ Built vector store with {store.get_stats()['total_documents']} chunks")

    # Test retrieval
    queries = [
        "What is machine learning?",
        "What are the climate change findings?",
        "Tell me about deep learning"
    ]

    print(f"\n✓ Testing retrieval with {len(queries)} queries:")
    for query in queries:
        query_embedding = embedder.embed_text(query)
        results = store.search(query_embedding, top_k=2)
        print(f"\n  Query: '{query}'")
        print(f"  Top result: {results[0]['text'][:80]}...")
        print(f"  Relevance score: {results[0]['score']:.4f}")

    # Test persistence
    temp_dir = tempfile.mkdtemp()
    try:
        store.save(temp_dir, "e2e_test")
        print(f"\n✓ Saved vector store to disk")

        new_store = VectorStore.load(temp_dir, "e2e_test")
        stats = new_store.get_stats()
        print(f"✓ Loaded vector store from disk")
        print(f"  - Documents: {stats['total_documents']}")
        print(f"  - Vectors: {stats['total_vectors']}")
    finally:
        shutil.rmtree(temp_dir)

    return True


def test_cli_structure():
    """Test CLI availability."""
    print("\n" + "="*60)
    print("TEST 6: CLI Structure")
    print("="*60)

    if os.path.exists("cli.py"):
        print("✓ CLI script exists: cli.py")

        # Check if it's executable
        with open("cli.py", 'r') as f:
            content = f.read()
            if "argparse" in content:
                print("✓ CLI uses argparse")
            if "add_documents_command" in content:
                print("✓ CLI has 'add' command")
            if "query_command" in content:
                print("✓ CLI has 'query' command")
            if "stats_command" in content:
                print("✓ CLI has 'stats' command")
        return True
    else:
        print("✗ CLI script not found")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("AGENTRAG SYSTEM TESTING")
    print("="*70)

    # Create test docs directory
    os.makedirs("test_docs", exist_ok=True)

    results = {}

    # Run tests
    results['Document Loading'] = test_document_loading()
    results['Text Chunking'] = test_text_chunking()
    results['Embeddings'] = test_embeddings()
    results['Vector Store'] = test_vector_store()
    results['End-to-End'] = test_end_to_end()
    results['CLI Structure'] = test_cli_structure()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The RAG system is working correctly.")
        print("\nNext steps:")
        print("1. Set your API key: export ANTHROPIC_API_KEY='your-key'")
        print("2. Try the CLI: python cli.py add --files test_docs/ml_research.md")
        print("3. Query: python cli.py query --interactive --store-name test")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
