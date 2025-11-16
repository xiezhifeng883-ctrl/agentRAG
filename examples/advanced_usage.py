"""
Advanced usage examples for the RAG system.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_system import RAGSystem
from src.document_loaders import load_document
from src.text_chunker import SemanticChunker
from src.embeddings import CachedEmbeddingGenerator
from src.vector_store import HybridVectorStore
from src.rag_engine import ConversationalRAGEngine


def custom_rag_system():
    """
    Build a custom RAG system with fine-grained control.
    """
    print("Building Custom RAG System")
    print("="*50)

    # Initialize components separately
    print("\n1. Initializing embedding generator...")
    embedder = CachedEmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",
        cache_size=10000
    )

    print("2. Creating vector store...")
    vector_store = HybridVectorStore(
        embedding_dim=embedder.get_embedding_dimension()
    )

    print("3. Setting up text chunker...")
    chunker = SemanticChunker(
        chunk_size=800,
        chunk_overlap=150
    )

    print("4. Initializing RAG engine...")
    rag_engine = ConversationalRAGEngine(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        temperature=0.5,
        max_history=20
    )

    print("\nCustom RAG system built successfully!")
    return embedder, vector_store, chunker, rag_engine


def batch_document_processing():
    """
    Process multiple documents in batch.
    """
    print("\nBatch Document Processing")
    print("="*50)

    rag = RAGSystem(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Process multiple documents at once
    documents = [
        "docs/research_paper_1.pdf",
        "docs/report_2023.docx",
        "docs/presentation.pptx",
        "docs/data_analysis.xlsx",
        "docs/notes.txt",
    ]

    # Note: Replace with actual file paths
    # results = rag.add_documents(documents, show_progress=True)

    # Check results
    # for result in results:
    #     if 'error' in result:
    #         print(f"Error: {result['file_path']} - {result['error']}")
    #     else:
    #         print(f"Success: {result['file_path']} - {result['num_chunks']} chunks")


def save_and_load_example():
    """
    Demonstrate saving and loading vector stores.
    """
    print("\nSave and Load Vector Store")
    print("="*50)

    # Create and populate RAG system
    rag = RAGSystem(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Add documents
    # rag.add_document("path/to/document.pdf")

    # Save with custom name
    print("\nSaving vector store...")
    rag.save("my_knowledge_base")

    # Later, load the saved vector store
    print("\nLoading vector store...")
    rag_new = RAGSystem(api_key=os.getenv("ANTHROPIC_API_KEY"))
    rag_new.load("my_knowledge_base")

    # Query the loaded system
    # response = rag_new.query("What information is stored?")
    # print(response)


def multi_query_example():
    """
    Perform multiple queries efficiently.
    """
    print("\nMulti-Query Example")
    print("="*50)

    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        use_hybrid_search=True
    )

    # Add documents
    # rag.add_document("path/to/document.pdf")

    # Multiple related queries
    queries = [
        "What is the main objective?",
        "What methodology was used?",
        "What were the key findings?",
        "What are the limitations?",
        "What future work is suggested?",
    ]

    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {query}")
        response = rag.query(
            query,
            top_k=3,
            return_context=True
        )
        results.append({
            'query': query,
            'answer': response['response'],
            'sources': response.get('sources', [])
        })
        print(f"Answer: {response['response'][:200]}...")

    return results


def custom_system_prompt_example():
    """
    Use a custom system prompt for specialized responses.
    """
    print("\nCustom System Prompt Example")
    print("="*50)

    from src.rag_engine import RAGEngine
    from src.embeddings import EmbeddingGenerator
    from src.vector_store import VectorStore

    # Initialize components
    embedder = EmbeddingGenerator()
    vector_store = VectorStore(embedder.get_embedding_dimension())

    # Create RAG engine
    rag_engine = RAGEngine(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Custom system prompt for technical documentation
    custom_prompt = """You are a technical documentation expert assistant.

Your responsibilities:
1. Provide detailed technical explanations
2. Include code examples when relevant
3. Explain complex concepts clearly
4. Reference specific sections of the documentation
5. Highlight important warnings or notes

When answering:
- Use technical terminology appropriately
- Structure responses with clear headings
- Provide step-by-step instructions when applicable
- Include links to relevant sections"""

    # Add documents and query with custom prompt
    # (Assuming vector_store is populated)
    # query_embedding = embedder.embed_text("How do I configure the system?")
    # context_chunks = vector_store.search(query_embedding, top_k=5)
    # response = rag_engine.generate_response(
    #     "How do I configure the system?",
    #     context_chunks,
    #     system_prompt=custom_prompt
    # )


def statistics_and_monitoring():
    """
    Monitor RAG system statistics and performance.
    """
    print("\nRAG System Statistics")
    print("="*50)

    rag = RAGSystem(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Add some documents
    # rag.add_document("path/to/doc1.pdf")
    # rag.add_document("path/to/doc2.docx")

    # Get detailed statistics
    stats = rag.get_stats()

    print("\nSystem Configuration:")
    print(f"  Embedding Model: {stats['embedding_model']}")
    print(f"  Embedding Dimension: {stats['embedding_dim']}")
    print(f"  Claude Model: {stats['claude_model']}")
    print(f"  Chunker Type: {stats['chunker_type']}")
    print(f"  Chunk Size: {stats['chunk_size']}")
    print(f"  Chunk Overlap: {stats['chunk_overlap']}")
    print(f"  Hybrid Search: {stats['use_hybrid_search']}")
    print(f"  Conversational: {stats['conversational']}")

    print("\nVector Store:")
    vs_stats = stats['vector_store']
    print(f"  Total Documents: {vs_stats['total_documents']}")
    print(f"  Total Vectors: {vs_stats['total_vectors']}")
    print(f"  Index Type: {vs_stats['index_type']}")


def interactive_chat():
    """
    Interactive chat session with the RAG system.
    """
    print("\nInteractive Chat Mode")
    print("="*50)
    print("Type 'quit' to exit, 'reset' to clear history\n")

    rag = RAGSystem(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        conversational=True
    )

    # Add documents
    print("Please add documents first:")
    print("Example: rag.add_document('path/to/document.pdf')")
    # rag.add_document("path/to/document.pdf")

    while True:
        try:
            question = input("\nYou: ").strip()

            if not question:
                continue

            if question.lower() == 'quit':
                print("Goodbye!")
                break

            if question.lower() == 'reset':
                rag.rag_engine.reset_conversation()
                print("Conversation history cleared.")
                continue

            # Get response
            response = rag.query(question, top_k=5)
            print(f"\nAssistant: {response}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    print("Advanced RAG System Examples")
    print("="*70)

    # Uncomment to run different examples:

    # custom_rag_system()
    # batch_document_processing()
    # save_and_load_example()
    # multi_query_example()
    # custom_system_prompt_example()
    # statistics_and_monitoring()
    # interactive_chat()

    print("\nUncomment the examples you want to run!")
