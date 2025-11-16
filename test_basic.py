"""
Basic tests for RAG system components (no ML dependencies required).
"""

import os
import sys

def test_imports():
    """Test that core modules can be imported."""
    print("\n" + "="*60)
    print("TEST: Module Imports")
    print("="*60)

    try:
        import sys
        sys.path.insert(0, '.')
        # Import directly to avoid __init__.py dependencies
        import importlib.util

        spec = importlib.util.spec_from_file_location("document_loaders", "src/document_loaders.py")
        document_loaders = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(document_loaders)
        print("✓ document_loaders module imported")
    except Exception as e:
        print(f"✗ Failed to import document_loaders: {e}")
        return False

    try:
        spec = importlib.util.spec_from_file_location("text_chunker", "src/text_chunker.py")
        text_chunker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(text_chunker)
        print("✓ text_chunker module imported")
    except Exception as e:
        print(f"✗ Failed to import text_chunker: {e}")
        return False

    print("✓ Basic imports successful (without ML libs)")
    return True


def test_document_loading():
    """Test document loading."""
    print("\n" + "="*60)
    print("TEST: Document Loading")
    print("="*60)

    # Import directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("document_loaders", "src/document_loaders.py")
    document_loaders = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_loaders)
    load_document = document_loaders.load_document

    # Test text file
    txt_file = "test_docs/climate_report.txt"
    if os.path.exists(txt_file):
        doc = load_document(txt_file)
        print(f"✓ Loaded TXT file: {txt_file}")
        print(f"  - Length: {len(doc['text'])} characters")
        print(f"  - File type: {doc['metadata']['file_type']}")
        print(f"  - Preview: {doc['text'][:80]}...")
    else:
        print(f"✗ File not found: {txt_file}")
        return False

    # Test markdown file
    md_file = "test_docs/ml_research.md"
    if os.path.exists(md_file):
        doc = load_document(md_file)
        print(f"\n✓ Loaded Markdown file: {md_file}")
        print(f"  - Length: {len(doc['text'])} characters")
        print(f"  - File type: {doc['metadata']['file_type']}")
        print(f"  - Has headers: {'#' in doc['text']}")
    else:
        print(f"✗ File not found: {md_file}")
        return False

    return True


def test_text_chunking():
    """Test text chunking."""
    print("\n" + "="*60)
    print("TEST: Text Chunking")
    print("="*60)

    # Import directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("document_loaders", "src/document_loaders.py")
    document_loaders = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_loaders)
    load_document = document_loaders.load_document

    spec = importlib.util.spec_from_file_location("text_chunker", "src/text_chunker.py")
    text_chunker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(text_chunker)
    TextChunker = text_chunker.TextChunker
    SemanticChunker = text_chunker.SemanticChunker

    # Load a document
    md_file = "test_docs/ml_research.md"
    doc = load_document(md_file)

    # Test basic chunking
    print("\n1. Basic Chunking:")
    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_text(doc['text'], doc['metadata'])
    print(f"   ✓ Created {len(chunks)} chunks")
    print(f"   - First chunk size: {len(chunks[0]['text'])} chars")
    print(f"   - Last chunk size: {len(chunks[-1]['text'])} chars")
    print(f"   - First chunk preview:")
    print(f"     {chunks[0]['text'][:100]}...")

    # Test semantic chunking
    print("\n2. Semantic Chunking:")
    semantic_chunker = SemanticChunker(chunk_size=400, chunk_overlap=80)
    semantic_chunks = semantic_chunker.chunk_text(doc['text'], doc['metadata'])
    print(f"   ✓ Created {len(semantic_chunks)} semantic chunks")
    print(f"   - Average chunk size: {sum(len(c['text']) for c in semantic_chunks) // len(semantic_chunks)} chars")

    # Test overlap
    print("\n3. Chunk Overlap Test:")
    if len(chunks) >= 2:
        chunk1_end = chunks[0]['text'][-30:]
        chunk2_start = chunks[1]['text'][:30]
        print(f"   - End of chunk 1: ...{chunk1_end}")
        print(f"   - Start of chunk 2: {chunk2_start}...")

    return True


def test_project_structure():
    """Test project structure."""
    print("\n" + "="*60)
    print("TEST: Project Structure")
    print("="*60)

    files_to_check = [
        ("README.md", "README"),
        ("requirements.txt", "Requirements"),
        ("cli.py", "CLI"),
        ("src/__init__.py", "Package init"),
        ("src/rag_system.py", "RAG system"),
        ("examples/basic_usage.py", "Basic example"),
    ]

    all_found = True
    for filepath, description in files_to_check:
        if os.path.exists(filepath):
            print(f"✓ {description}: {filepath}")
        else:
            print(f"✗ Missing {description}: {filepath}")
            all_found = False

    return all_found


def main():
    """Run basic tests."""
    print("\n" + "="*70)
    print("AGENTRAG BASIC TESTING (No ML Dependencies)")
    print("="*70)

    results = {}

    results['Module Imports'] = test_imports()
    if results['Module Imports']:
        results['Document Loading'] = test_document_loading()
        results['Text Chunking'] = test_text_chunking()
    results['Project Structure'] = test_project_structure()

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
        print("\n🎉 All basic tests passed!")
        print("\nCore functionality (document loading, chunking) is working.")
        print("Run test_system.py after ML dependencies install to test embeddings.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
