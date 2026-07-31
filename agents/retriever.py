import json
import re
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

try:
    from langchain_chroma import Chroma
except ImportError:  # pragma: no cover - handled at runtime
    Chroma = Any  # type: ignore[misc, assignment]

from langchain_core.documents import Document

from ingestion.embedding import EmbeddingModel


class RetrieverAgent:
    """Retrieve grounded documents from one document-type scope at a time."""

    _scope_by_type = {
        "PDF": {"pdf"},
        "DOCX": {"docx"},
        "PPT": {"pptx"},
        "MAPPING": {"xlsx"},
        "GENERAL": set(),
        "PRESENTATION": {"pptx"},
        "DOCUMENT": {"docx"},
        "CONCEPT": {"pdf"},
    }

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        self.persist_directory = project_root / "database" / "chroma_db"
        self.collection_name = "enterprise_knowledge_base"
        self.top_k = 20
        self.embedding_model = EmbeddingModel()
        self.vector_store = self._initialize_vector_store()
        self.last_diagnostics: Dict[str, Any] = {}

    def retrieve(self, plan: Dict[str, Any]) -> List[Document]:
        if not isinstance(plan, dict):
            raise TypeError("Plan must be a dictionary.")
        query = plan.get("optimized_query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Plan must contain a non-empty 'optimized_query'.")

        started_at = perf_counter()
        search_type = str(plan.get("search_type", "GENERAL")).strip().upper()
        scope = self._scope_for_search_type(search_type)
        metadata_filters = self._build_metadata_filters(query, plan)
        detected_table = plan.get("detected_table") or self._detect_table(query)
        detected_column = plan.get("detected_column") or self._detect_column(query)

        if self._is_collection_empty():
            candidates: list[tuple[Document, float]] = []
        elif search_type == "MAPPING":
            metadata_documents = self._search_metadata_documents(metadata_filters)
            candidates = [(document, 1.0) for document in metadata_documents[:20]]
            if not candidates:
                candidates = self._similarity_search_top20(query, scope)
        else:
            candidates = self._similarity_search_top20(query, scope)

        candidates = [
            (document, score)
            for document, score in candidates
            if self._is_candidate_relevant(query, document, search_type, score)
        ]
        documents = self._rerank_documents(query, candidates, search_type)[:5]
        elapsed = round(perf_counter() - started_at, 3)
        sources = [str((document.metadata or {}).get("source", "Unknown")) for document in documents]
        document_types = [
            str((document.metadata or {}).get("document_type", "unknown")) for document in documents
        ]
        self.last_diagnostics = {
            "question": plan.get("original_question", query),
            "question_type": search_type,
            "detected_table": detected_table,
            "detected_column": detected_column,
            "search_scope": sorted(scope) if scope else ["all"],
            "metadata_filter": metadata_filters,
            "retrieved_sources": sources,
            "document_types": document_types,
            "similarity_scores": [round(float(score), 5) for _, score in candidates[:20]],
            "final_documents": [self._extract_document_id(document) for document in documents],
            "execution_time": elapsed,
            "query_time": elapsed,
            "returned_documents": len(documents),
            "exception": None,
        }
        self._write_query_log(self.last_diagnostics)
        return documents

    def _scope_for_search_type(self, search_type: str) -> set[str]:
        return set(self._scope_by_type.get(str(search_type).upper(), set()))

    def _similarity_search_top20(
        self, query: str, scope: set[str] | None = None
    ) -> list[tuple[Document, float]]:
        search_kwargs: Dict[str, Any] = {"query": query, "k": 20}
        if scope and len(scope) == 1:
            search_kwargs["filter"] = {"document_type": next(iter(scope))}
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(**search_kwargs)
            return [(document, float(score)) for document, score in results]
        except (AttributeError, TypeError, ValueError):
            documents = self.vector_store.similarity_search(**search_kwargs)
            return [(document, 0.0) for document in documents]

    def _rerank_documents(
        self, query: str, results: list[tuple[Document, float]], search_type: str
    ) -> list[Document]:
        query_tokens = self._content_tokens(query)
        metadata_candidates = {
            self._normalize_metadata_candidate(candidate)
            for candidate in self._extract_metadata_candidates(query)
        }
        scope = self._scope_for_search_type(search_type)
        ranked: list[tuple[int, int, int, float, Document]] = []
        for document, relevance in results:
            metadata = getattr(document, "metadata", {}) or {}
            metadata_values = {
                self._normalize_metadata_candidate(value)
                for value in metadata.values()
                if value is not None
            }
            exact_metadata = sum(candidate in metadata_values for candidate in metadata_candidates)
            keyword_overlap = len(query_tokens & self._content_tokens(document.page_content or ""))
            same_type = int(not scope or str(metadata.get("document_type", "")).lower() in scope)
            ranked.append((exact_metadata, keyword_overlap, same_type, float(relevance), document))
        ranked.sort(key=lambda item: item[:4], reverse=True)
        return [document for *_, document in ranked]

    def _search_metadata_documents(self, metadata_filters: list[dict[str, Any]]) -> list[Document]:
        documents: list[Document] = []
        seen_ids: set[str] = set()
        for metadata_filter in metadata_filters:
            for metadata, content, identifier in self._collection_get(metadata_filter):
                document = Document(page_content=content, metadata=metadata)
                document_id = str(identifier or self._extract_document_id(document))
                if document_id in seen_ids:
                    continue
                seen_ids.add(document_id)
                documents.append(document)
        return documents

    def _collection_get(self, metadata_filter: dict[str, Any]) -> list[tuple[dict, str, str]]:
        if metadata_filter.get("kind") == "and":
            where = {"$and": [{clause["field"]: clause["value"]} for clause in metadata_filter["clauses"]]}
        else:
            where = {metadata_filter["field"]: metadata_filter["value"]}
        try:
            result = self.vector_store.get(where=where, include=["metadatas", "documents"])
        except (AttributeError, TypeError, ValueError):
            collection = getattr(self.vector_store, "_collection", None)
            if collection is None:
                return []
            result = collection.get(where=where, include=["metadatas", "documents"])
        metadatas = result.get("metadatas") or []
        contents = result.get("documents") or []
        identifiers = result.get("ids") or []
        return [
            (metadatas[index] or {}, contents[index] or "", identifiers[index] if index < len(identifiers) else "")
            for index in range(len(contents))
        ]

    def _build_metadata_filters(
        self, query: str, plan: Dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        plan = plan or {}
        table = self._normalize_metadata_candidate(plan.get("detected_table") or self._detect_table(query))
        column = self._normalize_metadata_candidate(plan.get("detected_column") or self._detect_column(query))
        if table and column:
            return [{"kind": "and", "clauses": [{"field": "table", "value": table}, {"field": "target_column", "value": column}]}]
        if table:
            return [{"kind": "field", "field": "table", "value": table}]
        if column:
            return [{"kind": "field", "field": "target_column", "value": column}]
        return []

    def _is_candidate_relevant(
        self, query: str, document: Document, search_type: str, score: float
    ) -> bool:
        if search_type != "GENERAL":
            return True
        query_tokens = self._content_tokens(query)
        document_tokens = self._content_tokens(document.page_content or "")
        # General semantic similarity alone is too permissive for unknown questions.
        # Require at least one meaningful query term in the retrieved content.
        return bool(query_tokens & document_tokens)

    def _extract_metadata_candidates(self, query: str) -> list[str]:
        return re.findall(r"[A-Za-z][A-Za-z0-9_]*", query)

    def _detect_table(self, query: str) -> str:
        for candidate in self._extract_metadata_candidates(query):
            normalized = self._normalize_metadata_candidate(candidate)
            if self._looks_like_table_name(normalized):
                return normalized
        return ""

    def _detect_column(self, query: str) -> str:
        for candidate in self._extract_metadata_candidates(query):
            normalized = self._normalize_metadata_candidate(candidate)
            if self._looks_like_column_name(normalized):
                return normalized
        return ""

    def _looks_like_table_name(self, value: str) -> bool:
        return any(marker in value for marker in ("_fct", "_fact", "_dim", "_tbl"))

    def _looks_like_column_name(self, value: str) -> bool:
        return value.endswith("_id") or value in {"snapshot_id", "account_id"}

    def _content_tokens(self, value: str) -> set[str]:
        stop_words = {"what", "is", "the", "for", "in", "of", "to", "a", "an", "and", "are", "on", "about"}
        return {token for token in re.findall(r"[a-z0-9_]+", value.lower()) if token not in stop_words}

    def _normalize_metadata_candidate(self, value: Any) -> str:
        return re.sub(r"[^a-z0-9_]+", "", str(value).strip().lower())

    def _is_collection_empty(self) -> bool:
        try:
            result = self.vector_store.get(limit=1)
            return not bool(result.get("ids"))
        except (AttributeError, TypeError, ValueError):
            return False

    def _extract_document_id(self, document: Document) -> str:
        metadata = getattr(document, "metadata", {}) or {}
        return str(metadata.get("chunk_id") or metadata.get("row_number") or metadata.get("source") or "Unknown")

    def _write_query_log(self, diagnostics: Dict[str, Any]) -> None:
        log_path = Path(__file__).resolve().parent.parent / "logs" / "query_logs.jsonl"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(diagnostics, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _initialize_vector_store(self) -> Chroma:
        if Chroma is Any:  # type: ignore[comparison-overlap]
            raise ImportError("The 'langchain-chroma' package is required to initialize the retriever.")
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=str(self.persist_directory),
            embedding_function=self.embedding_model.get_embeddings(),
        )
