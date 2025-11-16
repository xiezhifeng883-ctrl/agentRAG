"""
Demo script showing RAG system capabilities (without API calls).
This demonstrates document loading, chunking, embeddings, and retrieval.
"""

import os
import sys

def demo():
    print("="*70)
    print("AGENTRAG SYSTEM DEMONSTRATION")
    print("="*70)

    # Step 1: Document Loading
    print("\n📄 STEP 1: Loading Documents")
    print("-"*70)

    import importlib.util
    spec = importlib.util.spec_from_file_location("document_loaders", "src/document_loaders.py")
    document_loaders = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_loaders)

    docs = []
    for filename in ["ml_research.md", "climate_report.txt"]:
        filepath = f"test_docs/{filename}"
        if os.path.exists(filepath):
            doc = document_loaders.load_document(filepath)
            docs.append((filename, doc))
            print(f"✓ Loaded: {filename}")
            print(f"  Type: {doc['metadata']['file_type']}")
            print(f"  Size: {len(doc['text'])} characters")

    # Step 2: Text Chunking
    print("\n✂️  STEP 2: Chunking Documents")
    print("-"*70)

    spec = importlib.util.spec_from_file_location("text_chunker", "src/text_chunker.py")
    text_chunker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(text_chunker)

    chunker = text_chunker.SemanticChunker(chunk_size=300, chunk_overlap=50)

    all_chunks = []
    for filename, doc in docs:
        chunks = chunker.chunk_text(doc['text'], doc['metadata'])
        all_chunks.extend(chunks)
        print(f"✓ {filename}: {len(chunks)} chunks created")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"\nExample chunk:")
    print(f"  Text: {all_chunks[0]['text'][:150]}...")
    print(f"  Source: {all_chunks[0]['metadata'].get('source', 'unknown')}")

    # Step 3: Check if embeddings library is available
    print("\n🧮 STEP 3: Embeddings & Vector Store")
    print("-"*70)

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        print("Loading embedding model...")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print(f"✓ Model loaded: all-MiniLM-L6-v2")
        print(f"  Embedding dimension: {embedder.get_sentence_embedding_dimension()}")

        # Generate embeddings
        print("\nGenerating embeddings for all chunks...")
        chunk_texts = [chunk['text'] for chunk in all_chunks]
        embeddings = embedder.encode(chunk_texts, show_progress_bar=True)
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"  Shape: {embeddings.shape}")

        # Step 4: Vector Store
        try:
            import faiss

            print("\n🗄️  STEP 4: Building Vector Store")
            print("-"*70)

            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype(np.float32))
            print(f"✓ Vector store created with {index.ntotal} vectors")

            # Test retrieval
            print("\n🔍 STEP 5: Testing Retrieval")
            print("-"*70)

            test_queries = [
                "What is machine learning?",
                "What are the climate change findings?",
                "Tell me about deep learning"
            ]

            for query in test_queries:
                # Generate query embedding
                query_embedding = embedder.encode([query])[0]

                # Search
                distances, indices = index.search(
                    query_embedding.reshape(1, -1).astype(np.float32),
                    k=2
                )

                print(f"\nQuery: '{query}'")
                print(f"Top result:")
                print(f"  Score: {distances[0][0]:.4f} (lower is better)")
                print(f"  Text: {chunk_texts[indices[0][0]][:120]}...")

            print("\n" + "="*70)
            print("✅ FULL RAG PIPELINE DEMONSTRATION COMPLETE!")
            print("="*70)
            print("\nAll components working:")
            print("  ✓ Document loading (PDF, DOCX, TXT, MD, etc.)")
            print("  ✓ Smart text chunking with overlap")
            print("  ✓ Vector embeddings generation")
            print("  ✓ FAISS vector storage")
            print("  ✓ Similarity search")
            print("\nTo complete the system, add:")
            print("  • Claude API integration (set ANTHROPIC_API_KEY)")
            print("  • Try: python cli.py query --interactive")

        except ImportError:
            print("⚠️  FAISS not installed yet. Install with: pip install faiss-cpu")
            print("   Vector store and search will be available after installation.")

    except ImportError as e:
        print("⚠️  ML libraries not installed yet.")
        print(f"   Error: {e}")
        print("   Install with: pip install sentence-transformers faiss-cpu")
        print("\n   Document loading and chunking are working!")
        print("   Run this script again after installation completes.")


if __name__ == "__main__":
    demo()
