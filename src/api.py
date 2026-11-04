"""
FastAPI backend server for EduRAG — Intelligent Coursework Retrieval System
Replaces the Telegram bot with a modern REST API.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from db import (
    calculate_sha256,
    insert_document,
    list_documents,
    get_document,
    delete_document,
    update_document_index_status,
)

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s — %(message)s",
)
logger = logging.getLogger("edurag.api")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="EduRAG API",
    description="Intelligent Coursework Retrieval System — REST API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
DATA_DIR = ROOT_DIR / "data"
NOTES_DIR = ROOT_DIR / "notes"

SUBJECT_LABELS: dict[str, str] = {
    "BCS301": "Maths for CS",
    "BCS302": "Data Structures",
    "BCS303": "Operating Systems",
    "BCS402": "Design & Analysis of Algorithms",
    "BCS403": "Software Engineering",
    "BCS501": "Computer Networks",
    "BCS503": "Automata Theory",
    "BEC303": "Electronic Circuits",
    "BEC304": "Signals & Systems",
    "BMATE101": "Engineering Mathematics",
}

SUBJECT_PROMPTS: dict[str, list[str]] = {
    "BCS301": [
        "Explain Bayes Theorem with an engineering example",
        "What is Fourier Series and its Dirichlet conditions?",
        "Solve second order linear differential equations"
    ],
    "BCS302": [
        "Explain time complexity between AVL tree and Red-Black tree",
        "How does Dijkstra's algorithm work with Priority Queue?",
        "Compare Linear Probing and Quadratic Probing in Hashing"
    ],
    "BCS303": [
        "Explain Banker's Algorithm for Deadlock Avoidance",
        "Compare Preemptive vs Non-Preemptive CPU Scheduling",
        "What is Paging and how does TLB work?"
    ],
    "BCS402": [
        "Explain Strassen's Matrix Multiplication and complexity",
        "Explain Bellman-Ford algorithm with negative edge weights",
        "Differentiate Backtracking vs Branch & Bound"
    ],
    "BCS403": [
        "Explain Agile Scrum lifecycle and sprint ceremonies",
        "Difference between Functional and Non-Functional testing",
        "Explain Clean Architecture and SOLID principles"
    ],
    "BCS501": [
        "Explain 3-way handshake in TCP connection",
        "Compare Distance Vector vs Link State routing",
        "Explain CSMA/CD collision detection in Ethernet"
    ],
    "BCS503": [
        "Convert NFA to equivalent DFA using Subset Construction",
        "Explain Chomsky Hierarchy of grammars with examples",
        "What is the Halting Problem in Turing Machines?"
    ],
    "BEC303": [
        "Explain frequency response of CE BJT amplifier",
        "Differentiate Positive vs Negative feedback amplifiers",
        "Explain Astable Multivibrator using 555 timer"
    ],
    "BEC304": [
        "Explain Continuous-Time Fourier Transform properties",
        "What is ROC in Z-Transform and its stability condition?",
        "Explain Nyquist Sampling Theorem and Aliasing"
    ],
    "BMATE101": [
        "Explain Mean Value Theorems and geometrical interpretation",
        "Find eigenvalues and eigenvectors of a matrix",
        "Explain Taylor series for functions of two variables"
    ],
}


def _load_json(path: Path) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _get_sources() -> dict:
    return _load_json(DATA_DIR / "sources.json")


def _get_notes_links() -> dict:
    return _load_json(DATA_DIR / "notes_link.json")


# ---------------------------------------------------------------------------
# Background job tracking (simple in-memory store)
# ---------------------------------------------------------------------------
_job_status: dict[str, dict] = {}  # job_id -> {status, message, error?}


def _make_job_id(branch: str, sub_code: str) -> str:
    return f"{branch.lower()}_{sub_code.upper()}"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str


class DownloadRequest(BaseModel):
    branch: str
    subject_code: str


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/subjects")
def list_subjects() -> JSONResponse:
    """Return all known subjects with metadata."""
    sources = _get_sources()
    notes_links = _get_notes_links()
    all_codes = sorted(set(list(sources.keys()) + list(notes_links.keys())))

    subjects = []
    for code in all_codes:
        notes_path = NOTES_DIR / code
        local_pdfs = list(notes_path.glob("*.pdf")) if notes_path.exists() else []

        subjects.append(
            {
                "code": code,
                "name": SUBJECT_LABELS.get(code, code),
                "has_source": code in sources,
                "has_links": code in notes_links,
                "has_local_files": len(local_pdfs) > 0,
                "file_count": len(local_pdfs),
                "source_url": sources.get(code),
                "suggested_prompts": SUBJECT_PROMPTS.get(code, []),
            }
        )

    return JSONResponse({"subjects": subjects})


@app.post("/api/download")
def download_subject(req: DownloadRequest, background_tasks: BackgroundTasks) -> dict:
    """Trigger a scrape + download + index job in the background."""
    from scraper import get_notes
    from rag import add_to_db

    job_id = _make_job_id(req.branch, req.subject_code)

    if job_id in _job_status and _job_status[job_id].get("status") == "running":
        return {"job_id": job_id, "status": "already_running"}

    _job_status[job_id] = {"status": "running", "message": "Scraping notes…"}

    def _run():
        try:
            result = get_notes(req.branch.lower(), req.subject_code.upper())
            if not result:
                _job_status[job_id] = {
                    "status": "failed",
                    "message": "Could not find notes for this subject/branch combination.",
                }
                return

            _job_status[job_id]["message"] = "Indexing PDFs into vector database…"
            add_to_db(req.subject_code.upper())
            _job_status[job_id] = {
                "status": "done",
                "message": f"Successfully downloaded & indexed {req.subject_code.upper()} materials.",
            }
        except Exception as exc:
            logger.exception("Download job failed")
            _job_status[job_id] = {"status": "failed", "message": str(exc)}

    background_tasks.add_task(_run)
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/download/status/{job_id}")
def download_status(job_id: str) -> dict:
    if job_id not in _job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **_job_status[job_id]}


@app.post("/api/ask")
def ask_question(req: AskRequest) -> dict:
    """Run RAG query and return answer with citations/sources."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        from rag import query_rag
        res = query_rag(req.question)
        return {
            "question": req.question,
            "answer": res["answer"],
            "sources": res.get("sources", []),
            "has_context": res.get("has_context", False),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("RAG query failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/notes/{subject_code}")
def list_note_files(subject_code: str) -> dict:
    """List downloaded PDF files or cached remote preview links for a subject."""
    code = subject_code.upper()
    notes_path = NOTES_DIR / code
    local_files = []
    if notes_path.exists():
        files = sorted(notes_path.glob("*.pdf"))
        local_files = [
            {"name": f.name, "size_kb": round(f.stat().st_size / 1024, 1), "is_local": True}
            for f in files
        ]

    # Include cached cloud slide links from notes_link.json if available
    remote_links = []
    notes_links = _get_notes_links()
    if code in notes_links:
        for idx, link in enumerate(notes_links[code]):
            remote_links.append({
                "name": f"Module_{idx + 1}_Cloud_Slides.pdf",
                "preview_url": link,
                "is_local": False,
            })

    return {
        "subject_code": code,
        "files": local_files,
        "remote_links": remote_links,
        "has_local_files": len(local_files) > 0,
        "has_remote_links": len(remote_links) > 0,
    }


@app.get("/api/notes/{subject_code}/{filename}")
def download_note_file(subject_code: str, filename: str) -> FileResponse:
    """Stream a specific PDF file inline for live browser viewing."""
    file_path = NOTES_DIR / subject_code.upper() / filename
    if not file_path.exists() or not file_path.suffix == ".pdf":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        content_disposition_type="inline",
    )


# ---------------------------------------------------------------------------
# Upload & Document Management Endpoints
# ---------------------------------------------------------------------------
UPLOADS_DIR = ROOT_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _index_uploaded_pdf_task(doc_id: str, file_path_str: str, subject_code: str):
    """Background task to extract and index uploaded PDF using the Triage Engine."""
    try:
        from rag import pdf_2_md, add_to_vdb
        file_path = Path(file_path_str)
        md = pdf_2_md(file_path, subject_code)
        if md and len(md) == 3:
            add_to_vdb(md)
            chunk_count = len(md[0])
            import pymupdf
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            update_document_index_status(doc_id, is_indexed=1, chunk_count=chunk_count, page_count=page_count)
            logger.info(f"Successfully indexed uploaded document {doc_id} ({chunk_count} chunks)")
    except Exception as e:
        logger.error(f"Failed indexing uploaded document {doc_id}: {e}")


@app.post("/api/upload")
def upload_study_material(
    file: UploadFile = File(...),
    scheme: str = Form("2022 Scheme"),
    subject_code: str = Form(...),
    sem: str = Form("Sem 5"),
    material_type: str = Form("Study Material"),
    title: Optional[str] = Form(None),
) -> dict:
    """Upload study material / question paper PDF and register in SQLite and ChromaDB."""
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files (.pdf) are supported.")

    content = file.file.read()
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid PDF file. Header missing %PDF- signature.")

    sub_clean = subject_code.upper().strip()
    clean_scheme = scheme.strip() or "2022 Scheme"
    clean_sem = sem.strip() or "Sem 5"
    clean_type = material_type.strip() or "Study Material"
    clean_title = (title or "").strip() or filename

    # Compute SHA256 for deduplication
    file_hash = calculate_sha256(content)

    # Save to disk
    sub_upload_dir = UPLOADS_DIR / sub_clean
    sub_upload_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{file_hash[:8]}_{filename.replace(' ', '_')}"
    saved_path = sub_upload_dir / safe_filename

    if not saved_path.exists():
        with open(saved_path, "wb") as f:
            f.write(content)

    # Count pages
    page_count = 0
    try:
        import pymupdf
        pdoc = pymupdf.open(stream=content, filetype="pdf")
        page_count = len(pdoc)
    except Exception:
        pass

    # Insert into SQLite
    doc_record = insert_document(
        scheme=clean_scheme,
        subject_code=sub_clean,
        sem=clean_sem,
        material_type=clean_type,
        title=clean_title,
        file_name=filename,
        file_path=str(saved_path),
        file_size_bytes=len(content),
        file_hash=file_hash,
        page_count=page_count,
        is_indexed=0,
        chunk_count=0,
    )

    # Dispatch background indexing into ChromaDB in a daemon thread
    threading.Thread(
        target=_index_uploaded_pdf_task,
        args=(doc_record["id"], str(saved_path), sub_clean),
        daemon=True,
    ).start()

    return {
        "status": "ok",
        "message": f"Successfully uploaded {filename}",
        "document": doc_record,
    }


@app.get("/api/documents")
def get_documents(
    subject_code: Optional[str] = None,
    material_type: Optional[str] = None,
) -> dict:
    """List uploaded study materials and question papers."""
    docs = list_documents(subject_code=subject_code, material_type=material_type)
    return {"documents": docs, "count": len(docs)}


@app.delete("/api/documents/{doc_id}")
def remove_document(doc_id: str) -> dict:
    """Delete a document from SQLite and filesystem."""
    deleted_path = delete_document(doc_id)
    if not deleted_path:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "ok", "message": f"Document {doc_id} deleted."}


@app.get("/api/documents/{doc_id}/view")
def view_document_pdf(doc_id: str) -> FileResponse:
    """Stream uploaded PDF for inline viewing in the workspace."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(doc["file_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing from disk")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        content_disposition_type="inline",
    )


# ---------------------------------------------------------------------------
# Serve the frontend SPA
# ---------------------------------------------------------------------------
FRONTEND_DIR = ROOT_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/")
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str = "") -> FileResponse:
        # Don't intercept /api routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        index = FRONTEND_DIR / "index.html"
        if not index.exists():
            raise HTTPException(status_code=404, detail="Frontend not built")
        response = FileResponse(str(index))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

