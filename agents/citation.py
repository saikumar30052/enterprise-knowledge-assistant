import logging
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class CitationAgent:
    """Attach structured citations to an answer generated from retrieved documents."""

    def __init__(self) -> None:
        pass

    def generate_citations(self, answer: Dict[str, Any], retrieved_docs: List[Any]) -> Dict[str, Any]:
        if not isinstance(answer, dict):
            raise TypeError("answer must be a dictionary.")

        if not isinstance(retrieved_docs, list):
            raise TypeError("retrieved_docs must be a list of documents.")

        if "question" not in answer or "answer" not in answer:
            raise ValueError("answer must contain 'question' and 'answer' fields.")

        answer_text = str(answer.get("answer", "")).strip().lower()
        if answer_text.startswith("i could not find") or answer_text.startswith("no relevant information"):
            return {
                "question": answer["question"],
                "answer": answer["answer"],
                "citations": [],
            }

        seen: set[tuple[str, Any, str]] = set()
        citations = []

        for document in retrieved_docs:
            metadata = getattr(document, "metadata", {}) or {}
            source = metadata.get("source") or "Unknown"
            page = metadata.get("page")
            chunk_id = metadata.get("chunk_id") or "Unknown"

            if page is None:
                page_value = "N/A"
            else:
                page_value = page

            citation_key = (str(source), page_value, str(chunk_id))
            if citation_key in seen:
                continue

            seen.add(citation_key)
            citations.append(
                {
                    "source": str(source),
                    "page": page_value,
                    "chunk_id": str(chunk_id),
                }
            )

        logger.info("Generated %s citations from %s retrieved documents", len(citations), len(retrieved_docs))

        return {
            "question": answer["question"],
            "answer": answer["answer"],
            "citations": citations,
        }
