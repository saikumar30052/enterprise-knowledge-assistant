import sys
import traceback
from collections import Counter
from pathlib import Path
import time

from langchain_chroma import Chroma

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.chunker import DocumentChunker
from ingestion.embedding import EmbeddingModel
from ingestion.loader import DocumentLoader


class VectorIndexer:
	"""Build and persist the enterprise knowledge base vector index."""

	_embedding_batch_size = 32

	def __init__(self) -> None:
		project_root = Path(__file__).resolve().parents[1]
		self.documents_path = project_root / "documents"
		self.persist_directory = project_root / "database" / "chroma_db"
		self.collection_name = "enterprise_knowledge_base"

	def build_index(self) -> Chroma:
		"""Load, chunk, embed, and persist all enterprise documents."""
		loader = DocumentLoader(str(self.documents_path))
		documents = loader.load_documents()

		chunker = DocumentChunker()
		chunks = chunker.split_documents(documents)
		unique_chunks = []
		seen_chunk_ids = set()
		for chunk in chunks:
			chunk_id = str(chunk.metadata.get("chunk_id", ""))
			if chunk_id and chunk_id in seen_chunk_ids:
				continue
			seen_chunk_ids.add(chunk_id)
			unique_chunks.append(chunk)
		chunks = unique_chunks

		print("----------------------------------------")
		print("Chunks before indexing")
		print("----------------------------------------")
		source_counts = Counter(chunk.metadata.get("source", "Unknown") for chunk in chunks)
		for source in [
			"Bread Client KT.pptx",
			"Marketing Mart.pdf",
			"client presentation doc.docx",
			"MAPPING-DOCUMENT.xlsx",
		]:
			print(f"{source} : {source_counts.get(source, 0)}")
		print("----------------------------------------")
		print(f"Total chunks being indexed: {len(chunks)}")

		embedding_model = EmbeddingModel()
		embeddings = embedding_model.get_embeddings()

		self.persist_directory.mkdir(parents=True, exist_ok=True)
		existing_store = Chroma(
			collection_name=self.collection_name,
			persist_directory=str(self.persist_directory),
			embedding_function=embeddings,
		)
		existing_store.delete_collection()

		vector_store = Chroma(
			collection_name=self.collection_name,
			persist_directory=str(self.persist_directory),
			embedding_function=embeddings,
		)
		try:
			print("Starting Chroma indexing...")
			for start in range(0, len(chunks), self._embedding_batch_size):
				batch = chunks[start : start + self._embedding_batch_size]
				print(f"Documents being passed to Chroma: {len(batch)}")
				try:
					vector_store.add_documents(
						batch,
						ids=[str(doc.metadata["chunk_id"]) for doc in batch],
					)
				except Exception as exc:  # try per-document fallback with retries
					print(f"Batch add failed: {exc}. Falling back to per-document add with retries.")
					for doc in batch:
						for attempt in range(1, 4):
							try:
								vector_store.add_documents([doc], ids=[str(doc.metadata["chunk_id"])])
								break
							except Exception as inner_exc:
								print(f"Attempt {attempt} failed for single document: {inner_exc}")
								time.sleep(1)
						else:
							print("Failed to add document after retries; continuing with next document.")
		except Exception:
			traceback.print_exc()
			raise

		print("Chroma indexing completed successfully.")
		print("----------------------------------------")
		print(f"Documents Loaded      : {len(documents)}")
		print(f"Chunks Created        : {len(chunks)}")
		print(f"Embeddings Generated  : {len(chunks)}")
		print(f"Vectors Stored        : {len(chunks)}")
		print()
		print("Persist Directory:")
		print()
		project_root = Path(__file__).resolve().parents[1]
		persist_directory = self.persist_directory.resolve()
		print(persist_directory.relative_to(project_root).as_posix())

		return vector_store


if __name__ == "__main__":
	VectorIndexer().build_index()
