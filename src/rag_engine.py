"""
RAG (Retrieval-Augmented Generation) engine combining retrieval with Claude.
"""

from typing import List, Dict, Optional
import anthropic
from anthropic import Anthropic


class RAGEngine:
    """
    RAG engine that retrieves relevant context and generates responses using Claude.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialize the RAG engine.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation (0-1)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(
        self,
        query: str,
        context_chunks: List[Dict],
        system_prompt: Optional[str] = None,
        include_sources: bool = True
    ) -> Dict:
        """
        Generate a response using retrieved context.

        Args:
            query: User's question/query
            context_chunks: List of retrieved document chunks
            system_prompt: Optional custom system prompt
            include_sources: Whether to include source citations

        Returns:
            Dictionary with 'response', 'sources', and 'context_used'
        """
        # Build context from retrieved chunks
        context = self._build_context(context_chunks)

        # Create system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        # Build user message with context
        user_message = self._build_user_message(query, context)

        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = message.content[0].text

            # Prepare result
            result = {
                'response': response_text,
                'context_used': context,
                'model': self.model,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
            }

            # Add source information if requested
            if include_sources:
                result['sources'] = self._extract_sources(context_chunks)

            return result

        except Exception as e:
            raise RuntimeError(f"Error generating response: {str(e)}")

    def generate_streaming_response(
        self,
        query: str,
        context_chunks: List[Dict],
        system_prompt: Optional[str] = None
    ):
        """
        Generate a streaming response using retrieved context.

        Args:
            query: User's question/query
            context_chunks: List of retrieved document chunks
            system_prompt: Optional custom system prompt

        Yields:
            Text chunks as they are generated
        """
        # Build context
        context = self._build_context(context_chunks)

        # Create system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        # Build user message
        user_message = self._build_user_message(query, context)

        # Stream response
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise RuntimeError(f"Error generating streaming response: {str(e)}")

    def _build_context(self, context_chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        if not context_chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})

            # Include source information if available
            source = metadata.get('source', 'Unknown')
            chunk_info = f"[Source {i}: {source}]"

            if metadata.get('chunk_index') is not None:
                chunk_info += f" [Chunk {metadata['chunk_index']}]"

            context_parts.append(f"{chunk_info}\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def _build_user_message(self, query: str, context: str) -> str:
        """Build the user message with query and context."""
        return f"""Context information from relevant documents:

{context}

---

Based on the context provided above, please answer the following question. If the context doesn't contain enough information to answer the question, please say so and provide the best answer you can based on what's available.

Question: {query}"""

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for RAG."""
        return """You are a helpful AI assistant that answers questions based on provided context from documents.

Your responsibilities:
1. Answer questions accurately using the provided context
2. Cite sources when referencing specific information
3. If the context doesn't contain enough information, acknowledge this
4. Don't make up information that isn't in the context
5. Be concise but thorough in your responses

When answering:
- Reference the source numbers (e.g., "According to Source 1...")
- Quote relevant passages when helpful
- Synthesize information across multiple sources when appropriate
- Indicate uncertainty when the context is ambiguous"""

    def _extract_sources(self, context_chunks: List[Dict]) -> List[Dict]:
        """Extract source information from context chunks."""
        sources = []
        seen_sources = set()

        for chunk in context_chunks:
            metadata = chunk.get('metadata', {})
            source = metadata.get('source', 'Unknown')

            if source not in seen_sources:
                sources.append({
                    'source': source,
                    'file_type': metadata.get('file_type', 'unknown'),
                    'title': metadata.get('title', ''),
                    'author': metadata.get('author', '')
                })
                seen_sources.add(source)

        return sources

    def ask_followup(
        self,
        conversation_history: List[Dict],
        new_query: str,
        context_chunks: List[Dict]
    ) -> Dict:
        """
        Handle follow-up questions with conversation history.

        Args:
            conversation_history: List of previous messages
            new_query: New question
            context_chunks: Retrieved context for new query

        Returns:
            Response dictionary
        """
        # Build context
        context = self._build_context(context_chunks)

        # Add new message to history
        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": self._build_user_message(new_query, context)
        })

        # Generate response
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._get_default_system_prompt(),
                messages=messages
            )

            response_text = message.content[0].text

            return {
                'response': response_text,
                'context_used': context,
                'sources': self._extract_sources(context_chunks),
                'model': self.model,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
            }

        except Exception as e:
            raise RuntimeError(f"Error generating follow-up response: {str(e)}")


class ConversationalRAGEngine(RAGEngine):
    """
    RAG engine with built-in conversation management.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_history: int = 10
    ):
        """
        Initialize conversational RAG engine.

        Args:
            max_history: Maximum number of conversation turns to keep
        """
        super().__init__(api_key, model, max_tokens, temperature)
        self.conversation_history = []
        self.max_history = max_history

    def chat(
        self,
        query: str,
        context_chunks: List[Dict],
        reset_history: bool = False
    ) -> Dict:
        """
        Chat with conversation history.

        Args:
            query: User's question
            context_chunks: Retrieved context
            reset_history: Whether to reset conversation history

        Returns:
            Response dictionary
        """
        if reset_history:
            self.conversation_history = []

        # Build context
        context = self._build_context(context_chunks)

        # Add user message
        user_message = self._build_user_message(query, context)
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Generate response
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._get_default_system_prompt(),
                messages=self.conversation_history
            )

            response_text = message.content[0].text

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            # Trim history if too long
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-(self.max_history * 2):]

            return {
                'response': response_text,
                'context_used': context,
                'sources': self._extract_sources(context_chunks),
                'model': self.model,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
            }

        except Exception as e:
            # Remove failed message from history
            if self.conversation_history:
                self.conversation_history.pop()
            raise RuntimeError(f"Error in chat: {str(e)}")

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
