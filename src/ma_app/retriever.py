import os
from typing import List
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from sentence_transformers import SentenceTransformer

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "ma_corpus")


class LocalEmbeddingFn:
    """Sentence-Transformers embedding function for Chroma when not using OpenAI."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class Retriever:
    def __init__(self):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

        if provider == "openai":
            emb_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            self.embedding = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"), model_name=emb_name
            )
        else:
            model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            self.embedding = LocalEmbeddingFn(model_name)

        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
        self.col = self.client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=self.embedding)

    def search(self, query: str, k: int = 4) -> List[str]:
        if not query.strip():
            return []
        res = self.col.query(query_texts=[query], n_results=k)
        return [doc for doc in (res.get("documents") or [[]])[0]]

