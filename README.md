# AgentRAG - RAG System with Claude Agent SDK

A powerful Retrieval-Augmented Generation (RAG) system built with the Claude Agent SDK that supports multiple document formats including PDF, Word, PowerPoint, Excel, and text files.

## Features

- **Multi-format Document Support**: PDF, DOCX, PPTX, XLSX, TXT, MD
- **Intelligent Text Chunking**: Smart document chunking with overlap for better context preservation
- **Vector Search**: FAISS-based vector storage for efficient similarity search
- **Claude Integration**: Built on the Anthropic Claude Agent SDK
- **Easy to Use**: Simple API for document upload and querying

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agentRAG
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Quick Start

```python
from src.rag_system import RAGSystem

# Initialize the RAG system
rag = RAGSystem(api_key="your-anthropic-api-key")

# Upload documents
rag.add_document("path/to/document.pdf")
rag.add_document("path/to/report.docx")

# Query the system
response = rag.query("What are the main findings in the documents?")
print(response)
```

## Architecture

- **Document Loaders**: Extract text from various file formats
- **Text Chunker**: Split documents into manageable chunks with overlap
- **Embedding Generator**: Create vector embeddings using sentence-transformers
- **Vector Store**: FAISS-based storage for efficient retrieval
- **RAG Engine**: Combine retrieval with Claude's generation capabilities

## Project Structure

```
agentRAG/
├── src/
│   ├── document_loaders.py    # Document parsing and loading
│   ├── text_chunker.py         # Text chunking strategies
│   ├── vector_store.py         # Vector storage and retrieval
│   ├── embeddings.py           # Embedding generation
│   ├── rag_engine.py           # Core RAG logic
│   └── rag_system.py           # Main system interface
├── examples/
│   └── basic_usage.py          # Example usage
├── tests/
│   └── test_rag_system.py      # Unit tests
├── data/
│   ├── uploads/                # Uploaded documents
│   └── vector_stores/          # Persisted vector stores
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT License
