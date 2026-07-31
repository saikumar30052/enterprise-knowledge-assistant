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
        print("Retrieved Chunks")
        print("----------------------------------------")
        print(f"Retrieval failed: {retrieval_import_error}")
        return

    if ReasoningAgent is None:
        print("----------------------------------------")
        print("Retrieved Chunks")
        print("----------------------------------------")
        print(f"Reasoning failed: {reasoning_import_error}")
        return

    retriever = RetrieverAgent()

    try:
        reasoning_agent = ReasoningAgent()
    except Exception as exc:
        print("----------------------------------------")
        print("Generated Answer")
        print("----------------------------------------")
        print(f"Reasoning failed: {exc}")
        return

    try:
        retrieved_docs = retriever.retrieve(planning_result)
    except Exception as exc:
        print("----------------------------------------")
        print("Retrieved Chunks")
        print("----------------------------------------")
        print(f"Retrieval failed: {exc}")
        return

    print("----------------------------------------")
    print("Retrieved Chunks")
    print("----------------------------------------")
    print(len(retrieved_docs))
    print()

    result = reasoning_agent.generate_answer(question, retrieved_docs)

    print("----------------------------------------")
    print("Generated Answer")
    print("----------------------------------------")
    print(result["answer"])


if __name__ == "__main__":
    main()
