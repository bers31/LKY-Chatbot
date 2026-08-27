"""
Ask Lee Kuan Yew -- Streamlit UI.
Jalankan dari root folder project: streamlit run app.py
"""
import os
import streamlit as st

try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

from src.ingestion import run_ingestion
from src.chunking import run_chunking
from src.embedding import run_embedding
from src.retrieval import retrieve, _collection
from src.generation import generate_answer


@st.cache_resource
def ensure_index_built():
    """Cek apakah vector DB sudah terisi. Kalau kosong (misal: baru saja
    di-deploy, data/chroma_db/ memang tidak di-commit ke repo), bangun
    dari nol: download PDF dari source_url -> chunk -> embed.
    @st.cache_resource memastikan ini cuma jalan SEKALI per instance
    aplikasi, bukan tiap kali ada pertanyaan baru."""
    if _collection.count() == 0:
        with st.spinner("Membangun index pertama kali (bisa beberapa menit)..."):
            run_ingestion()
            run_chunking()
            run_embedding()
    return True


ensure_index_built()

st.set_page_config(page_title="Ask Lee Kuan Yew", page_icon="🇸🇬")
st.title("Ask Lee Kuan Yew")
st.caption(
    "An AI simulation grounded in Lee Kuan Yew's documented speeches, "
    "interviews, and writings. This is not the real Lee Kuan Yew."
)

if "history" not in st.session_state:
    st.session_state.history = []

question = st.chat_input("Ask a question about LKY's documented views...")

if question:
    with st.spinner("Retrieving evidence and generating answer..."):
        passages = retrieve(question)
        answer = generate_answer(question, passages)
    st.session_state.history.append({"question": question, "answer": answer, "passages": passages})

for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        with st.expander("Retrieved passages (for debugging)"):
            for p in entry["passages"]:
                m = p["metadata"]
                st.markdown(f"**{m.get('title')}** ({m.get('date')}) — distance: {p['distance']:.3f}")
                st.text(p["text"][:300] + "...")