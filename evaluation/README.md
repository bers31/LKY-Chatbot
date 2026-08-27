# Evaluation

## Otomatis (dihitung oleh src/evaluation.py)
- Citation correctness -- apakah judul yang disebut di jawaban memang berasal dari passage yang di-retrieve.
- Abstention accuracy -- apakah pertanyaan berlabel `expects_insufficient_evidence: true` benar-benar dijawab "insufficient evidence".

## Manual / LLM-judge (isi setelah run evaluation.py)
Baca `evaluation/results.json`, untuk tiap baris nilai 1/0:
- **Retrieval relevance**: apakah passage yang di-retrieve nyambung ke pertanyaan.
- **Groundedness**: apakah tiap klaim di jawaban benar-benar didukung passage (bukan ditambahi dari luar).
- **Answer relevance**: apakah jawaban benar-benar menjawab pertanyaan yang diajukan.

Rekap manual ke tabel di sini setelah selesai dibaca -- JANGAN isi sebelum benar-benar membaca hasilnya.