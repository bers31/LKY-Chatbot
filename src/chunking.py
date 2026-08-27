"""
Chunking pipeline: pecah teks bersih di data/processed/*.txt jadi
potongan (chunk) ~250 kata dengan overlap antar-chunk, lalu gabungkan
dengan metadata dari data/sources.json.

Output: data/chunks.json -- input untuk Phase 8 (embedding).

Dijalankan manual, setelah ingestion.py:
    python src/chunking.py
"""
import json
import re
from pathlib import Path

SOURCES_FILE = Path("data/sources.json")
PROCESSED_DIR = Path("data/processed")
CHUNKS_FILE = Path("data/chunks.json")

TARGET_WORDS = 250
OVERLAP_SENTENCES = 2

# Singkatan umum yang TIDAK boleh dianggap akhir kalimat (sering muncul
# di transkrip parlemen/pidato formal: "Mr. Speaker", "Dr. Goh", dst)
ABBREVIATIONS = ["Mr", "Mrs", "Ms", "Dr", "Prof", "Sir", "St", "vs", "etc", "No", "U.S", "U.K"]


def split_into_sentences(text: str) -> list[str]:
    protected = text
    for abbr in ABBREVIATIONS:
        protected = re.sub(rf'\b{re.escape(abbr)}\.', f'{abbr}<DOT>', protected)

    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z])', protected)
    return [s.replace('<DOT>', '.').strip() for s in raw if s.strip()]


def chunk_sentences(sentences: list[str], target_words: int = TARGET_WORDS,
                     overlap_sentences: int = OVERLAP_SENTENCES) -> list[str]:
    chunks = []
    i, n = 0, len(sentences)

    while i < n:
        chunk_sents = []
        word_count = 0
        j = i
        while j < n and word_count < target_words:
            chunk_sents.append(sentences[j])
            word_count += len(sentences[j].split())
            j += 1

        chunks.append(" ".join(chunk_sents))

        if j >= n:
            break
        i = max(i + 1, j - overlap_sentences)  # mundur utk overlap, tapi selalu maju

    return chunks


def run_chunking():
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    all_chunks = []

    print(f"Chunking {len(sources)} dokumen...\n")

    for doc in sources:
        txt_path = PROCESSED_DIR / f"{doc['id']}.txt"
        if not txt_path.exists():
            print(f"[SKIP] {doc['id']}: {txt_path} tidak ada. Jalankan ingestion.py dulu.")
            continue

        text = txt_path.read_text(encoding="utf-8")
        sentences = split_into_sentences(text)
        chunks = chunk_sentences(sentences)

        for idx, chunk_text in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{doc['id']}_{idx}",
                "doc_id": doc["id"],
                "chunk_index": idx,
                "text": chunk_text,
                "title": doc.get("title"),
                "speaker": doc.get("speaker"),
                "date": doc.get("date"),
                "document_type": doc.get("document_type"),
                "topic": doc.get("topic"),
                "source_publication": doc.get("source_publication"),
                "source_url": doc.get("source_url"),
            })

        print(f"[OK] {doc['id']}: {len(chunks)} chunk")

    CHUNKS_FILE.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTotal: {len(all_chunks)} chunk dari {len(sources)} dokumen -> {CHUNKS_FILE}")


if __name__ == "__main__":
    run_chunking()