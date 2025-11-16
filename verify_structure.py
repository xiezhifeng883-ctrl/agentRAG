#!/usr/bin/env python3
"""
Verify the project structure is correct.
"""

import os
from pathlib import Path


def check_file_exists(path, description):
    """Check if a file exists and print status."""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists


def main():
    """Verify project structure."""
    print("AgentRAG Project Structure Verification")
    print("=" * 60)

    all_ok = True

    # Check root files
    print("\nRoot Configuration Files:")
    all_ok &= check_file_exists("README.md", "README")
    all_ok &= check_file_exists("requirements.txt", "Requirements")
    all_ok &= check_file_exists(".gitignore", "Git ignore")
    all_ok &= check_file_exists(".env.example", "Environment example")
    all_ok &= check_file_exists("setup.py", "Setup script")
    all_ok &= check_file_exists("cli.py", "CLI interface")
    all_ok &= check_file_exists("QUICKSTART.md", "Quick start guide")

    # Check source files
    print("\nSource Code:")
    all_ok &= check_file_exists("src/__init__.py", "Package init")
    all_ok &= check_file_exists("src/document_loaders.py", "Document loaders")
    all_ok &= check_file_exists("src/text_chunker.py", "Text chunker")
    all_ok &= check_file_exists("src/embeddings.py", "Embeddings")
    all_ok &= check_file_exists("src/vector_store.py", "Vector store")
    all_ok &= check_file_exists("src/rag_engine.py", "RAG engine")
    all_ok &= check_file_exists("src/rag_system.py", "RAG system")

    # Check examples
    print("\nExamples:")
    all_ok &= check_file_exists("examples/basic_usage.py", "Basic usage")
    all_ok &= check_file_exists("examples/advanced_usage.py", "Advanced usage")

    # Check tests
    print("\nTests:")
    all_ok &= check_file_exists("tests/test_rag_system.py", "System tests")

    # Check directories
    print("\nDirectories:")
    all_ok &= check_file_exists("data/uploads", "Uploads directory")
    all_ok &= check_file_exists("data/vector_stores", "Vector stores directory")

    # Count lines of code
    print("\nCode Statistics:")
    total_lines = 0
    for file in ["src/document_loaders.py", "src/text_chunker.py",
                 "src/embeddings.py", "src/vector_store.py",
                 "src/rag_engine.py", "src/rag_system.py"]:
        if os.path.exists(file):
            with open(file) as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  {file}: {lines} lines")

    print(f"\n  Total source code: {total_lines} lines")

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All files and directories are present!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up API key: export ANTHROPIC_API_KEY='your-key'")
        print("3. See QUICKSTART.md for usage examples")
    else:
        print("✗ Some files or directories are missing!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
