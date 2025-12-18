"""
LLM handler module for generating context-aware answers.
Uses LangChain with OpenAI GPT models for RAG-based question answering.
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import Config


class LLMHandler:
    """Handles LLM-based answer generation"""

    def __init__(self):
        """Initialize LLM handler with OpenAI model"""
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )

        # System prompt for RAG
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Instructions:
1. Answer the question using ONLY the information from the provided context
2. If the context doesn't contain enough information to answer the question, say:
   "I don't have enough information in the provided documents to answer this question."
3. Be concise and accurate
4. Do not hallucinate or add extra information

Context from documents:
{context}
"""

    def generate_answer(self, query: str, context_chunks: List[Dict]) -> Dict:
        """
        Generate an answer based on query and retrieved context
        """
        if not context_chunks:
            return {
                "answer": "I don't have any relevant documents to answer this question.",
                "sources": [],
                "confidence": 0.0
            }

        context_text = self._format_context(context_chunks)

        messages = [
            SystemMessage(content=self.system_prompt.format(context=context_text)),
            HumanMessage(content=f"Question: {query}")
        ]

        try:
            response = self.llm.invoke(messages)
            answer = response.content

            avg_similarity = sum(
                chunk.get("similarity_score", 0.0) for chunk in context_chunks
            ) / len(context_chunks)

            return {
                "answer": answer,
                "sources": self._format_sources(context_chunks),
                "confidence": self._calculate_confidence(avg_similarity)
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

    def _format_context(self, chunks: List[Dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            source = metadata.get("filename", "Unknown")
            section = metadata.get("chunk_index", 0) + 1

            context_parts.append(
                f"[Source {i}: {source}, Section {section}]\n{chunk['text']}"
            )

        return "\n\n".join(context_parts)

    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        sources = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            text = chunk["text"]

            sources.append({
                "filename": metadata.get("filename", "Unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "text_preview": text[:200] + "..." if len(text) > 200 else text,
                "similarity_score": chunk.get("similarity_score", 0.0)
            })

        return sources

    def _calculate_confidence(self, avg_similarity: float) -> float:
        # FAISS uses L2 distance: lower is better
        if avg_similarity < 0.5:
            return 0.9
        elif avg_similarity < 1.0:
            return 0.7
        elif avg_similarity < 1.5:
            return 0.5
        else:
            return 0.3
