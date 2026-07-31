import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.citation import CitationAgent
from agents.logger import LoggerAgent
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

    if RetrieverAgent is None:
        print("Retrieval failed:", retrieval_import_error)
        return

    if ReasoningAgent is None:
        print("Reasoning failed:", reasoning_import_error)
        return

    retriever = RetrieverAgent()
    reasoning_agent = ReasoningAgent()
    citation_agent = CitationAgent()
    logger_agent = LoggerAgent()

    try:
        retrieved_docs = retriever.retrieve(planning_result)
    except Exception as exc:
        print(f"Retrieval failed: {exc}")
        return

    try:
        reasoning_result = reasoning_agent.generate_answer(question, retrieved_docs)
    except Exception as exc:
        print(f"Reasoning failed: {exc}")
        return

    citation_result = citation_agent.generate_citations(reasoning_result, retrieved_docs)
    logged = logger_agent.log_interaction(planning_result, retrieved_docs, reasoning_result)

    print("----------------------------------------")
    print("Question Logged Successfully")
    print("----------------------------------------")
    print(logger_agent.log_file)


if __name__ == "__main__":
    main()
