import os

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

FAISS_INDEX_PATH = "vector_store/index.faiss"
DOC_STORE_PATH = "vector_store/docs.pkl"

OPENAI_MODEL = "gpt-4.1-mini"
TOP_K = 3
DEDUP_THRESHOLD = 0.9

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")