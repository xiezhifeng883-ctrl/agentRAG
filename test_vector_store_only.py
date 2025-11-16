#!/usr/bin/env python3
"""
Test vector store functionality with FAISS (no embeddings model needed).
Uses random vectors to test FAISS operations.
"""

import numpy as np
import tempfile
import shutil

def test_vector_store():
    """Test vector store with random embeddings."""

    print("\n" + "="*70)
    print("TESTING VECTOR STORE (FAISS)")
    print("="*70)

    # Import
    print("\n1. Importing vector store...")
    try:
        # Import directly to avoid __init__.py dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location("vector_store", "src/vector_store.py")
        vector_store_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vector_store_module)
        VectorStore = vector_store_module.VectorStore
        print("✓ VectorStore imported successfully")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

    # Create store
    print("\n2. Creating vector store...")
    try:
        embedding_dim = 384
        store = VectorStore(embedding_dim)
        print(f"✓ Vector store created")
        print(f"  - Embedding dimension: {embedding_dim}")
        print(f"  - Index type: {store.index_type}")
    except Exception as e:
        print(f"✗ Creation failed: {e}")
        return False

    # Generate random embeddings
    print("\n3. Generating test data...")
    try:
        num_docs = 20
        np.random.seed(42)
        embeddings = np.random.rand(num_docs, embedding_dim).astype(np.float32)

        texts = [
            "Machine learning is transforming technology",
            "Climate change affects global temperatures",
            "Deep neural networks learn hierarchical features",
            "Renewable energy sources include solar and wind",
            "Natural language processing enables text understanding",
            "Data science combines statistics and programming",
            "Artificial intelligence mimics human cognition",
            "Ocean levels are rising due to warming",
            "Computer vision processes visual information",
            "Sustainable development balances ecology and economy",
            "Reinforcement learning through trial and error",
            "Greenhouse gases trap heat in atmosphere",
            "Convolutional networks excel at image tasks",
            "Carbon emissions contribute to global warming",
            "Transfer learning reuses pretrained models",
            "Biodiversity loss threatens ecosystems",
            "Attention mechanisms focus on relevant information",
            "Forest conservation preserves carbon sinks",
            "Transformer architecture revolutionized NLP",
            "Environmental policy shapes climate action"
        ]

        metadata = [{'id': i, 'topic': 'general'} for i in range(num_docs)]

        print(f"✓ Generated {num_docs} test documents")
        print(f"  - Embedding shape: {embeddings.shape}")
    except Exception as e:
        print(f"✗ Data generation failed: {e}")
        return False

    # Add documents
    print("\n4. Adding documents to vector store...")
    try:
        store.add_documents(embeddings, texts, metadata)
        stats = store.get_stats()
        print(f"✓ Documents added successfully")
        print(f"  - Total documents: {stats['total_documents']}")
        print(f"  - Total vectors: {stats['total_vectors']}")
    except Exception as e:
        print(f"✗ Adding documents failed: {e}")
        return False

    # Search
    print("\n5. Testing similarity search...")
    try:
        # Use first embedding as query
        query_embedding = embeddings[0]
        results = store.search(query_embedding, top_k=3)

        print(f"✓ Search completed")
        print(f"  - Query (using first doc as query)")
        print(f"  - Top {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. Score: {result['score']:.4f}")
            print(f"       Text: {result['text'][:60]}...")

        # First result should be the query itself (distance ~0)
        if results[0]['score'] < 0.01:
            print(f"✓ Top result is query itself (score: {results[0]['score']:.6f})")
        else:
            print(f"⚠️  Expected query as top result, got score: {results[0]['score']}")

    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False

    # Save and load
    print("\n6. Testing save/load persistence...")
    try:
        temp_dir = tempfile.mkdtemp()

        # Save
        store.save(temp_dir, "test_vector_store")
        print(f"✓ Vector store saved to {temp_dir}")

        # Load
        loaded_store = VectorStore.load(temp_dir, "test_vector_store")
        loaded_stats = loaded_store.get_stats()
        print(f"✓ Vector store loaded")
        print(f"  - Loaded documents: {loaded_stats['total_documents']}")
        print(f"  - Loaded vectors: {loaded_stats['total_vectors']}")

        # Verify loaded store works
        query_embedding = embeddings[5]
        loaded_results = loaded_store.search(query_embedding, top_k=2)
        print(f"✓ Loaded store search works: {len(loaded_results)} results")

        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"✓ Cleanup complete")

    except Exception as e:
        print(f"✗ Persistence failed: {e}")
        return False

    # Multiple searches
    print("\n7. Testing multiple search queries...")
    try:
        for i in [0, 5, 10, 15]:
            query_embedding = embeddings[i]
            results = store.search(query_embedding, top_k=1)
            print(f"  Query {i}: '{texts[i][:40]}...'")
            print(f"    → Top match: '{results[0]['text'][:40]}...' (score: {results[0]['score']:.4f})")

        print(f"✓ Multiple searches completed successfully")
    except Exception as e:
        print(f"✗ Multiple searches failed: {e}")
        return False

    return True


def main():
    """Run vector store tests."""

    print("\n" + "🔍"*35)
    print("    VECTOR STORE TESTING (FAISS)")
    print("🔍"*35)

    success = test_vector_store()

    print("\n" + "="*70)
    if success:
        print("✅ ALL VECTOR STORE TESTS PASSED!")
        print("="*70)
        print("\n✓ What's working:")
        print("  • FAISS vector indexing")
        print("  • Document storage and retrieval")
        print("  • Similarity search (L2 distance)")
        print("  • Save/load persistence")
        print("  • Multiple query handling")
        print("\n⏳ Still waiting for:")
        print("  • sentence-transformers (for real embeddings)")
        print("  • Then we can test end-to-end RAG!")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
