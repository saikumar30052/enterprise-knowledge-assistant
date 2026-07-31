import re
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:  # pragma: no cover - fallback for minimal environments
    yaml = None


class PlannerAgent:
    """Analyze a user question and prepare a retrieval plan."""

    def __init__(self) -> None:
        self.config_path = Path(__file__).resolve().parent.parent / "config" / "retrieval_config.yaml"
        self.top_k = self._load_top_k()

    def plan(self, question: str) -> Dict[str, Any]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        normalized_question = re.sub(r"\s+", " ", question.strip())
        search_type = self._determine_search_type(normalized_question)
        detected_table, detected_column = self._extract_mapping_entities(normalized_question)

        top_k = 20

        return {
            "original_question": question,
            "optimized_query": normalized_question,
            "search_type": search_type,
            "top_k": top_k,
            "detected_table": detected_table,
            "detected_column": detected_column,
        }

    def _load_top_k(self) -> int:
        if not self.config_path.exists():
            return 5

        try:
            if yaml is not None:
                with self.config_path.open("r", encoding="utf-8") as handle:
                    config = yaml.safe_load(handle) or {}
                top_k = config.get("top_k", 5)
                return int(top_k)

            with self.config_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    stripped = line.strip()
                    if stripped.startswith("top_k:"):
                        return int(stripped.split(":", 1)[1].strip())
        except (TypeError, ValueError, OSError):
            return 5

        return 5

    def _determine_search_type(self, question: str) -> str:
        lowered_question = question.lower()

        mapping_keywords = (
            "mapping",
            "map",
            "field",
            "column",
            "table",
            "lookup",
            "datatype",
            "data type",
            "business name",
            "logical name",
            "transformation",
        )
        presentation_keywords = (
            "presentation",
            "slide",
            "deck",
            "ppt",
            ".pptx",
            "summarize client presentation",
            "bread client",
        )
        document_keywords = (
            "document",
            "docx",
            "section",
            "heading",
            "paragraph",
        )
        concept_keywords = (
            "explain",
            "what is",
            "define",
            "overview",
            "describe",
            "who is",
            "how does",
            "why",
            "purpose",
            "meaning",
            "summarize",
            "who presented",
        )

        if any(keyword in lowered_question for keyword in mapping_keywords):
            return "MAPPING"
        if any(keyword in lowered_question for keyword in presentation_keywords):
            return "PPT"
        if any(keyword in lowered_question for keyword in document_keywords):
            return "DOCX"
        document_subject_keywords = (
            "marketing mart",
            "billing data mart",
            "bread financial",
        )
        if any(keyword in lowered_question for keyword in concept_keywords) and any(
            keyword in lowered_question for keyword in document_subject_keywords
        ):
            return "PDF"
        return "GENERAL"

    def _extract_mapping_entities(self, question: str) -> tuple[str, str]:
        """Extract common mapping identifiers without changing the query text."""
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_]*", question)
        normalized_tokens = [token.strip().lower() for token in tokens]
        table = next(
            (
                token
                for token in normalized_tokens
                if any(marker in token for marker in ("_fct", "_fact", "_dim", "_tbl"))
            ),
            "",
        )
        column = next(
            (
                token
                for token in normalized_tokens
                if token.endswith("_id") or token in {"snapshot_id", "account_id"}
            ),
            "",
        )
        return table, column
