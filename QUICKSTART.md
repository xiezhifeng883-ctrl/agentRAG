# Quick Start Guide

Get started with AgentRAG in 5 minutes!

## Installation

1. **Clone and navigate to the repository:**
   ```bash
   cd agentRAG
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

   Or export it directly:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

## Quick Usage

### Method 1: Command Line Interface (Easiest)

```bash
# Add documents
python cli.py add --files document.pdf report.docx --store-name my_docs

# Ask questions (interactive mode)
python cli.py query --interactive --store-name my_docs

# Ask a single question
python cli.py query --question "What are the key findings?" --store-name my_docs

# View statistics
python cli.py stats --store-name my_docs
```

### Method 2: Python API

```python
from src.rag_system import RAGSystem

# Initialize
rag = RAGSystem(api_key="your-api-key")

# Add documents
rag.add_document("path/to/document.pdf")
rag.add_document("path/to/report.docx")

# Save for later use
rag.save("my_knowledge_base")

# Query
answer = rag.query("What are the main topics?")
print(answer)
```

### Method 3: Advanced Usage

```python
from src.rag_system import RAGSystem

# Initialize with advanced options
rag = RAGSystem(
    api_key="your-api-key",
    embedding_model="all-MiniLM-L6-v2",
    claude_model="claude-3-5-sonnet-20241022",
    chunk_size=1000,
    chunk_overlap=200,
    use_semantic_chunking=True,  # Better structure preservation
    use_hybrid_search=True,       # Combine semantic + keyword search
    conversational=True           # Enable conversation history
)

# Add multiple documents
rag.add_documents([
    "doc1.pdf",
    "doc2.docx",
    "doc3.pptx"
])

# Get detailed response
response = rag.query(
    "What is the main conclusion?",
    top_k=5,
    return_context=True
)

print(f"Answer: {response['response']}")
print(f"Sources: {response['sources']}")
print(f"Tokens used: {response['usage']}")
```

## Supported File Formats

- **PDF** (.pdf)
- **Word** (.docx, .doc)
- **PowerPoint** (.pptx, .ppt)
- **Excel** (.xlsx, .xls)
- **Text** (.txt)
- **Markdown** (.md)

## Key Features

### 1. Semantic Chunking
Preserves document structure by keeping paragraphs and sections together:
```python
rag = RAGSystem(use_semantic_chunking=True)
```

### 2. Hybrid Search
Combines vector similarity with keyword matching for better results:
```python
rag = RAGSystem(use_hybrid_search=True)
```

### 3. Conversational Mode
Maintains conversation history for follow-up questions:
```python
rag = RAGSystem(conversational=True)

rag.query("What is the document about?")
rag.query("Can you elaborate on that?")  # Remembers context
rag.query("What are the implications?")   # Still remembers
```

### 4. Streaming Responses
Get responses as they're generated:
```python
for chunk in rag.query_stream("Your question here"):
    print(chunk, end="", flush=True)
```

### 5. Persistent Storage
Save and load your document collections:
```python
# Save
rag.save("my_collection")

# Load later
rag_new = RAGSystem()
rag_new.load("my_collection")
```

## Example Workflows

### Research Paper Analysis

```bash
# Add all papers
python cli.py add --files paper1.pdf paper2.pdf paper3.pdf \
  --store-name research_papers --semantic

# Interactive Q&A
python cli.py query --interactive --conversational \
  --store-name research_papers
```

### Document Comparison

```python
rag = RAGSystem(use_hybrid_search=True)

# Add documents to compare
rag.add_documents([
    "proposal_v1.docx",
    "proposal_v2.docx",
    "final_proposal.docx"
])

# Ask comparison questions
rag.query("What are the key differences between the versions?")
rag.query("Which version includes the budget section?")
```

### Meeting Notes Search

```python
rag = RAGSystem(conversational=True)

# Add all meeting notes
import glob
meeting_notes = glob.glob("meetings/*.txt")
rag.add_documents(meeting_notes)

# Search across all meetings
rag.query("What decisions were made about the project timeline?")
rag.query("Who was assigned to the design task?")
```

## Troubleshooting

### "No module named 'src'"
Make sure you're running from the project root directory.

### "API key required"
Set your API key:
```bash
export ANTHROPIC_API_KEY='your-key'
```

### Out of memory
Reduce chunk size or use smaller batches:
```python
rag = RAGSystem(chunk_size=500)
```

### Slow embedding generation
First run downloads the model (~90MB). Subsequent runs are faster.

## Next Steps

- See `examples/basic_usage.py` for more examples
- See `examples/advanced_usage.py` for advanced features
- Run tests: `python tests/test_rag_system.py`
- Read the full README.md for architecture details

## Getting Help

- Check the examples folder for sample code
- Read the documentation in each module's docstrings
- Run with `--verbose` flag for detailed output

Enjoy using AgentRAG! 🚀
