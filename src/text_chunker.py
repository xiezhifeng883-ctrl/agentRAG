"""
Text chunking strategies for splitting documents into manageable pieces.
"""

from typing import List, Dict, Optional
import re


class TextChunker:
    """
    Chunks text into smaller pieces with overlap for better context preservation.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n"
    ):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separator: Primary separator to use for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk
            metadata: Optional metadata to include with each chunk

        Returns:
            List of dictionaries containing 'text', 'metadata', and 'chunk_index'
        """
        if not text or not text.strip():
            return []

        chunks = []
        metadata = metadata or {}

        # Split by separator first
        splits = self._split_text(text, self.separator)

        # Combine splits into chunks
        current_chunk = []
        current_size = 0

        for split in splits:
            split_size = len(split)

            # If a single split is larger than chunk_size, split it further
            if split_size > self.chunk_size:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk,
                        len(chunks),
                        metadata
                    ))
                    current_chunk = []
                    current_size = 0

                # Split the large text by sentences
                sub_chunks = self._split_large_text(split)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(
                        [sub_chunk],
                        len(chunks),
                        metadata
                    ))

            # If adding this split would exceed chunk_size, save current chunk
            elif current_size + split_size > self.chunk_size:
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk,
                        len(chunks),
                        metadata
                    ))

                # Start new chunk with overlap from previous
                if chunks and self.chunk_overlap > 0:
                    overlap_text = self._get_overlap(chunks[-1]['text'])
                    current_chunk = [overlap_text, split]
                    current_size = len(overlap_text) + split_size
                else:
                    current_chunk = [split]
                    current_size = split_size

            # Otherwise, add to current chunk
            else:
                current_chunk.append(split)
                current_size += split_size

        # Add the last chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk,
                len(chunks),
                metadata
            ))

        return chunks

    def _split_text(self, text: str, separator: str) -> List[str]:
        """Split text by separator."""
        if separator:
            splits = text.split(separator)
        else:
            splits = [text]

        # Filter out empty strings and strip whitespace
        return [s.strip() for s in splits if s.strip()]

    def _split_large_text(self, text: str) -> List[str]:
        """Split large text by sentences or characters."""
        # Try to split by sentences first
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))

                # Add overlap
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap(' '.join(current_chunk))
                    current_chunk = [overlap_text, sentence]
                    current_size = len(overlap_text) + sentence_size
                else:
                    current_chunk = [sentence]
                    current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        # If we still have chunks larger than chunk_size, split by characters
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                final_chunks.extend(self._split_by_characters(chunk))
            else:
                final_chunks.append(chunk)

        return final_chunks

    def _split_by_characters(self, text: str) -> List[str]:
        """Split text by characters as a last resort."""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            chunks.append(chunk)
        return chunks

    def _get_overlap(self, text: str) -> str:
        """Get the overlap text from the end of a chunk."""
        if len(text) <= self.chunk_overlap:
            return text

        # Try to find a good breaking point (space, newline, etc.)
        overlap_start = len(text) - self.chunk_overlap
        overlap_text = text[overlap_start:]

        # Try to start at a word boundary
        first_space = overlap_text.find(' ')
        if first_space != -1 and first_space < self.chunk_overlap // 2:
            overlap_text = overlap_text[first_space + 1:]

        return overlap_text

    def _create_chunk(
        self,
        text_parts: List[str],
        index: int,
        metadata: Dict
    ) -> Dict:
        """Create a chunk dictionary."""
        text = self.separator.join(text_parts) if isinstance(text_parts, list) else text_parts

        return {
            'text': text,
            'metadata': {
                **metadata,
                'chunk_index': index,
                'chunk_size': len(text)
            },
            'chunk_index': index
        }


class SemanticChunker(TextChunker):
    """
    Advanced chunker that tries to keep semantic units together.
    Prioritizes keeping paragraphs, sections, and sentences intact.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """Initialize the semantic chunker."""
        super().__init__(chunk_size, chunk_overlap, separator="\n\n")

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Chunk text while preserving semantic structure.

        Args:
            text: The text to chunk
            metadata: Optional metadata to include with each chunk

        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            return []

        # First try to split by headers/sections (markdown-style)
        section_pattern = r'\n(?=#{1,6}\s)'
        sections = re.split(section_pattern, text)

        # Then split each section by paragraphs
        all_chunks = []
        for section in sections:
            if section.strip():
                chunks = super().chunk_text(section, metadata)
                all_chunks.extend(chunks)

        # Re-index chunks
        for i, chunk in enumerate(all_chunks):
            chunk['chunk_index'] = i
            chunk['metadata']['chunk_index'] = i

        return all_chunks
