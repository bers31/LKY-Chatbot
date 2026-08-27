"""
Evaluation runner: jalankan seluruh benchmark question lewat pipeline
RAG, hitung metrics otomatis (citation correctness, abstention accuracy).
Metrics yang butuh manusia/LLM-judge (groundedness, relevance) TIDAK
dihitung di sini -- lihat evaluation/README.md.

Dijalankan setelah semua chunk di-embed (Phase 8):
    python src/evaluation.py
"""
import json
from pathlib import Path

from retrieval import retrieve
from generation import generate_answer

BENCHMARK_FILE = Path("evaluation/benchmark_questions.json")
RESULTS_FILE = Path("evaluation/results.json")
ABSTENTION_PHRASE = "do not establish a clear position"


def check_citation_correctness(answer: str, passages: list[dict]) -> bool:
    retrieved_titles = {p["metadata"].get("title", "") for p in passages}
    if not retrieved_titles:
        return "(none relevant)" in answer.lower() or ABSTENTION_PHRASE in answer.lower()
    return any(title and title in answer for title in retrieved_titles)


def check_abstention(answer: str, expects_insufficient_evidence: bool) -> bool:
    said_insufficient = ABSTENTION_PHRASE in answer.lower()
    return said_insufficient == expects_insufficient_evidence


def main():
    questions = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    results = []

    print(f"Menjalankan {len(questions)} benchmark question...\n")

    for q in questions:
        passages = retrieve(q["question"])
        answer = generate_answer(q["question"], passages)

        result = {
            "id": q["id"],
            "question": q["question"],
            "category": q.get("category"),
            "expects_insufficient_evidence": q.get("expects_insufficient_evidence", False),
            "answer": answer,
            "retrieved_titles": [p["metadata"].get("title") for p in passages],
            "citation_correct": check_citation_correctness(answer, passages),
            "abstention_correct": check_abstention(answer, q.get("expects_insufficient_evidence", False)),
        }
        results.append(result)
        print(f"[{q['id']}] citation_correct={result['citation_correct']} abstention_correct={result['abstention_correct']}")

    RESULTS_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    n = len(results)
    citation_rate = sum(r["citation_correct"] for r in results) / n if n else 0
    abstention_rate = sum(r["abstention_correct"] for r in results) / n if n else 0

    print(f"\n=== RINGKASAN (otomatis) ===")
    print(f"Citation correctness: {citation_rate:.0%} ({sum(r['citation_correct'] for r in results)}/{n})")
    print(f"Abstention accuracy:  {abstention_rate:.0%} ({sum(r['abstention_correct'] for r in results)}/{n})")
    print(f"\nRetrieval relevance, groundedness, answer relevance BELUM dihitung --")
    print(f"itu butuh baca manual/LLM-judge. Lihat evaluation/README.md.")
    print(f"\nHasil lengkap: {RESULTS_FILE}")


if __name__ == "__main__":
    main()