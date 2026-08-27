# Ask Lee Kuan Yew

## Overview
Chatbot RAG yang menjawab pertanyaan berdasarkan pidato, wawancara, dan tulisan
Lee Kuan Yew yang terdokumentasi secara publik.

## Disclaimer
Ini adalah AI simulation berdasarkan sumber terdokumentasi Lee Kuan Yew -- BUKAN
Lee Kuan Yew yang sebenarnya. Jawaban dibatasi pada apa yang didukung sumber yang
di-retrieve; sistem secara eksplisit menyatakan ketidakcukupan bukti alih-alih mengarang.

## Architecture
Dua pipeline terpisah: ingestion (offline, sekali jalan) dan query (online, real-time).
Detail lengkap di docs/architecture.md.

## RAG Pipeline
PDF (data/raw/) -> extract & clean (ingestion.py) -> sentence-based chunking dengan
overlap (chunking.py) -> embedding gemini-embedding-001 (embedding.py) -> ChromaDB
lokal -> retrieval top-k=5 (retrieval.py) -> generation dengan grounding rules ketat
(generation.py, prompts/system_prompt.txt).

## Data Sources
National Archives of Singapore (nas.gov.sg/archivesonline/speeches). Metadata publik
di data/sources.json; teks penuh tidak didistribusikan ulang sesuai Terms of Use NAS
(lihat data/README.md).

## Chunking Strategy
Sentence-based (bukan paragraph-based -- paragraph tidak bertahan lewat ekstraksi
PDF, lihat "What Went Wrong"), target ~250 kata/chunk, overlap 2 kalimat.

## Embedding Strategy
gemini-embedding-001, 3072 dimensi (default, tanpa reduksi dimensi supaya tidak
perlu normalisasi manual). task_type RETRIEVAL_DOCUMENT untuk indexing, RETRIEVAL_QUERY
untuk query.

## Vector Database
ChromaDB, persisted lokal di data/chroma_db/, tidak di-commit ke repo (regenerable
dari data/chunks.json + API call).

## Hallucination Control
System prompt eksplisit melarang kutipan/citation fiktif, mewajibkan frasa abstention
persis ("The available sources do not establish a clear position on this topic.") saat
bukti tidak cukup, dan membedakan documented view vs inference vs speculation.

## Evaluation Method
20-30 benchmark question lintas 15 kategori (evaluation/benchmark_questions.json).
Citation correctness & abstention accuracy dihitung otomatis (src/evaluation.py);
groundedness & relevance dinilai manual (evaluation/README.md).

## Testing Results
**[ISI SETELAH run src/evaluation.py -- jangan isi dengan angka perkiraan]**

## What Went Wrong
- Asumsi awal chunking per-paragraf gagal: ekstraksi PDF (pypdf) tidak konsisten
  menyimpan baris kosong sebagai penanda paragraf, ditemukan lewat testing di
  Phase 6 sebelum sempat dipakai. Diganti ke sentence-based chunking di Phase 7.
- Chroma `add()` tidak update entry dengan id yang sama saat di-run ulang (silent
  no-op) -- ditemukan lewat testing Phase 8, diganti ke `upsert()`.
- **[Tambahkan temuan dari Phase 15/16 run yang sebenarnya di sini]**

## Known Limitations
- Corpus terbatas pada dokumen yang berhasil ditemukan manual di NAS (bukan seluruh
  arsip pidato LKY).
- Sentence splitter berbasis regex, bukan NLP penuh -- bisa salah di kalimat kompleks
  yang jarang.
- Tidak ada threshold jarak numerik untuk retrieval -- keputusan "cukup bukti"
  sepenuhnya bergantung pada judgment LLM di generation time.
- **[Tambahkan limitation lain yang ketemu saat testing nyata]**

## Local Setup / Environment Variables / Running the App
Lihat langkah Phase 3 (environment), Phase 6-8 (build index), dan perintah
`streamlit run app.py` di atas.

## Deployment
Streamlit Community Cloud -- lihat langkah Phase 17 di atas.

## Example Conversations
**[ISI dengan screenshot/transcript asli setelah app di-run -- bukan contoh karangan]**