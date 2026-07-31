import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
	sys.stdout.reconfigure(encoding="utf-8")

from ingestion.loader import DocumentLoader
from ingestion.chunker import DocumentChunker

loader = DocumentLoader("documents")
documents = loader.load_documents()

chunker = DocumentChunker()

chunks = chunker.split_documents(documents)

print(f"Original Documents : {len(documents)}")
print(f"Chunks Created     : {len(chunks)}")

print("=" * 80)

source_counts = Counter(chunk.metadata.get("source", "Unknown") for chunk in chunks)
print("----------------------------------------")
for source, count in sorted(source_counts.items()):
	print(f"{source} : {count}")
print("----------------------------------------")

print(chunks[0].metadata)

print("-" * 80)

print(chunks[0].page_content)