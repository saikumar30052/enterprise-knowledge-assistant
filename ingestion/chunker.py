from pathlib import Path
from typing import List

import yaml
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:
	"""Split only long PDF pages while preserving structured documents."""

	def __init__(self):
		self.config = self.load_config()
		self.text_splitter = RecursiveCharacterTextSplitter(
			chunk_size=800,
			chunk_overlap=150,
		)

	def load_config(self) -> dict:
		"""Load and validate chunking settings from the retrieval config."""
		config_path = Path(__file__).resolve().parents[1] / "config" / "retrieval_config.yaml"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = yaml.safe_load(config_file) or {}

		chunk_size = 800
		chunk_overlap = 150

		if not isinstance(chunk_size, int) or chunk_size <= 0:
			raise ValueError("chunk_size must be a positive integer")
		if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
			raise ValueError("chunk_overlap must be a non-negative integer")
		if chunk_overlap >= chunk_size:
			raise ValueError("chunk_overlap must be smaller than chunk_size")

		return {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap}

	def split_documents(self, documents: List[Document]) -> List[Document]:
		"""Split long PDF pages and assign stable one-based chunk identifiers."""
		chunks: List[Document] = []
		for document in documents:
			document_type = str(document.metadata.get("document_type", "")).lower()
			if document_type == "pdf" and len(document.page_content or "") > self.config["chunk_size"]:
				chunks.extend(self.text_splitter.split_documents([document]))
			else:
				chunks.append(document)

		chunk_numbers = {}
		for chunk in chunks:
			source = chunk.metadata.get("source", "unknown")
			location = chunk.metadata.get(
				"page",
				chunk.metadata.get("slide", chunk.metadata.get("section", "unknown")),
			)
			chunk_key = (source, location)
			chunk_numbers[chunk_key] = chunk_numbers.get(chunk_key, 0) + 1
			chunk.metadata["chunk_id"] = f"{source}_{location}_{chunk_numbers[chunk_key]}"

		return chunks
