<div class="hero">

<h1>🇸🇬 Ask Lee Kuan Yew — Grounded RAG Chatbot</h1>

<p>AI Simulation Grounded in Documented Speeches · Retrieval-Augmented Generation · Hallucination-Controlled</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/RAG-6D28D9?style=flat-square" alt="RAG"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-8B5CF6?style=flat-square" alt="Google Gemini"/>
  <img src="https://img.shields.io/badge/ChromaDB-F59E0B?style=flat-square" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="MIT License"/>
</p>

<p>
A retrieval-augmented chatbot that answers questions using only Lee Kuan Yew's
documented speeches and public records — designed to cite its evidence, refuse
to answer beyond it, and never fabricate a quote.
</p>

</div>

---

> **⚠️ Disclaimer**
> This is an **AI simulation grounded in Lee Kuan Yew's documented speeches, interviews, and public records** — it is **not** the real Lee Kuan Yew, and it never claims to be. Every answer is restricted to what retrieved source material actually supports. Where the sources don't establish a clear position, the system says so explicitly instead of guessing.

---

## 📖 Project Overview

This project is a **retrieval-augmented generation (RAG) chatbot** built around a single constraint: it may only speak from evidence.

It was developed for a "What Would Lee Kuan Yew Do?" AI application challenge, where the core requirement was not a chatbot that *sounds* like Lee Kuan Yew, but one that is **provably grounded** in his actual documented record — with retrieval, citations, and evaluation as first-class parts of the system, not afterthoughts.

The pipeline is split into two halves that run at different times:

```text
OFFLINE — runs once, or when new documents are added
Source PDF (National Archives of Singapore)
        ↓
Text extraction & cleaning
        ↓
Sentence-based chunking (with overlap)
        ↓
Embedding (gemini-embedding-001)
        ↓
ChromaDB vector store

ONLINE — runs on every user question
User question
        ↓
Query embedding
        ↓
Top-k similarity search
        ↓
Grounded generation (gemini-2.5-flash)
        ↓
Answer + explicit citations
```

> **Core philosophy:** a chatbot that never fabricates is more valuable than one that always has an answer. Every design decision below optimizes for that, sometimes at the cost of a shorter or less confident-sounding response.

---

## 🎯 Project Objectives

1. Answer user questions using **only** retrieved, documented evidence.
2. Attach a visible citation to every claim — no source, no claim.
3. Explicitly refuse to answer when evidence is insufficient, rather than improvising.
4. Respect the legal terms of the source archive rather than bulk-redistributing copyrighted material.
5. Measure system quality with a real benchmark, not a demo-only impression.
6. Keep the entire stack simple enough to run, explain, and reproduce end-to-end.

---

## ✨ Key Features

### 🔍 Retrieval-Augmented Generation Pipeline

Every answer is generated from passages actually retrieved from the vector store for that specific question — the model never answers from parametric memory about Lee Kuan Yew alone. Retrieval uses `gemini-embedding-001` with task-type-aware embeddings (`RETRIEVAL_DOCUMENT` at indexing time, `RETRIEVAL_QUERY` at question time), which measurably improves match quality over using one generic embedding mode for both.

### 🚫 Hallucination & Abstention Control

The system prompt enforces a strict rule set: no invented quotations, no fabricated citations, no attributing an opinion to Lee Kuan Yew without textual support, and a required, exact abstention phrase — *"The available sources do not establish a clear position on this topic"* — for anything outside the retrieved evidence, including topics and technologies that postdate his lifetime.

### 📚 Source-Grounded Citations

Every answer ends with a `Sources` section built directly from the metadata of the passages that were actually retrieved for that query — title, date, and publication — never a citation invented by the model.

### ⚖️ Copyright-Aware Data Governance

Source material comes from the National Archives of Singapore, whose Terms of Use prohibit redistributing their content. Rather than committing PDFs (or even processed text) to the repository, the app stores only **metadata and source URLs** publicly, and rebuilds its own index at runtime by fetching directly from the original archive — see [Data Governance](#-data-governance--legal-compliance) below.

### 🧪 Structured Evaluation Framework

A 24-question benchmark spans leadership, geopolitics, meritocracy, governance, Singapore–Malaysia relations, China, education, and deliberately adversarial cases (leading premises, quote-fabrication traps, questions with no possible evidence). Citation correctness and abstention accuracy are graded automatically; groundedness and relevance are graded manually against a documented rubric.

### 💬 Interactive Streamlit Interface

A minimal chat interface showing the answer and its sources by default, with an expandable panel exposing the raw retrieved passages and their similarity distances — useful for debugging retrieval quality, not just for chatting.

---

## 🏗️ System Architecture

```text
┌───────────────────────────┐
│   OFFLINE INGESTION        │
│   PDF → clean → chunk →    │
│   embed → ChromaDB         │
└─────────────┬──────────────┘
              ↓
┌───────────────────────────┐
│   ONLINE QUERY             │
│   question → embed →       │
│   retrieve top-k →         │
│   grounded generation      │
└─────────────┬──────────────┘
              ↓
      Answer + Sources
```

The split matters: re-embedding the entire corpus on every user message would be slow and wasteful. Indexing happens once (or once per deployment, see below); querying is what happens live.

---

## 🧭 Design Principles

**1. Groundedness over fluency.** A shorter, hedged answer beats a fluent, unsupported one.

**2. Explicit abstention is a feature, not a failure.** The system is evaluated partly on how *often it correctly says "I don't know"* — see the `no-evidence` benchmark category.

**3. Citations are derived, never generated.** Source lists come from retrieval metadata, not from the language model's own text.

**4. Legal compliance is part of the architecture, not an afterthought.** The data pipeline was redesigned specifically so no copyrighted archive content is ever committed to a public repository.

**5. Every reported number must come from an actual run.** No score in this README is estimated — see [Project Status](#-project-status).

---

## 🗂️ Technical Components

| Component | Purpose |
|---|---|
| 📄 **PDF Ingestion** | Downloads & extracts text from National Archives source documents |
| ✂️ **Sentence Chunker** | Splits cleaned text into overlapping, retrieval-sized passages |
| 🧬 **Embedding Layer** | Converts chunks and queries into vectors (`gemini-embedding-001`) |
| 🗄️ **ChromaDB Vector Store** | Persists embeddings locally for similarity search |
| 🔎 **Retriever** | Finds the top-k most relevant passages for a question |
| ✍️ **Generator** | Produces grounded answers under strict citation/abstention rules (`gemini-2.5-flash`) |
| 🧪 **Evaluation Runner** | Executes the benchmark and scores automatic metrics |
| 💬 **Streamlit UI** | Chat interface with a debug view into retrieval |

---

## 🔬 Technical Implementation

### Chunking Strategy

Chunking is **sentence-based with a 2-sentence overlap**, targeting ~250 words per chunk — not paragraph-based, despite that being the original plan. Testing during development showed PDF text extraction does not reliably preserve paragraph boundaries, so paragraph-based splitting would have silently merged unrelated content. Sentence-based chunking also protects common abbreviations (`Mr.`, `Dr.`, `U.S.`) from being misread as sentence breaks — a real failure mode in parliamentary-speech transcripts.

### Embedding Strategy

`gemini-embedding-001` at its default 3072 dimensions, deliberately **not** reduced — dimensionality reduction requires manual vector normalization for correct similarity search, which adds real complexity for negligible benefit at this corpus size (tens, not millions, of chunks).

### Retrieval

Top-k (default 5) cosine-comparable similarity search. No hard numerical relevance threshold is applied before generation — that number can only be set correctly from real evaluation data, not guessed in advance, so the abstention decision is currently left entirely to the grounded generation step.

### Generation & Grounding

A dedicated system prompt (`prompts/system_prompt.txt`) encodes every grounding rule as an explicit instruction, run at low temperature (0.2) to favor consistency over creative variation.

---

## ⚖️ Data Governance & Legal Compliance

This is the part of the project that most beginner RAG tutorials skip entirely.

Source documents come from the **National Archives of Singapore**, whose Terms of Use explicitly prohibit reproducing or redistributing site content without written permission — personal, non-commercial research use is permitted; public rehosting is not.

That constraint shaped the architecture directly:

- `data/sources.json` (public, committed) — titles, dates, and **source URLs only**.
- `data/raw/`, `data/processed/`, `data/chroma_db/` (never committed) — the actual document content, present only on a local machine or inside a running deployment.
- On deployment, the app **rebuilds its own index at startup** by fetching each PDF directly from its original archive URL — the public repository never contains a copy of the source text itself.

The trade-off is honestly documented, not hidden: first load after a deployment (or after the app wakes from idling) is slower, since indexing happens live.

---

## 🧪 Evaluation Framework

```text
24 Benchmark Questions
        ↓
Retrieval + Generation (per question)
        ↓
   ┌────────────┴────────────┐
   ↓                         ↓
Automatic Metrics       Manual / Rubric Metrics
- Citation correctness  - Retrieval relevance
- Abstention accuracy   - Groundedness
                         - Answer relevance
```

Categories include leadership, geopolitics, meritocracy, governance, Singapore–Malaysia relations, China, education, and social policy — plus deliberately adversarial cases: a leading/loaded premise, a direct request for a fabricated quote, three questions about post-1990s topics Lee Kuan Yew could not have addressed, and a multi-topic question testing whether the system invents connections the sources don't support.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🐍 **Language** | Python 3.11+ | Core implementation |
| 💬 **Interface** | Streamlit | Chat UI + deployment target |
| 🧠 **Generation** | Gemini 2.5 Flash | Grounded answer generation |
| 🧬 **Embeddings** | gemini-embedding-001 | Document & query vectorization |
| 🗄️ **Vector Store** | ChromaDB | Local similarity search |
| 📄 **PDF Parsing** | pypdf | Source text extraction |
| ✅ **Validation** | Pydantic | Structured data handling |
| 🔐 **Config** | python-dotenv | Local secret management |

---

## 📊 Project Status

Reported honestly — this table is a status log, not a marketing claim.

| Component | Status |
|---|---|
| 📄 Data collection & metadata (`sources.json`) | ✅ Built — 9–10 documents, National Archives of Singapore |
| 🔄 Ingestion, chunking, embedding pipeline | ✅ Built |
| 🔎 Retrieval pipeline | ✅ Built |
| ✍️ Generation + grounding rules | ✅ Built |
| 💬 Streamlit interface | ✅ Built |
| 🧪 Evaluation benchmark (24 questions) | ✅ Built — **not yet run** |
| 📈 Evaluation results | ⏳ Pending first full run |
| ☁️ Public deployment | 🔧 In progress — see [Known Issues](#-known-issues) |

---

## 🧩 Key Engineering Decisions

Real iteration, kept instead of erased:

| Assumption | What testing showed | What changed |
|---|---|---|
| Chunk by paragraph, detected via blank lines in extracted PDF text | PDF extraction does not reliably preserve blank-line paragraph breaks | Switched to sentence-based chunking with overlap |
| Re-running the indexing script is safe with `collection.add()` | `add()` silently no-ops on a duplicate ID instead of updating it | Switched to `collection.upsert()` |
| Committing the built vector index would simplify deployment | Vector store content is still substantially the same protected text as the source PDFs | Redesigned deployment to rebuild the index at runtime from public source URLs instead |

## 🐞 Known Issues

- First deployment attempt hit a `ClientError` from the embedding API during index build; root cause still being isolated from Streamlit Cloud logs at time of writing.

---

## 🎥 Demo

<div align="center">

<p><strong>💬 Ask Lee Kuan Yew — Live Demo</strong></p>

<p>
<a href="#"><strong>► Add live Streamlit URL here once deployment is verified working</strong></a>
</p>

</div>

### 📸 Screenshots

*Add screenshots of the running chat interface here once the deployed app is confirmed working — e.g. `images/chat-example.png`, `images/sources-expander.png`.*

---

## 💼 Portfolio Alignment

| Capability | Project Evidence |
|---|---|
| RAG system design | Two-pipeline architecture (`src/ingestion.py` → `src/embedding.py` → `src/retrieval.py`) |
| Prompt engineering for reliability | `prompts/system_prompt.txt` — explicit grounding & abstention rules |
| Applied data governance | Runtime index rebuild architecture, respecting archive Terms of Use |
| Evaluation methodology design | 24-question benchmark, automatic + rubric-based metrics |
| Full-stack AI product delivery | Streamlit UI wired to a live retrieval + generation backend |
| Engineering judgment under real constraints | Documented pivots in [Key Engineering Decisions](#-key-engineering-decisions) |

> **Portfolio positioning:** this project demonstrates building a RAG system where being *right and honest* is treated as the primary success metric — not just producing plausible-sounding text.

---

## 📚 Documentation & Reproducibility

- `docs/architecture.md` — full pipeline design
- `docs/methodology.md` — chunking, embedding, and evaluation methodology
- `data/README.md` — data provenance and licensing notes
- `evaluation/README.md` — how automatic vs. manual metrics are scored

The public repository, together with `data/sources.json`, is sufficient to reproduce the entire corpus and index from scratch on another machine.

---

## 🔭 Future Development

- Tune a numerical relevance threshold once real evaluation data exists.
- Add hybrid (keyword + semantic) retrieval if evaluation shows a specific gap.
- Expand the source corpus beyond the current 9–10 documents.
- Cache the rebuilt index between deployments to avoid repeated cold-start indexing.

---

## 📄 License

Original code, prompts, and documentation in this repository are licensed under the **MIT License** — see [`LICENSE`](LICENSE).

> Source material referenced in `data/sources.json` originates from the National Archives of Singapore and remains subject to its own Terms of Use. This repository does not redistribute that content — see [Data Governance](#-data-governance--legal-compliance).

---

<div class="contact-hero">

<p><strong>Interested in the project?</strong></p>

<p>
👨‍💻 <strong>Bernardo Nandaniar Sunia</strong><br/>
Computer Science Graduate — Diponegoro University<br/>
RAG Systems · AI Application Engineering · Applied NLP
</p>

<p>
<a href="https://linkedin.com/in/bernardo-sunia/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
</a>
<a href="https://mail.google.com/mail/?view=cm&fs=1&to=suniabernardo@gmail.com">
<img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email">
</a>
<a href="https://github.com/bers31">
<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>
<a href="https://bit.ly/bernardo-my_portfolio">
<img src="https://img.shields.io/badge/Portfolio-255E63?style=for-the-badge&logo=About.me&logoColor=white" alt="Portfolio">
</a>
</p>

</div>

---

## 📌 Conclusion

This project treats a chatbot's willingness to say *"the sources don't support an answer"* as a measure of quality, not a shortcoming. The retrieval, generation, and evaluation layers were all built around that one constraint — including the parts that were harder or slower because of it, like rebuilding the index at deploy time instead of shipping a pre-baked copy of copyrighted archive text.

It is a working system with a real benchmark waiting to be run, not a finished, fully-scored product — and this README will be updated with real numbers, real screenshots, and a live demo link the moment those exist.