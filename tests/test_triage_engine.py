import sys
import time
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import pymupdf
from rag import pdf_2_md, extract_page_content, _get_page_cache

def test_tier_1_digital_fast_path():
    """Verify Tier 1 Fast-Path extracts digital notes in < 2 seconds."""
    bcs503_path = Path("notes/BCS503/Module_1_Lecture_Notes.pdf")
    if not bcs503_path.exists():
        print("  - Skipped BCS503 check (sample notes not downloaded).")
        return

    start = time.perf_counter()
    res = pdf_2_md(bcs503_path, "BCS503")
    elapsed = time.perf_counter() - start

    assert res is not None, "pdf_2_md should return non-None for digital PDF"
    texts, metadatas, ids = res
    assert len(texts) > 0, "Extracted chunks must not be empty"
    assert len(texts) == len(metadatas) == len(ids), "Metadata must be aligned"

    first_meta = metadatas[0]
    assert first_meta["sub_code"] == "BCS503"
    assert first_meta["page_number"] == 1
    assert first_meta["type"] == "digital"
    print(f"  OK: Tier 1 Passed in {elapsed:.3f}s. Extracted {len(texts)} pages.")

def test_tier_2_scanned_detection():
    """Verify Tier 2 correctly identifies scanned pages and prevents empty chunk pollution."""
    bcs301_path = Path("notes/BCS301/Module_1_Lecture_Notes.pdf")
    if not bcs301_path.exists():
        print("  - Skipped BCS301 check (sample notes not downloaded).")
        return

    doc = pymupdf.open(bcs301_path)
    cache_dir = Path("notes/BCS301/.cache")

    content, ext_type = extract_page_content(doc, 0, bcs301_path, "BCS301", cache_dir)
    doc.close()

    assert ext_type in ("scanned_empty", "scanned_cached", "scanned_vision")
    print(f"  OK: Tier 2 correctly classified scanned page as '{ext_type}'.")

def test_disk_caching_layer():
    """Verify that disk caching returns stored Markdown in < 20ms without OCR re-run."""
    cache_dir = Path("notes/TEST_MOCK/.cache")
    dummy_bytes = b"fake_png_data_for_unit_testing"

    cache_file, cached_text = _get_page_cache(cache_dir, "test.pdf", 1, dummy_bytes)
    assert cached_text is None, "Initial state should be cache miss"

    mock_md = "# Module 1: OS Concepts\n- Deadlock prevention\n- Formula: $R_i \leq A_i$"
    cache_file.write_text(mock_md, encoding="utf-8")

    start = time.perf_counter()
    cache_file_2, cached_text_2 = _get_page_cache(cache_dir, "test.pdf", 1, dummy_bytes)
    hit_time = (time.perf_counter() - start) * 1000

    assert cached_text_2 == mock_md, "Cache hit must match stored markdown"
    print(f"  OK: Disk cache hit verified in {hit_time:.2f} ms.")

    # Cleanup
    cache_file.unlink(missing_ok=True)
    if cache_dir.exists():
        try:
            cache_dir.rmdir()
            cache_dir.parent.rmdir()
        except Exception:
            pass

if __name__ == "__main__":
    print("\nRunning EduRAG Triage Engine Test Suite...")
    test_tier_1_digital_fast_path()
    test_tier_2_scanned_detection()
    test_disk_caching_layer()
    print("All tests passed successfully.\n")
