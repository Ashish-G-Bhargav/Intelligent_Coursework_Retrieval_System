import os
import hashlib
import base64
from pathlib import Path
from dotenv import load_dotenv
import pymupdf
import pymupdf4llm
from openai import OpenAI

from retriever import (
    get_chroma_client,
    get_embedding_function,
    get_indexed_collection,
    get_context,
    retrieve,
)
from augmenter import build_prompt
from generator import generate

ROOT_DIR = Path(__file__).resolve().parent.parent

# ─── TIER 2: SCANNED PAGE VISION / OCR HANDLERS ───

def _transcribe_page_vision(img_bytes: bytes) -> str:
    """Send scanned page image to Gemini / OpenRouter Vision for high-accuracy LaTeX math transcription."""
    load_dotenv(ROOT_DIR / ".env")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openrouter_key = os.getenv("OPEN_ROUTER_API")

    if not gemini_key and not openrouter_key:
        return ""

    b64_img = base64.b64encode(img_bytes).decode("utf-8")
    prompt = (
        "Transcribe this engineering lecture note page into clean Markdown. "
        "Convert mathematical equations and formulas to LaTeX ($...$ or $$...$$). "
        "Preserve tables, lists, and state diagram representations accurately. "
        "Output only the transcribed Markdown text without preamble."
    )

    try:
        if gemini_key:
            # Google AI Studio Free Tier (Gemini 3.5 / 2.5 Flash)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            client = OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=gemini_key,
                timeout=30.0,
            )
        else:
            # OpenRouter Vision fallback
            model_name = os.getenv("VISION_MODEL", "google/gemini-2.0-flash-001")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                timeout=30.0,
            )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64_img}"},
                        },
                    ],
                }
            ],
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Triage Vision] Vision API transcription failed: {e}")
        return ""


def _transcribe_page_local_ocr(img_bytes: bytes) -> str:
    """Local fallback OCR if rapidocr_onnxruntime is installed."""
    try:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()
        result, _ = engine(img_bytes)
        if result:
            return "\n".join([line[1] for line in result]).strip()
    except ImportError:
        pass
    except Exception as e:
        print(f"[Triage Local OCR] Error: {e}")
    return ""


def _get_page_cache(cache_dir: Path, pdf_name: str, page_num: int, img_bytes: bytes):
    """Check and return cached OCR markdown from disk."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    img_hash = hashlib.md5(img_bytes).hexdigest()
    cache_file = cache_dir / f"{pdf_name}_p{page_num}_{img_hash}.md"
    if cache_file.exists():
        try:
            return cache_file, cache_file.read_text(encoding="utf-8")
        except Exception:
            pass
    return cache_file, None


# ─── ADAPTIVE TWO-TIER TRIAGE ENGINE ───

def extract_page_content(doc, page_idx: int, pdf_path: Path, sub_code: str, cache_dir: Path):
    """
    Tier 1 (Fast-Path): If digital text exists (len >= 40), use pymupdf4llm directly (<5ms).
    Tier 2 (Scanned Fallback): If image-only (len < 40), check disk cache -> Vision API -> Local OCR.
    """
    page = doc[page_idx]
    page_num = page_idx + 1
    raw_text = page.get_text("text").strip()

    # Tier 1: Digital Fast-Path
    if len(raw_text) >= 40:
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path), pages=[page_idx])
            if md_text and md_text.strip():
                return md_text.strip(), "digital"
        except Exception:
            return raw_text, "digital_raw"

    # Tier 2: Scanned Copy Fallback
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")

    cache_file, cached_text = _get_page_cache(cache_dir, pdf_path.name, page_num, img_bytes)
    if cached_text is not None:
        return cached_text, "scanned_cached"

    # Attempt Vision Transcription (Gemini / OpenRouter)
    vision_text = _transcribe_page_vision(img_bytes)
    if vision_text and vision_text.strip():
        try:
            cache_file.write_text(vision_text, encoding="utf-8")
        except Exception:
            pass
        return vision_text.strip(), "scanned_vision"

    # Attempt Local RapidOCR if Vision not available
    local_text = _transcribe_page_local_ocr(img_bytes)
    if local_text and local_text.strip():
        try:
            cache_file.write_text(local_text, encoding="utf-8")
        except Exception:
            pass
        return local_text.strip(), "scanned_local_ocr"

    # Neither available or page is blank
    return "", "scanned_empty"


def pdf_2_md(path, sub_code):
    """Adaptive Triage: processes digital and scanned pages with disk caching and empty-chunk filtering."""
    pdf_path = Path(path)
    if not pdf_path.exists():
        print(f"Error: PDF {path} not found.")
        return None

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {path}: {e}")
        return None

    pdf_filename = pdf_path.name
    cache_dir = ROOT_DIR / "notes" / sub_code.upper() / ".cache"

    texts = []
    metadata = []
    ids = []

    for i in range(len(doc)):
        page_num = i + 1
        page_content, extraction_type = extract_page_content(doc, i, pdf_path, sub_code, cache_dir)

        # Empty-chunk filter: never index zero-length chunks
        if not page_content or not page_content.strip():
            continue

        clean_metadata = {
            "source": pdf_filename,
            "page_number": page_num,
            "type": extraction_type,
            "sub_code": sub_code.upper(),
        }

        texts.append(page_content)
        metadata.append(clean_metadata)
        ids.append(f"{sub_code.upper()}_{pdf_filename}_chunk_{i}")

    doc.close()

    if not texts:
        print(f"Notice: No extractable text found in {pdf_filename} (scanned pages need GEMINI_API_KEY).")
        return None

    return [texts, metadata, ids]


def add_to_vdb(md_lst):
    if not md_lst or not md_lst[0]:
        return

    client = get_chroma_client()
    embedding_function = get_embedding_function()
    try:
        collection = client.get_or_create_collection(
            name="collage_notes_database",
            embedding_function=embedding_function
        )
        collection.upsert(documents=md_lst[0], ids=md_lst[2], metadatas=md_lst[1])
        print(f"Successfully added {len(md_lst[0])} chunks to '{collection.name}'.")
    except Exception as e:
        print(f"Error adding to vector DB: {e}")


def query_rag(query, n_results=5):
    documents, metadatas = retrieve(query, n_results)

    context = ""
    sources = []
    for i, doc in enumerate(documents):
        context += f"\n{doc}\n\n"
        meta = metadatas[i] if i < len(metadatas) else {}
        clean_snippet = " ".join(doc.split())[:180] + "..." if len(doc) > 180 else doc
        sources.append({
            "source": meta.get("source", "notes.pdf"),
            "page": meta.get("page_number", 1),
            "sub_code": meta.get("sub_code", ""),
            "snippet": clean_snippet,
        })

    prompt = build_prompt(context, query)
    answer = generate(prompt)
    return {
        "answer": answer,
        "sources": sources,
        "has_context": bool(context.strip()),
    }


def ask_llm(query):
    rag_res = query_rag(query)
    return rag_res["answer"]


def add_to_db(sub_code):
    path = ROOT_DIR / "notes" / sub_code.upper()
    if not path.exists() or not path.is_dir():
        print(f"Directory {path} does not exist.")
        return

    for file in sorted(path.glob("*.pdf")):
        print(f"Processing file: {file.name}")
        md = pdf_2_md(file, sub_code)
        if md:
            add_to_vdb(md)
        else:
            print(f"Skipping {file.name}: no extractable text chunks.")
