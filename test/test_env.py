from dotenv import load_dotenv
import os

load_dotenv()

print("BASE_URL:", os.getenv("OLLAMA_BASE_URL"))
print("LLM_MODEL:", os.getenv("OLLAMA_LLM_MODEL"))
print("EMBED_MODEL:", os.getenv("OLLAMA_EMBEDDING_MODEL"))