import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from langchain_chroma import Chroma
except ModuleNotFoundError as exc:
    Chroma = None
    chroma_import_error = exc
else:
    chroma_import_error = None

try:
    from ingestion.embedding import EmbeddingModel
except ModuleNotFoundError as exc:  # pragma: no cover - manual debugging script
    EmbeddingModel = None
    embedding_import_error = exc
else:
    embedding_import_error = None


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    persist_directory = project_root / "database" / "chroma_db"
    collection_name = "enterprise_knowledge_base"

    print("----------------------------------------")
    print("Collection Information")
    print("----------------------------------------")

    if Chroma is None:
        print(f"Unable to inspect collection: {chroma_import_error}")
        return

    if EmbeddingModel is None:
        print(f"Unable to inspect collection: {embedding_import_error}")
        return

    embeddings = EmbeddingModel().get_embeddings()
    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=str(persist_directory),
        embedding_function=embeddings,
    )

    result = vector_store.get(include=["metadatas", "documents"])
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    print(f"Total vectors stored: {len(documents)}")

    source_counts: Counter[str] = Counter()
    for metadata in metadatas:
        source = metadata.get("source") or "Unknown"
        source_counts[source] += 1

    print()
    for source, count in sorted(source_counts.items()):
        print(f"{source} : {count}")


if __name__ == "__main__":
    main()
