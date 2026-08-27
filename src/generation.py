"""
Generation pipeline: susun prompt dari retrieved passages + system rules,
panggil Gemini untuk hasilkan jawaban grounded.
"""
import os
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

GENERATION_MODEL = "gemini-2.5-flash"
SYSTEM_PROMPT_FILE = Path("prompts/system_prompt.txt")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Cek file .env kamu.")

_client = genai.Client(api_key=api_key)
_system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")


def format_passages(passages: list[dict]) -> str:
    blocks = []
    for i, p in enumerate(passages, start=1):
        m = p["metadata"]
        blocks.append(
            f"[Passage {i}]\n"
            f"Title: {m.get('title')}\n"
            f"Date: {m.get('date')}\n"
            f"Source: {m.get('source_publication')}\n"
            f"Text: {p['text']}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, passages: list[dict]) -> str:
    if not passages:
        return (
            "Answer:\nThe available sources do not establish a clear position "
            "on this topic.\n\nSources:\n(none relevant)"
        )

    passages_text = format_passages(passages)
    user_content = f"Retrieved passages:\n\n{passages_text}\n\nUser question: {question}"

    response = _client.models.generate_content(
        model=GENERATION_MODEL,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=_system_prompt,
            temperature=0.2,
        ),
    )
    return response.text