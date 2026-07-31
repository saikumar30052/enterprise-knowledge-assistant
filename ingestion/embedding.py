import os
from typing import Any

from dotenv import load_dotenv

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:  # pragma: no cover - handled at runtime
    OllamaEmbeddings = None  # type: ignore[assignment]


class EmbeddingModel:
    """Provide a configured LangChain Ollama embedding model."""

    def __init__(self) -> None:
        load_dotenv()

        base_url = os.getenv("OLLAMA_BASE_URL")
        model = os.getenv("OLLAMA_EMBEDDING_MODEL")

        missing_variables = [
            name
            for name, value in (
                ("OLLAMA_BASE_URL", base_url),
                ("OLLAMA_EMBEDDING_MODEL", model),
            )
            if not value or not value.strip()
        ]
        if missing_variables:
            missing = ", ".join(missing_variables)
            raise ValueError(
                f"Missing required embedding configuration: {missing}. "
                "Set these variables in the .env file."
            )

        if OllamaEmbeddings is None:
            raise ImportError(
                "The 'langchain-ollama' package is required to use the embedding model."
            )

        self._embeddings: Any = OllamaEmbeddings(
            base_url=base_url or "",
            model=model or "",
        )

    def get_embeddings(self) -> Any:
        """Return the configured Ollama embedding object."""
        return self._embeddings
