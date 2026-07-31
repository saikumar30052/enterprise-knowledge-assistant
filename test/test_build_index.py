import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.build_index import VectorIndexer


print("----------------------------------------")
print("Building Enterprise Knowledge Base...")
print("----------------------------------------")
print()

try:
    indexer = VectorIndexer()
    indexer.build_index()
    print()
    print("Index Built Successfully")
except Exception as exc:
    print(f"Index build failed: {exc}")
