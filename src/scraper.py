from bs4 import BeautifulSoup
import requests
import json
import os
from pathlib import Path

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
NOTES_DIR = ROOT_DIR / "notes"

def make_download_link(link):
    if not link:
        return False
    
    link_elems = link.split("/")
    if "d" in link_elems:
        uid_index = link_elems.index("d") + 1

        if uid_index < len(link_elems):
            file_id = link_elems[uid_index]
            return f"https://drive.google.com/uc?export=download&id={file_id}"

def download_pdf(link, file_path):
    d_link = make_download_link(link)

    if not d_link:
        return False
    
    try:
        with requests.get(d_link, stream=True, headers=header, timeout=30) as response:
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    except requests.exceptions.RequestException as e:
        print(f"Failed to download file: {e}")

def download(lst, sub_code):
    os.makedirs(NOTES_DIR / sub_code, exist_ok=True)
    for i in lst:
        name = lst.index(i)
        download_pdf(i, NOTES_DIR / sub_code / f"{name}.pdf")

def load_sources(src):
    try:
        with open(src, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

sources = load_sources(DATA_DIR / "sources.json")
notes_link = load_sources(DATA_DIR / "notes_link.json")

def save_sources(sources_dict, src):
    with open(src, "w") as f:
        json.dump(sources_dict, f, indent=4)

def get_source(branch, sub_code):
    if sub_code in sources:
        return sources[sub_code]
    
    try: 
        urls = [
            "https://saividya.ac.in/study-blogs",
            f"https://saividya.ac.in/study-material-{branch}.html",
        ]

        for link in urls:
            response = requests.get(link, headers=header, timeout=30)
            if response.status_code == 404:
                continue
            response.raise_for_status()
            scrape = BeautifulSoup(response.text, "lxml")

            for anchor in scrape.find_all("a", href=True):
                text = anchor.get_text(" ", strip=True).upper()
                href = anchor["href"]
                if sub_code.upper() in text or sub_code.upper() in href.upper():
                    sources[sub_code] = href
                    return href

            for table in scrape.find_all("table"):
                for row in table.find_all("tr"):
                    tds = row.find_all("td")
                    if len(tds) > 1 and sub_code.upper() in tds[0].get_text().upper():
                        anchor = tds[1].find("a", href=True)
                        if anchor:
                            sources[sub_code] = anchor["href"]
                            return anchor["href"]

        return False
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch the webpage. Details: {e}")
        return False

def get_notes(branch, sub_code):
    source = get_source(branch, sub_code)

    if not source:
        return False
    
    if sub_code in notes_link:
        return notes_link[sub_code]
    
    try:
        lst = []
        response = requests.get(source, headers=header, timeout=30)
        response.raise_for_status()
        web_page = response.text
        scrape = BeautifulSoup(web_page, "lxml")
        iframes = scrape.find_all("iframe")

        for iframe in iframes:
            iframe_src = iframe.get("src")
            if iframe_src:
                lst.append(iframe_src)

        if not lst:
            return False

        notes_link[sub_code] = lst
        download(notes_link[sub_code], sub_code)

        return lst
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch the webpage. Details: {e}")

save_sources(sources, DATA_DIR / "sources.json")
save_sources(notes_link, DATA_DIR / "notes_link.json")