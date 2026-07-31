import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.loader import DocumentLoader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

loader = DocumentLoader("documents")

documents = loader.load_documents()

print(f"Total Chunks Loaded : {len(documents)}")

print("-" * 50)

for doc in documents:
    print(doc.metadata)
    print(doc.page_content[:300])
    print("=" * 100)