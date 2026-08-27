"""
Retrieval pipeline: ubah pertanyaan user jadi embedding, cari top-k
chunk paling relevan di ChromaDB.
"""
import os
from pathlib import Path

import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "lky_speeches"
EMBEDDING_MODEL = "gemini-embedding-001"
TOP_K = 5

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Cek file .env kamu.")

_client = genai.Client(api_key=api_key)
_chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def embed_query(query: str) -> list[float]:
    """task_type=RETRIEVAL_QUERY -- beda dari saat embed dokumen
    (RETRIEVAL_DOCUMENT di Phase 8), supaya vector query & dokumen
    'diarahkan' benar untuk dicocokkan."""
    result = _client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return result.embeddings[0].values


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    query_embedding = embed_query(query)
    results = _collection.query(query_embeddings=[query_embedding], n_results=top_k)

    passages = []
    for i in range(len(results["ids"][0])):
        passages.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
            "metadata": results["metadatas"][0][i],
        })
    return passages