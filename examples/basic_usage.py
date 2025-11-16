"""
Basic usage example for the RAG system.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_system import RAGSystem


def main():
    """Basic RAG system usage example."""

    # Initialize the RAG system
    print("Initializing RAG system...")
    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),  # Or provide directly
        embedding_model="all-MiniLM-L6-v2",
        claude_model="claude-3-5-sonnet-20241022",
        chunk_size=1000,
        chunk_overlap=200,
        use_semantic_chunking=True
    )

    # Add documents
    print("\nAdding documents...")
    # Replace these with actual file paths
    documents = [
        # "path/to/document1.pdf",
        # "path/to/document2.docx",
        # "path/to/document3.txt",
    ]

    if not documents:
        print("No documents specified. Please add document paths to the example.")
        print("\nExample usage:")
        print("  rag.add_document('path/to/document.pdf')")
        return

    for doc_path in documents:
        try:
            stats = rag.add_document(doc_path)
            print(f"Added {doc_path}: {stats['num_chunks']} chunks")
        except Exception as e:
            print(f"Error adding {doc_path}: {e}")

    # Save the vector store
    print("\nSaving vector store...")
    rag.save("my_documents")

    # Query the system
    print("\n" + "="*50)
    print("QUERYING THE RAG SYSTEM")
    print("="*50)

    questions = [
        "What are the main topics discussed in the documents?",
        "Can you summarize the key findings?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        print("-" * 50)

        response = rag.query(
            question,
            top_k=5,
            include_sources=True,
            return_context=True
        )

        print(f"A: {response['response']}")
        print(f"\nSources used:")
        for i, source in enumerate(response.get('sources', []), 1):
            print(f"  {i}. {source['source']}")

        print(f"\nTokens used: {response['usage']['input_tokens']} input, "
              f"{response['usage']['output_tokens']} output")

    # Get system statistics
    print("\n" + "="*50)
    print("SYSTEM STATISTICS")
    print("="*50)
    stats = rag.get_stats()
    print(f"Total documents: {stats['vector_store']['total_documents']}")
    print(f"Embedding model: {stats['embedding_model']}")
    print(f"Claude model: {stats['claude_model']}")
    print(f"Chunk size: {stats['chunk_size']}")


def streaming_example():
    """Example of streaming responses."""
    print("\nStreaming Response Example")
    print("="*50)

    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        use_semantic_chunking=True
    )

    # Add a document first (replace with actual path)
    # rag.add_document("path/to/document.pdf")

    # Stream the response
    question = "What are the main points?"
    print(f"\nQ: {question}")
    print("A: ", end="", flush=True)

    for chunk in rag.query_stream(question, top_k=5):
        print(chunk, end="", flush=True)

    print("\n")


def conversational_example():
    """Example of conversational mode."""
    print("\nConversational RAG Example")
    print("="*50)

    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        conversational=True  # Enable conversation history
    )

    # Add documents
    # rag.add_document("path/to/document.pdf")

    # Have a conversation
    questions = [
        "What is this document about?",
        "Can you elaborate on the first point?",  # Follow-up question
        "What are the implications?",  # Another follow-up
    ]

    for question in questions:
        print(f"\nQ: {question}")
        response = rag.query(question, top_k=3)
        print(f"A: {response}")


def hybrid_search_example():
    """Example of hybrid search (semantic + keyword)."""
    print("\nHybrid Search Example")
    print("="*50)

    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        use_hybrid_search=True  # Enable hybrid search
    )

    # Add documents
    # rag.add_document("path/to/document.pdf")

    # Query with hybrid search
    question = "machine learning algorithms"
    print(f"\nQ: {question}")
    response = rag.query(question, top_k=5)
    print(f"A: {response}")


if __name__ == "__main__":
    # Run the basic example
    main()

    # Uncomment to try other examples:
    # streaming_example()
    # conversational_example()
    # hybrid_search_example()
