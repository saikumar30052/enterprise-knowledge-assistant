import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.documents import Document

from agents.citation import CitationAgent
from agents.planner import PlannerAgent

try:
    from agents.retriever import RetrieverAgent
except ModuleNotFoundError as exc:
    RetrieverAgent = None
    retrieval_import_error = exc
else:
    retrieval_import_error = None

try:
    from agents.reasoning import ReasoningAgent
except ModuleNotFoundError as exc:
    ReasoningAgent = None
    reasoning_import_error = exc
else:
    reasoning_import_error = None


def main() -> None:
    planner = PlannerAgent()
    question = "Explain Marketing Mart"
    planning_result = planner.plan(question)

    print("----------------------------------------")
    print("Question")
    print("----------------------------------------")
    print(question)
    print()

    if RetrieverAgent is None:
        print("----------------------------------------")
        print("Answer")
        print("----------------------------------------")
        print(f"Retrieval failed: {retrieval_import_error}")
        return

    if ReasoningAgent is None:
        print("----------------------------------------")
        print("Answer")
        print("----------------------------------------")
        print(f"Reasoning failed: {reasoning_import_error}")
        return

    retriever = RetrieverAgent()
    reasoning_agent = ReasoningAgent()
    citation_agent = CitationAgent()

    try:
        retrieved_docs = retriever.retrieve(planning_result)
    except Exception as exc:
        print("----------------------------------------")
        print("Answer")
        print("----------------------------------------")
        print(f"Retrieval failed: {exc}")
        return

    try:
        reasoning_result = reasoning_agent.generate_answer(question, retrieved_docs)
    except Exception as exc:
        print("----------------------------------------")
        print("Answer")
        print("----------------------------------------")
        print(f"Reasoning failed: {exc}")
        return

    citation_result = citation_agent.generate_citations(reasoning_result, retrieved_docs)

    print("----------------------------------------")
    print("Answer")
    print("----------------------------------------")
    print(citation_result["answer"])
    print()

    print("----------------------------------------")
    print("Sources")
    print("----------------------------------------")
    for citation in citation_result.get("citations", []):
        print("Source:")
        print(citation.get("source", "Unknown"))
        print("Page:")
        print(citation.get("page", "N/A"))
        print("Chunk ID:")
        print(citation.get("chunk_id", "Unknown"))
        print()


def test_kubernetes_question_returns_no_citations():
    citation_agent = CitationAgent()
    answer = {
        "question": "What is Kubernetes?",
        "answer": "I could not find the answer in the available enterprise documents.",
    }
    retrieved_docs = [Document(page_content="placeholder", metadata={"source": "MAPPING-DOCUMENT.xlsx"})]

    citation_result = citation_agent.generate_citations(answer, retrieved_docs)

    assert citation_result["citations"] == []


if __name__ == "__main__":
    main()
