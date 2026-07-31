import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.planner import PlannerAgent

try:
    from agents.retriever import RetrieverAgent
except ModuleNotFoundError as exc:
    RetrieverAgent = None
    retrieval_import_error = exc
else:
    retrieval_import_error = None


def main() -> None:
    planner = PlannerAgent()
    question = "Explain Marketing Mart"
    planning_result = planner.plan(question)

    print("----------------------------------------")
    print("Question:")
    print(question)
    print("Planning Result:")
    print(planning_result)
    print("Retrieved Chunks:")

    if RetrieverAgent is None:
        print(f"Retrieval failed: {retrieval_import_error}")
        return

    retriever = RetrieverAgent()

    try:
        chunks = retriever.retrieve(planning_result)
    except Exception as exc:  # pragma: no cover - manual verification script
        print(f"Retrieval failed: {exc}")
        return

    for index, chunk in enumerate(chunks, start=1):
        print("----------------------------------------")
        print(f"Chunk Number: {index}")
        print("Source Document:")
        print(chunk.metadata.get("source", "N/A"))
        page = chunk.metadata.get("page")
        if page is not None:
            print(f"Page: {page}")
        else:
            print("Page: N/A")
        print(f"Chunk ID: {chunk.metadata.get('chunk_id', 'N/A')}")
        content = chunk.page_content or ""
        print("Content:")
        print(content[:300])

    print("----------------------------------------")


if __name__ == "__main__":
    main()
