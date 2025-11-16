"""
Setup script for agentRAG package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentRAG",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A RAG system with Claude Agent SDK for multi-format document processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentRAG",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.39.0",
        "python-dotenv>=1.0.0",
        "PyPDF2>=3.0.0",
        "python-docx>=1.1.0",
        "python-pptx>=0.6.23",
        "openpyxl>=3.1.0",
        "markdown>=3.5.0",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.0",
        "sentence-transformers>=2.2.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.1",
        "tiktoken>=0.5.0",
        "tqdm>=4.66.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)
