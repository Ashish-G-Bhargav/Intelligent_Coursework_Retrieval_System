# EduRAG — Intelligent Coursework Retrieval System & Study Workspace

An AI-powered academic retrieval system that turns university syllabus notes and lecture slides into an interactive, grounded study platform. Answers are synthesized directly from official Visvesvaraya Technological University (VTU) coursework materials with side-by-side ground truth verification and live synchronized PDF viewing.

---

## Key Features

- **Side-by-Side Study Workspace**: Live in-browser PDF viewer paired with real-time AI explanations and ChromaDB ground-truth excerpts.
- **Synchronized Page Jumping**: Clicking any citation chip (e.g. `Module_2.pdf • p. 14`) instantly jumps the PDF viewer to that exact page (`#page=14`) without page reloads.
- **Adaptive Two-Tier Triage Engine**:
  - **Tier 1 (Digital Fast-Path)**: Instant sub-second parsing for digital lecture slides (< 5ms/page, zero API calls).
  - **Tier 2 (Scanned Vision Fallback)**: Automatically routes scanned copies / handwritten notes to Google Gemini Flash / Vision API for pristine LaTeX math and diagram transcription.
  - **Persistent Disk Caching**: Scanned pages are hashed and saved under `notes/<sub_code>/.cache/` so each page is parsed only once in history.
- **Zero Hallucination Grounding**: Prompted strictly on retrieved vector chunks with source page citations.
- **Automated Web Scraper**: Discovers coursework portal links, extracts Google Drive PDFs, and indexes them into ChromaDB.
- **6 Psychology-Calibrated Study Themes**:
  - **🌿 Deep Focus (Emerald Forest)**: Lowers test anxiety & cognitive load.
  - **🌊 Calm Clarity (Ocean Cyan)**: Boosts analytical working memory & recall.
  - **⚡ Exam Sprint (Cyber Crimson)**: Stimulates high-alert focus for timed prep.
  - **🔮 Flow State (Nebula Violet)**: Deep immersion for coding & automata algorithms.
  - **☀️ Solar Energy (Warm Amber)**: Dopamine booster to combat study fatigue.
  - **☕ Lofi Study Cafe (Warm Sepia)**: Low blue-light contrast for late-night reading.
- **Zero-Dependency Native PDF Viewer**: Uses the browser's built-in PDF engine with 0ms load penalty and native search/zoom controls.

---

## Architecture

```
User Query ──► FastAPI (/api/ask) ──► ChromaDB Vector Search (SentenceTransformer)
                                           │
                                           ▼ Top Chunks + Metadatas
Live PDF Viewer ◄── Citations + Ground Truth ── LLM (OpenRouter / Gemini)
(#page=N sync)
```

- **Frontend**: Single Page Application (`frontend/index.html`) with desktop split-view, command palette (`Ctrl+K`), circuit board canvas, 3D tilt cards, and in-app document preview.
- **Backend**: FastAPI (`src/api.py`) serving PDFs inline and exposing asynchronous indexing tasks.
- **Embeddings**: `mixedbread-ai/mxbai-embed-large-v1` via ChromaDB.
- **Parsing**: Adaptive Two-Tier Triage Engine (`src/rag.py`) combining `pymupdf4llm` with Gemini Vision fallback.

---

## Quick Start

### 1. Prerequisites & Installation

```bash
git clone https://github.com/your-username/Intelligent_Coursework_Retrieval_System.git
cd Intelligent_Coursework_Retrieval_System

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Add your API keys:

```env
# OpenRouter API (For DeepSeek/Llama answer generation)
OPEN_ROUTER_API=your_openrouter_api_key_here

# Google AI Studio Free Tier (For Scanned Notes OCR & LaTeX Math)
# Get free key at: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

### 3. Run the Server

```bash
python run.py
```

Open your browser at **[http://localhost:8000](http://localhost:8000)**.

### 4. Run the Test Suite

```bash
python tests/test_triage_engine.py
```

---

## Project Structure

```
├── data/
│   ├── notes_link.json      # Mapping of subject codes to PDF download links
│   ├── sources.json         # Subject portal & blogspot links
│   └── sub_name.json        # Subject code to full name mapping
├── frontend/
│   ├── index.html           # Modern SPA interface & Study Workspace
│   └── static/              # Static frontend assets
├── src/
│   ├── api.py               # FastAPI application & endpoints
│   ├── augmenter.py         # Prompt engineering & context augmentation
│   ├── generator.py         # OpenRouter LLM generation client
│   ├── rag.py               # Adaptive Triage Pipeline & PDF indexing
│   ├── retriever.py         # ChromaDB client & semantic search
│   └── scraper.py           # Web scraper for coursework materials
├── tests/
│   └── test_triage_engine.py# Automated component test suite
├── .env.example             # Example environment variables
├── .gitignore               # Production-grade git exclusion rules
├── requirements.txt         # Core dependencies
└── run.py                   # Server startup script
```

---

## License

MIT License.
