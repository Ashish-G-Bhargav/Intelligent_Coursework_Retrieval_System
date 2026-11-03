"""
EduRAG Coursework Scraper
Powered by Scrapling (https://github.com/D4Vinci/Scrapling)
Primary Source: VTU Circle (https://vtucircle.com) — 2022 Scheme Module Notes
Secondary Fallback: Sai Vidya Institute of Technology (SVIT)
"""

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import requests
from scrapling.parser import Adaptor, Selector

logger = logging.getLogger("edurag.scraper")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
NOTES_DIR = ROOT_DIR / "notes"
VTUCIRCLE_BASE = "https://vtucircle.com"
SCRAPLING_DB = DATA_DIR / "scrapling_storage.db"


def make_download_link(link: str) -> Optional[str]:
    """Extract Google Drive file ID and build a direct export/download URL."""
    if not link:
        return None
    if "/d/" in link:
        file_id = link.split("/d/")[1].split("/")[0].split("?")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    if "id=" in link:
        import urllib.parse
        parsed = urllib.parse.urlparse(link)
        params = urllib.parse.parse_qs(parsed.query)
        file_ids = params.get("id")
        if file_ids:
            return f"https://drive.google.com/uc?export=download&id={file_ids[0]}"
    return None


def download_pdf(link: str, file_path: Union[str, Path]) -> bool:
    """Download a single PDF from a Google Drive link, handling confirmation cookies."""
    d_link = make_download_link(link)
    if not d_link:
        return False

    dest = Path(file_path)
    if dest.exists() and dest.stat().st_size > 1024:
        return True  # Already cached

    dest.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    try:
        response = session.get(d_link, stream=True, headers=header, timeout=30)
        # Google Drive warning token for large files
        for k, v in response.cookies.items():
            if k.startswith("download_warning"):
                response = session.get(f"{d_link}&confirm={v}", stream=True, headers=header, timeout=30)
                break

        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=16384):
                f.write(chunk)
        return True
    except Exception as e:
        logger.warning(f"Download failed for {link}: {e}")
        if dest.exists() and dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
        return False


def load_sources(src: Path) -> dict:
    try:
        with open(src, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


sources = load_sources(DATA_DIR / "sources.json")
notes_link = load_sources(DATA_DIR / "notes_link.json")


def save_sources(sources_dict: dict, src: Path) -> None:
    src.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "w") as f:
        json.dump(sources_dict, f, indent=4)


# ---------------------------------------------------------------------------
# VTU Circle Scraper (Primary)
# ---------------------------------------------------------------------------

def _discover_vtucircle(sub_code: str) -> Tuple[Optional[str], List[str]]:
    """
    Search VTU Circle for a subject code using Scrapling's self-healing Adaptor.
    Survives layout changes, class shifts, and WordPress wrapper migrations.
    Returns (hub_url, list_of_module_urls).
    """
    sub = sub_code.lower().strip()
    search_url = f"{VTUCIRCLE_BASE}/?s={sub}"
    try:
        resp = requests.get(search_url, headers=header, timeout=15)
        if resp.status_code != 200:
            return None, []

        storage_args = {"storage_file": str(SCRAPLING_DB), "url": search_url}
        page = Adaptor(resp.text, url=search_url, adaptive=True, storage_args=storage_args)

        # Self-healing retrieval of content and article anchors
        anchor_elements = page.css("article a, main a", identifier="vtu_search_links", adaptive=True, auto_save=True)
        all_links = set(el.attrib.get("href", "") for el in anchor_elements if el.attrib.get("href"))

        # Hub candidates: subject code in url, but not module/paper/solution/category/author/pagination
        ignore_keywords = ["module", "paper", "solution", "category", "author", "program", "page/", "?s="]
        hub_candidates = [
            l for l in all_links
            if sub in l.lower() and not any(k in l.lower() for k in ignore_keywords)
        ]
        module_links = set([l for l in all_links if sub in l.lower() and "module" in l.lower()])

        hub_url = hub_candidates[0] if hub_candidates else None
        if hub_url:
            hr = requests.get(hub_url, headers=header, timeout=15)
            if hr.status_code == 200:
                h_storage_args = {"storage_file": str(SCRAPLING_DB), "url": hub_url}
                h_page = Adaptor(hr.text, url=hub_url, adaptive=True, storage_args=h_storage_args)
                h_anchors = h_page.css("a", identifier="vtu_hub_module_links", adaptive=True, auto_save=True)
                for a in h_anchors:
                    href = a.attrib.get("href", "")
                    if sub in href.lower() and "module" in href.lower():
                        module_links.add(href)

        if not hub_url and module_links:
            hub_url = search_url

        sorted_mods = sorted(list(module_links))
        return hub_url, sorted_mods
    except Exception as e:
        logger.warning(f"VTU Circle discovery error for {sub_code}: {e}")
        return None, []


def _extract_drive_link_scrapling(module_page_url: str) -> Optional[str]:
    """
    Fetch module subpage and extract Google Drive preview link using Scrapling's self-healing Adaptor.
    Survives layout changes, class obfuscation, and renamed iframe attributes (data-src, data-lazy-src, etc.).
    """
    try:
        resp = requests.get(module_page_url, headers=header, timeout=15)
        if resp.status_code != 200:
            return None

        # 1. Self-healing adaptive parse with persistent fingerprint storage
        storage_args = {"storage_file": str(SCRAPLING_DB), "url": module_page_url}
        page = Adaptor(resp.text, url=module_page_url, adaptive=True, storage_args=storage_args)

        # Query iframes with auto-healing and persistent structural fingerprinting
        iframes = page.css("iframe", identifier="vtu_module_iframe", adaptive=True, auto_save=True)
        for iframe in iframes:
            # Check ALL attributes (data-src, src, data-lazy-src, data-embed-url, etc.)
            for val in iframe.attrib.values():
                if "drive.google.com" in val and ("/d/" in val or "id=" in val):
                    return val

        # 2. Adaptive fallback: check any embed, object, or anchor tag
        embeds = page.css("embed, object, a", identifier="vtu_module_embeds", adaptive=True, auto_save=True)
        for el in embeds:
            for val in el.attrib.values():
                if "drive.google.com" in val and ("/d/" in val or "id=" in val):
                    return val

        # 3. Direct regex scan fallback if markup was rewritten into scripts or JSON blobs
        match = re.search(r"https://drive\.google\.com/(?:file/d/|open\?id=)[a-zA-Z0-9_-]+(?:/preview)?", resp.text)
        if match:
            return match.group(0)

    except Exception as e:
        logger.warning(f"Error extracting drive link from {module_page_url}: {e}")
    return None


def _format_filename_from_slug(slug: str, idx: int) -> str:
    """Produce clean, readable filename: e.g. bcs503-module-1-textbook -> Module_1_Textbook.pdf"""
    clean = slug.strip("/").split("/")[-1]
    match = re.search(r"module[_-]?(\d+)[_-]?([a-zA-Z]+)?", clean, re.IGNORECASE)
    if match:
        mod_num = match.group(1)
        mod_type = (match.group(2) or "notes").capitalize()
        return f"Module_{mod_num}_{mod_type}.pdf"
    return f"Module_{idx + 1}.pdf"


# ---------------------------------------------------------------------------
# SVIT Scraper (Secondary Fallback)
# ---------------------------------------------------------------------------

def _scrape_svit_source(branch: str, sub_code: str) -> Optional[str]:
    """Fallback search on Sai Vidya Institute of Technology portal using Scrapling."""
    sub = sub_code.upper().strip()
    urls = [
        "https://saividya.ac.in/study-blogs",
        f"https://saividya.ac.in/study-material-{branch.lower()}.html",
    ]
    for link in urls:
        try:
            resp = requests.get(link, headers=header, timeout=15)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            sel = Selector(resp.text)

            for a in sel.css("a"):
                text = (a.text or "").strip().upper()
                href = a.attrib.get("href", "")
                if sub in text or sub in href.upper():
                    return href

            for tr in sel.css("table tr"):
                tds = tr.css("td")
                if len(tds) > 1 and sub in (tds[0].text or "").upper():
                    anchors = tds[1].css("a::attr(href)").getall()
                    if anchors:
                        return anchors[0]
        except Exception as e:
            logger.warning(f"SVIT lookup error for {sub}: {e}")
    return None


def _scrape_svit_notes(source_url: str) -> List[str]:
    """Extract iframe URLs from an SVIT blogspot/portal page using Scrapling."""
    try:
        resp = requests.get(source_url, headers=header, timeout=15)
        resp.raise_for_status()
        sel = Selector(resp.text)
        iframes = sel.css("iframe::attr(src)").getall() + sel.css("iframe::attr(data-src)").getall()
        return [f for f in iframes if "drive.google.com" in f]
    except Exception as e:
        logger.warning(f"SVIT notes extraction error: {e}")
        return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_source(branch: str, sub_code: str) -> Union[str, bool]:
    code = sub_code.upper().strip()
    if code in sources:
        return sources[code]

    # 1. Try VTU Circle
    hub_url, _ = _discover_vtucircle(code)
    if hub_url:
        sources[code] = hub_url
        save_sources(sources, DATA_DIR / "sources.json")
        return hub_url

    # 2. Fallback to SVIT
    svit_url = _scrape_svit_source(branch, code)
    if svit_url:
        sources[code] = svit_url
        save_sources(sources, DATA_DIR / "sources.json")
        return svit_url

    return False


def download(lst: List[str], sub_code: str, filenames: Optional[List[str]] = None) -> None:
    """Download list of Google Drive PDF links concurrently."""
    code = sub_code.upper().strip()
    target_dir = NOTES_DIR / code
    target_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for idx, link in enumerate(lst):
            fname = filenames[idx] if filenames and idx < len(filenames) else f"Module_{idx + 1}.pdf"
            dest = target_dir / fname
            tasks.append(executor.submit(download_pdf, link, dest))

        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logger.warning(f"Error during parallel download: {e}")


def get_notes(branch: str, sub_code: str) -> Union[List[str], bool]:
    code = sub_code.upper().strip()

    # 1. Check existing cache & local files
    local_path = NOTES_DIR / code
    has_local = local_path.exists() and any(local_path.glob("*.pdf"))
    if code in notes_link and has_local:
        return notes_link[code]

    # 2. Try VTU Circle (Primary)
    hub_url, module_urls = _discover_vtucircle(code)
    if module_urls:
        drive_links = []
        filenames = []

        # Extract drive preview URLs from module pages in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(_extract_drive_link_scrapling, m): m for m in module_urls}
            for future in as_completed(future_to_url):
                m_url = future_to_url[future]
                try:
                    d_link = future.result()
                    if d_link:
                        drive_links.append(d_link)
                        filenames.append(_format_filename_from_slug(m_url, len(filenames)))
                except Exception as e:
                    logger.warning(f"Failed extracting drive link from {m_url}: {e}")

        if drive_links:
            if hub_url:
                sources[code] = hub_url
                save_sources(sources, DATA_DIR / "sources.json")

            notes_link[code] = drive_links
            save_sources(notes_link, DATA_DIR / "notes_link.json")

            download(drive_links, code, filenames=filenames)
            return drive_links

    # 3. Fallback to SVIT (Secondary)
    source = get_source(branch, code)
    if source:
        svit_links = _scrape_svit_notes(source)
        if svit_links:
            notes_link[code] = svit_links
            save_sources(notes_link, DATA_DIR / "notes_link.json")
            download(svit_links, code)
            return svit_links

    return False
