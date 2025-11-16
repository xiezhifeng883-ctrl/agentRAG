#!/usr/bin/env python3
"""
Command-line interface for the RAG system.
"""

import os
import sys
import argparse
from pathlib import Path

from src.rag_system import RAGSystem


def add_documents_command(args):
    """Add documents to the RAG system."""
    print("Initializing RAG system...")
    rag = RAGSystem(
        api_key=args.api_key,
        embedding_model=args.embedding_model,
        claude_model=args.claude_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        use_semantic_chunking=args.semantic,
        use_hybrid_search=args.hybrid,
        vector_store_path=args.vector_store_path
    )

    # Load existing vector store if it exists
    if args.load:
        try:
            rag.load(args.store_name)
            print(f"Loaded existing vector store: {args.store_name}")
        except Exception as e:
            print(f"Could not load vector store: {e}")
            print("Creating new vector store...")

    # Add documents
    if args.files:
        results = rag.add_documents(args.files, show_progress=True)

        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        successful = sum(1 for r in results if 'error' not in r)
        print(f"Successfully processed: {successful}/{len(results)}")

        if successful > 0:
            # Save vector store
            rag.save(args.store_name)
            print(f"\nVector store saved as: {args.store_name}")

            # Show statistics
            stats = rag.get_stats()
            print(f"\nTotal documents in store: {stats['vector_store']['total_documents']}")
    else:
        print("No files specified. Use --files to add documents.")


def query_command(args):
    """Query the RAG system."""
    print("Initializing RAG system...")
    rag = RAGSystem(
        api_key=args.api_key,
        claude_model=args.claude_model,
        use_hybrid_search=args.hybrid,
        conversational=args.conversational,
        vector_store_path=args.vector_store_path
    )

    # Load vector store
    try:
        rag.load(args.store_name)
        print(f"Loaded vector store: {args.store_name}\n")
    except Exception as e:
        print(f"Error loading vector store: {e}")
        print("Please add documents first using the 'add' command.")
        return

    if args.interactive:
        # Interactive mode
        print("="*50)
        print("Interactive Query Mode")
        print("="*50)
        print("Type 'quit' to exit, 'reset' to clear conversation history\n")

        while True:
            try:
                question = input("You: ").strip()

                if not question:
                    continue

                if question.lower() == 'quit':
                    print("Goodbye!")
                    break

                if question.lower() == 'reset' and args.conversational:
                    rag.rag_engine.reset_conversation()
                    print("Conversation history cleared.\n")
                    continue

                # Get response
                if args.stream:
                    print("Assistant: ", end="", flush=True)
                    for chunk in rag.query_stream(question, top_k=args.top_k):
                        print(chunk, end="", flush=True)
                    print("\n")
                else:
                    response = rag.query(
                        question,
                        top_k=args.top_k,
                        return_context=args.verbose
                    )

                    if args.verbose:
                        print(f"Assistant: {response['response']}\n")
                        print("Sources:")
                        for i, source in enumerate(response.get('sources', []), 1):
                            print(f"  {i}. {source['source']}")
                        print(f"\nTokens: {response['usage']['input_tokens']} in, "
                              f"{response['usage']['output_tokens']} out\n")
                    else:
                        print(f"Assistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")

    elif args.question:
        # Single question mode
        if args.stream:
            print("Answer: ", end="", flush=True)
            for chunk in rag.query_stream(args.question, top_k=args.top_k):
                print(chunk, end="", flush=True)
            print()
        else:
            response = rag.query(
                args.question,
                top_k=args.top_k,
                return_context=args.verbose
            )

            if args.verbose:
                print(f"Question: {args.question}\n")
                print(f"Answer: {response['response']}\n")
                print("Sources:")
                for i, source in enumerate(response.get('sources', []), 1):
                    print(f"  {i}. {source['source']}")
                print(f"\nTokens: {response['usage']['input_tokens']} in, "
                      f"{response['usage']['output_tokens']} out")
            else:
                print(response)
    else:
        print("Please provide a question with --question or use --interactive mode")


def stats_command(args):
    """Show statistics about the RAG system."""
    rag = RAGSystem(
        api_key=args.api_key or "dummy",  # API key not needed for stats
        vector_store_path=args.vector_store_path
    )

    try:
        rag.load(args.store_name)
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return

    stats = rag.get_stats()

    print("="*50)
    print("RAG SYSTEM STATISTICS")
    print("="*50)

    print("\nConfiguration:")
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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG System CLI - Document Q&A with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add documents to the RAG system
  python cli.py add --files doc1.pdf doc2.docx --store-name my_docs

  # Query the system
  python cli.py query --question "What is the main topic?" --store-name my_docs

  # Interactive mode
  python cli.py query --interactive --store-name my_docs

  # Show statistics
  python cli.py stats --store-name my_docs
        """
    )

    # Global arguments
    parser.add_argument(
        '--api-key',
        default=os.getenv('ANTHROPIC_API_KEY'),
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--vector-store-path',
        default='./data/vector_stores',
        help='Path to vector store directory'
    )
    parser.add_argument(
        '--store-name',
        default='vector_store',
        help='Name of the vector store'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add documents to the RAG system')
    add_parser.add_argument(
        '--files',
        nargs='+',
        help='Files to add'
    )
    add_parser.add_argument(
        '--embedding-model',
        default='all-MiniLM-L6-v2',
        help='Embedding model to use'
    )
    add_parser.add_argument(
        '--claude-model',
        default='claude-3-5-sonnet-20241022',
        help='Claude model to use'
    )
    add_parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Chunk size for text splitting'
    )
    add_parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Overlap between chunks'
    )
    add_parser.add_argument(
        '--semantic',
        action='store_true',
        help='Use semantic chunking'
    )
    add_parser.add_argument(
        '--hybrid',
        action='store_true',
        help='Use hybrid search (semantic + keyword)'
    )
    add_parser.add_argument(
        '--load',
        action='store_true',
        help='Load existing vector store before adding'
    )

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument(
        '--question',
        help='Question to ask'
    )
    query_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive query mode'
    )
    query_parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of relevant chunks to retrieve'
    )
    query_parser.add_argument(
        '--claude-model',
        default='claude-3-5-sonnet-20241022',
        help='Claude model to use'
    )
    query_parser.add_argument(
        '--conversational',
        action='store_true',
        help='Enable conversation history'
    )
    query_parser.add_argument(
        '--hybrid',
        action='store_true',
        help='Use hybrid search'
    )
    query_parser.add_argument(
        '--stream',
        action='store_true',
        help='Stream the response'
    )
    query_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show RAG system statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'add':
        add_documents_command(args)
    elif args.command == 'query':
        query_command(args)
    elif args.command == 'stats':
        stats_command(args)


if __name__ == '__main__':
    main()
