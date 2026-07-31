import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class LoggerAgent:
    """Append interaction logs to a JSONL file."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parent.parent
        self.logs_dir = self.project_root / "logs"
        self.log_file = self.logs_dir / "query_logs.jsonl"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_interaction(self, plan: Dict[str, Any], retrieved_docs: List[Any], answer: Dict[str, Any]) -> bool:
        if not isinstance(plan, dict):
            raise TypeError("plan must be a dictionary.")
        if not isinstance(retrieved_docs, list):
            raise TypeError("retrieved_docs must be a list.")
        if not isinstance(answer, dict):
            raise TypeError("answer must be a dictionary.")

        try:
            sources = []
            for document in retrieved_docs:
                metadata = getattr(document, "metadata", {}) or {}
                source = metadata.get("source")
                if source and source not in sources:
                    sources.append(source)

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "original_question": plan.get("original_question"),
                "optimized_query": plan.get("optimized_query"),
                "search_type": plan.get("search_type"),
                "top_k": plan.get("top_k"),
                "retrieved_chunks": len(retrieved_docs),
                "unique_sources": sources,
                "generated_answer": answer.get("answer"),
            }

            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

            logger.info("Logged interaction to %s", self.log_file)
            return True
        except OSError as exc:
            logger.exception("Failed to write interaction log: %s", exc)
            return False
