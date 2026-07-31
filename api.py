import logging
from typing import Any, Dict, List

try:
    from fastapi import FastAPI, HTTPException, status
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError("Install FastAPI and pydantic to run the API server.") from exc

from workflow.graph import run


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise Knowledge Assistant API",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    """Request payload for a user question."""

    question: str


class QueryResponse(BaseModel):
    """Response payload for a workflow execution."""

    question: str
    answer: str
    citations: List[Dict[str, Any]]


@app.get("/")
def health_check() -> Dict[str, str]:
    """Return the API health status."""
    return {
        "status": "running",
        "application": "Enterprise Knowledge Assistant",
    }


@app.post("/query", response_model=QueryResponse)
def query_answer(request: QueryRequest) -> QueryResponse:
    """Run the workflow for the provided question."""
    question = request.question.strip()
    logger.info("Incoming question: %s", question)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty.",
        )

    try:
        result = run(question)
        logger.info("Execution success for question: %s", question)
        return QueryResponse(
            question=result.get("question", question),
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
        )
    except ValueError as exc:
        logger.exception("Execution failure for question: %s", question)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.exception("Execution failure for question: %s", question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Execution failure for question: %s", question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error.",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )