import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.embedding import EmbeddingModel


try:
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.get_embeddings()
    embedding_vector = embeddings.embed_query("Enterprise Knowledge Assistant")

    print("Embedding Model Loaded Successfully")
    print(f"Embedding Dimension: {len(embedding_vector)}")
    print(f"First 10 values: {embedding_vector[:10]}")
except Exception as exc:
    print(f"Embedding verification failed: {exc}")
