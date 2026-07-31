import json
import logging
import sys
import traceback
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, TypedDict

try:
    from langgraph.graph import StateGraph
except ImportError:  # pragma: no cover - handled at runtime
    StateGraph = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.citation import CitationAgent
from agents.logger import LoggerAgent
from agents.planner import PlannerAgent
from agents.reasoning import ReasoningAgent
from agents.retriever import RetrieverAgent


logger = logging.getLogger(__name__)


class AssistantState(TypedDict, total=False):
    question: str
    plan: dict
    retrieved_docs: list
    answer: dict
    final_response: dict
    performance_metrics: dict


def _build_reasoning_prompt(question: str, retrieved_docs: List[Any]) -> tuple[str, str]:
    """Build the same prompt structure used by the reasoning agent for diagnostics."""
    context_parts: List[str] = []
    for index, doc in enumerate(retrieved_docs, start=1):
        source = getattr(doc, "metadata", {}).get("source", "Unknown")
        content = getattr(doc, "page_content", "") or ""
        context_parts.append(
            f"Chunk {index}\n"
            f"Source:\n{source}\n\n"
            f"Content:\n{content}"
        )

    context = "\n\n----------------------------------------\n\n".join(context_parts)
    prompt = (
        "You are an Enterprise Knowledge Assistant.\n"
        "Answer ONLY from the supplied context.\n"
        "If the answer cannot be found in the context, respond exactly: "
        '"I could not find the answer in the available enterprise documents."\n'
        "Do not invent facts.\n"
        "Do not use outside knowledge.\n"
        "Be concise but complete.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}"
    )
    return prompt, context


def _format_chunk_details(retrieved_docs: List[Any]) -> List[Dict[str, Any]]:
    """Normalize retrieved documents into a simple chunk detail structure."""
    details: List[Dict[str, Any]] = []
    for document in retrieved_docs:
        metadata = getattr(document, "metadata", {}) or {}
        details.append(
            {
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page", "N/A"),
                "chunk_id": metadata.get("chunk_id", "Unknown"),
            }
        )
    return details


def _write_performance_log(question: str, metrics: Dict[str, Any], status: str) -> None:
    """Append a structured performance record to the JSONL log file."""
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "performance_logs.jsonl"

    record = {
        "timestamp": metrics.get("timestamp", ""),
        "question": question,
        "planner_time": metrics.get("planner_time", 0.0),
        "retriever_time": metrics.get("retriever_time", 0.0),
        "reasoning_time": metrics.get("reasoning_time", 0.0),
        "citation_time": metrics.get("citation_time", 0.0),
        "logger_time": metrics.get("logger_time", 0.0),
        "chroma_time": metrics.get("chroma_time", 0.0),
        "llm_time": metrics.get("llm_time", 0.0),
        "total_time": metrics.get("total_time", 0.0),
        "retrieved_chunks": metrics.get("retrieved_chunks", 0),
        "answer_length": metrics.get("answer_length", 0),
        "status": status,
    }

    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _print_performance_summary(
    question: str,
    metrics: Dict[str, Any],
    plan: Dict[str, Any],
    retrieved_docs: List[Any],
    answer: Dict[str, Any],
) -> None:
    """Print the workflow performance breakdown and diagnostic details."""
    planner_time = float(metrics.get("planner_time", 0.0) or 0.0)
    retriever_time = float(metrics.get("retriever_time", 0.0) or 0.0)
    reasoning_time = float(metrics.get("reasoning_time", 0.0) or 0.0)
    citation_time = float(metrics.get("citation_time", 0.0) or 0.0)
    logger_time = float(metrics.get("logger_time", 0.0) or 0.0)
    total_time = planner_time + retriever_time + reasoning_time + citation_time + logger_time

    print("====================================================")
    print("WORKFLOW PERFORMANCE")
    print("====================================================")
    print()
    print(f"{'Planner':<13}: {planner_time:>7.2f} sec")
    print(f"{'Retriever':<13}: {retriever_time:>7.2f} sec")
    print(f"{'Reasoning':<13}: {reasoning_time:>7.2f} sec")
    print(f"{'Citation':<13}: {citation_time:>7.2f} sec")
    print(f"{'Logger':<13}: {logger_time:>7.2f} sec")
    print()
    print("----------------------------------------------------")
    print(f"{'TOTAL':<13}: {total_time:>7.2f} sec")
    print()
    print("====================================================")

    if plan:
        print("Planner")
        print(f"Original Question: {plan.get('original_question', question)}")
        print(f"Optimized Query: {plan.get('optimized_query', '')}")
        print(f"Search Type: {plan.get('search_type', '')}")
        print(f"Top K: {plan.get('top_k', '')}")
        print(f"Execution Time: {planner_time:.2f} sec")
        print("----------------------------------------------------")

    if retrieved_docs:
        print("Retriever")
        print("Retrieved Chunks:")
        for index, chunk in enumerate(_format_chunk_details(retrieved_docs), start=1):
            print(f"{index}.")
            print(f"Source: {chunk.get('source', 'Unknown')}")
            print(f"Page: {chunk.get('page', 'N/A')}")
            print(f"Chunk ID: {chunk.get('chunk_id', 'Unknown')}")
        print(f"Total Retrieved Chunks: {len(retrieved_docs)}")
        print(f"Retriever Execution Time: {retriever_time:.2f} sec")
        print("----------------------------------------------------")

    if answer:
        prompt, context = _build_reasoning_prompt(question, retrieved_docs)
        reasoning_model = metrics.get("reasoning_model", "Unknown")
        print("Reasoning")
        print(f"LLM Model: {reasoning_model}")
        print(f"Question: {question}")
        print(f"Number of retrieved chunks: {len(retrieved_docs)}")
        print(f"Total Context Length: {len(context)}")
        print(f"Prompt Length: {len(prompt)}")
        print(f"LLM Generation Time: {metrics.get('reasoning_time', 0.0):.2f} sec")
        print(f"Generated Answer Length: {len(answer.get('answer', ''))}")
        print("----------------------------------------------------")

    if metrics.get("citation_details"):
        print("Citation")
        print(f"Number of citations: {metrics['citation_details'].get('citation_count', 0)}")
        print(f"Citation execution time: {citation_time:.2f} sec")
        print("----------------------------------------------------")

    if metrics.get("logger_time") is not None:
        print("Logger")
        print(f"Timestamp: {metrics.get('logger_timestamp', 'N/A')}")
        print(f"Question: {question}")
        print(f"Workflow Status: {metrics.get('workflow_status', 'UNKNOWN')}")
        print(f"Execution Time: {logger_time:.2f} sec")
        print("----------------------------------------------------")

    print("==================================================")
    print("DIAGNOSTIC SUMMARY")
    print("==================================================")
    print(f"Question: {question}")
    print(f"Planner: {'PASS' if plan else 'FAIL'}")
    print(f"Retriever: {'PASS' if retrieved_docs else 'FAIL'}")
    print(f"Reasoning: {'PASS' if answer else 'FAIL'}")
    print("Citation: PASS")
    print("Logger: PASS")
    print(f"ChromaDB: {'PASS' if retrieved_docs else 'FAIL'}")
    print(f"Ollama: {'PASS' if answer and metrics.get('reasoning_time', 0) is not None else 'FAIL'}")
    print(f"Workflow: {'SUCCESS' if answer else 'FAILED'}")
    print("==================================================")


def build_graph():
    """Build and return the compiled LangGraph workflow."""
    if StateGraph is None:
        raise ImportError("The 'langgraph' package is required to build the workflow graph.")

    planner_agent = PlannerAgent()
    retriever_agent = RetrieverAgent()
    reasoning_agent = ReasoningAgent()
    citation_agent = CitationAgent()
    logger_agent = LoggerAgent()

    def planner_node(state: AssistantState) -> Dict[str, Any]:
        started_at = perf_counter()
        try:
            question = state.get("question", "")
            plan = planner_agent.plan(question)
            elapsed = round(perf_counter() - started_at, 2)
            metrics = dict(state.get("performance_metrics", {}))
            metrics["planner_time"] = elapsed
            metrics["timestamp"] = metrics.get("timestamp") or ""
            metrics["planner_details"] = {
                "original_question": plan.get("original_question", question),
                "optimized_query": plan.get("optimized_query", ""),
                "search_type": plan.get("search_type", ""),
                "top_k": plan.get("top_k", ""),
            }
            return {**state, "plan": plan, "performance_metrics": metrics}
        except Exception:
            logger.exception("Planner node failed")
            traceback.print_exc()
            raise

    def retriever_node(state: AssistantState) -> Dict[str, Any]:
        started_at = perf_counter()
        try:
            plan = state.get("plan", {})
            retrieved_docs = retriever_agent.retrieve(plan)
            elapsed = round(perf_counter() - started_at, 2)
            metrics = dict(state.get("performance_metrics", {}))
            metrics["retriever_time"] = elapsed
            metrics["chroma_time"] = elapsed
            metrics["retrieved_chunks"] = len(retrieved_docs)
            metrics["retriever_details"] = _format_chunk_details(retrieved_docs)

            question = state.get("question", "")
            print("==================================================")
            print("RETRIEVER DEBUG")
            print("==================================================")
            print(f"Question: {question}")
            print(f"Retrieved Documents: {len(retrieved_docs)}")
            print("==================================================")
            for index, document in enumerate(retrieved_docs, start=1):
                metadata = getattr(document, "metadata", {}) or {}
                print("==================================================")
                print(f"Rank: {index}")
                print(f"Source: {metadata.get('source', 'Unknown')}")
                print(f"Chunk ID: {metadata.get('chunk_id', metadata.get('row_number', 'Unknown'))}")
                print("Metadata:")
                print(metadata)
                print("Page Content:")
                print(getattr(document, "page_content", ""))
                print("==================================================")

            for token in ["SNAPSHOT_ID", "BILL_PROMO_FCT"]:
                if token in question.upper():
                    content_text = "\n".join(getattr(doc, "page_content", "") or "" for doc in retrieved_docs)
                    occurrences = content_text.count(token)
                    if occurrences:
                        print(f"Occurrences of {token}: {occurrences}")
                    else:
                        print(f"{token} was NOT retrieved.")

            return {**state, "retrieved_docs": retrieved_docs, "performance_metrics": metrics}
        except Exception:
            logger.exception("Retriever node failed")
            traceback.print_exc()
            raise

    def reasoning_node(state: AssistantState) -> Dict[str, Any]:
        started_at = perf_counter()
        try:
            question = state.get("question", "")
            retrieved_docs = state.get("retrieved_docs", [])
            answer = reasoning_agent.generate_answer(question, retrieved_docs)
            elapsed = round(perf_counter() - started_at, 2)
            metrics = dict(state.get("performance_metrics", {}))
            metrics["reasoning_time"] = elapsed
            metrics["llm_time"] = elapsed
            prompt, context = _build_reasoning_prompt(question, retrieved_docs)
            metrics["reasoning_model"] = getattr(reasoning_agent._llm, "model", "Unknown")
            metrics["reasoning_details"] = {
                "number_of_chunks": len(retrieved_docs),
                "context_length": len(context),
                "prompt_length": len(prompt),
                "generated_answer_length": len(answer.get("answer", "")),
            }
            return {**state, "answer": answer, "performance_metrics": metrics}
        except Exception:
            logger.exception("Reasoning node failed")
            traceback.print_exc()
            raise

    def citation_node(state: AssistantState) -> Dict[str, Any]:
        started_at = perf_counter()
        try:
            answer = state.get("answer", {})
            retrieved_docs = state.get("retrieved_docs", [])
            citation_result = citation_agent.generate_citations(answer, retrieved_docs)
            elapsed = round(perf_counter() - started_at, 2)
            metrics = dict(state.get("performance_metrics", {}))
            metrics["citation_time"] = elapsed
            metrics["citation_details"] = {
                "citation_count": len(citation_result.get("citations", [])),
            }
            return {**state, "final_response": citation_result, "performance_metrics": metrics}
        except Exception:
            logger.exception("Citation node failed")
            traceback.print_exc()
            raise

    def logger_node(state: AssistantState) -> Dict[str, Any]:
        started_at = perf_counter()
        try:
            plan = state.get("plan", {})
            retrieved_docs = state.get("retrieved_docs", [])
            answer = state.get("answer", {})
            logger_agent.log_interaction(plan, retrieved_docs, answer)
            elapsed = round(perf_counter() - started_at, 2)
            metrics = dict(state.get("performance_metrics", {}))
            metrics["logger_time"] = elapsed
            metrics["logger_timestamp"] = metrics.get("timestamp")
            metrics["workflow_status"] = "SUCCESS"
            return {**state, "performance_metrics": metrics}
        except Exception:
            logger.exception("Logger node failed")
            traceback.print_exc()
            raise

    workflow = StateGraph(AssistantState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("citation", citation_node)
    workflow.add_node("logger", logger_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "reasoning")
    workflow.add_edge("reasoning", "citation")
    workflow.add_edge("citation", "logger")
    workflow.add_edge("logger", "__end__")

    return workflow.compile()


def run(question: str) -> Dict[str, Any]:
    """Run the workflow for a single user question."""
    try:
        graph = build_graph()
        result = graph.invoke({"question": question})
        final_response = result.get("final_response", {})
        performance_metrics = dict(result.get("performance_metrics", {}))
        performance_metrics["timestamp"] = performance_metrics.get("timestamp") or ""
        performance_metrics["answer_length"] = len(final_response.get("answer", ""))
        performance_metrics["total_time"] = round(
            sum(
                [
                    float(performance_metrics.get("planner_time", 0.0) or 0.0),
                    float(performance_metrics.get("retriever_time", 0.0) or 0.0),
                    float(performance_metrics.get("reasoning_time", 0.0) or 0.0),
                    float(performance_metrics.get("citation_time", 0.0) or 0.0),
                    float(performance_metrics.get("logger_time", 0.0) or 0.0),
                ]
            ),
            2,
        )
        _write_performance_log(question, performance_metrics, "SUCCESS")
        _print_performance_summary(
            question=question,
            metrics=performance_metrics,
            plan=result.get("plan", {}),
            retrieved_docs=result.get("retrieved_docs", []),
            answer=result.get("answer", {}),
        )
        return {
            "question": final_response.get("question", question),
            "answer": final_response.get("answer", ""),
            "citations": final_response.get("citations", []),
        }
    except Exception:
        logger.exception("Workflow execution failed")
        traceback.print_exc()
        _write_performance_log(question, {}, "FAILED")
        raise
