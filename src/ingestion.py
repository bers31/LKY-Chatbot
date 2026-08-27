"""
Ingestion pipeline: ekstrak & bersihkan teks dari PDF di data/sources.json.
Kalau file PDF belum ada lokal, DOWNLOAD dulu dari source_url -- ini yang
memungkinkan aplikasi bangun index dari nol saat deploy (lihat app.py),
karena data/raw/ sendiri tidak pernah di-commit ke repo.
"""
import json
import re
import urllib.request
from pathlib import Path
from pypdf import PdfReader

SOURCES_FILE = Path("data/sources.json")
PROCESSED_DIR = Path("data/processed")


def download_if_missing(doc: dict) -> Path | None:
    pdf_path = Path(doc["local_file"])
    if pdf_path.exists():
        return pdf_path

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(doc["source_url"], pdf_path)
    except Exception as e:
        print(f"  [GAGAL DOWNLOAD] {doc['id']}: {e}")
        return None

    # Validasi: pastikan yang terdownload benar PDF, bukan halaman HTML
    # (source_url yang menunjuk ke record-details page, bukan file .pdf
    # langsung, akan lolos request tapi isinya bukan PDF valid)
    with open(pdf_path, "rb") as f:
        header = f.read(4)
    if header != b"%PDF":
        pdf_path.unlink()
        print(f"  [BUKAN PDF] {doc['id']}: source_url kemungkinan bukan link PDF langsung")
        return None

    return pdf_path


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def clean_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    lines = [ln for ln in lines if not re.fullmatch(r"\s*-?\s*\d+\s*-?\s*", ln)]
    text = "\n".join(lines)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def run_ingestion() -> None:
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Memproses {len(sources)} dokumen...\n")

    for doc in sources:
        pdf_path = download_if_missing(doc)
        if pdf_path is None:
            print(f"[SKIP] {doc['id']}: tidak ada file valid")
            continue

        cleaned = clean_text(extract_text_from_pdf(pdf_path))
        out_path = PROCESSED_DIR / f"{doc['id']}.txt"
        out_path.write_text(cleaned, encoding="utf-8")

        char_count = len(cleaned)
        status = "OK" if char_count > 200 else "PERIKSA (teks sangat pendek)"
        print(f"[{status}] {doc['id']}: {char_count} karakter")

    print("\nSelesai.")


if __name__ == "__main__":
    run_ingestion()