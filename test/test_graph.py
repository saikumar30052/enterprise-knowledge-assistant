import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from workflow.graph import build_graph
except ModuleNotFoundError as exc:
    build_graph = None
    graph_import_error = exc
else:
    graph_import_error = None


def main() -> None:
    question = "Explain Marketing Mart"

    if build_graph is None:
        print("----------------------------------------")
        print("Question")
        print("----------------------------------------")
        print(question)
        print()
        print("----------------------------------------")
        print("Answer")
        print("----------------------------------------")
        print(f"Workflow failed: {graph_import_error}")
        return

    graph = build_graph()
    result = graph.invoke({"question": question})
    final_response = result.get("final_response", {})

    print("----------------------------------------")
    print("Question")
    print("----------------------------------------")
    print(question)
    print()

    print("----------------------------------------")
    print("Answer")
    print("----------------------------------------")
    print(final_response.get("answer", ""))
    print()

    print("----------------------------------------")
    print("Sources")
    print("----------------------------------------")
    for citation in final_response.get("citations", []):
        print(f"Source: {citation.get('source', 'Unknown')}")
        print(f"Page: {citation.get('page', 'N/A')}")
        print(f"Chunk ID: {citation.get('chunk_id', 'Unknown')}")
        print()

    print("Workflow completed successfully.")


if __name__ == "__main__":
    main()
