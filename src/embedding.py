"""
Embedding pipeline: ubah tiap chunk di data/chunks.json jadi vector lewat
Gemini API, simpan ke ChromaDB (vector database lokal, persisted di
data/chroma_db/).

Dijalankan manual, setelah chunking.py:
    python src/embedding.py
"""
import json
import os
import time
from pathlib import Path

import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

CHUNKS_FILE = Path("data/chunks.json")
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "lky_speeches"
EMBEDDING_MODEL = "gemini-embedding-001"

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Cek file .env kamu.")

client = genai.Client(api_key=api_key)


def embed_text(text: str, retries: int = 1) -> list[float]:
    for attempt in range(retries + 1):
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"  [ERROR percobaan {attempt + 1}] {type(e).__name__}: {e}")
            if attempt < retries:
                time.sleep(2)
            else:
                raise


def flatten_metadata(chunk: dict) -> dict:
    """Chroma paling aman diisi metadata scalar (str/int/float/bool).
    'topic' aslinya list, digabung jadi satu string dulu."""
    return {
        "doc_id": chunk.get("doc_id") or "",
        "chunk_index": chunk.get("chunk_index") or 0,
        "title": chunk.get("title") or "",
        "speaker": chunk.get("speaker") or "",
        "date": chunk.get("date") or "",
        "document_type": chunk.get("document_type") or "",
        "topic": ", ".join(chunk.get("topic") or []),
        "source_publication": chunk.get("source_publication") or "",
        "source_url": chunk.get("source_url") or "",
    }


def run_embedding():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError("data/chunks.json kosong. Jalankan chunking.py dulu.")

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    print(f"Meng-embed {len(chunks)} chunk...\n")

    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk["text"])

        if i == 0:
            print(f"  Cek chunk pertama: dimensi embedding = {len(embedding)}")

        collection.upsert(
            ids=[chunk["chunk_id"]],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[flatten_metadata(chunk)],
        )

        print(f"[{i + 1}/{len(chunks)}] {chunk['chunk_id']} tersimpan")
        time.sleep(0.5)  # jaga-jaga terhadap rate limit free tier

    print(f"\nSelesai. Total {collection.count()} chunk di {CHROMA_DIR}")


if __name__ == "__main__":
    run_embedding()