"""
Milestone 3: Document Ingestion and Chunking Pipeline
Unofficial Guide to CS Courses at Cornell

Sources:
  - Local .txt files in data/  (Reddit threads saved manually + CUReviews + official docs)
  - Cornell CS Wiki (HTML)

Chunking: RecursiveCharacterTextSplitter, 450 chars, 75 overlap
"""

import re
import random
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Config (matches planning.md)
# ---------------------------------------------------------------------------

CHUNK_SIZE = 450
CHUNK_OVERLAP = 75

DATA_DIR = Path("data")

HTML_PAGES = [
    ("https://cornellcswiki.gitlab.io/faq.html", "cornellcswiki_faq"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; cornell-cs-guide/1.0; research project)"
}

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_local_file(filepath: str) -> str | None:
    path = Path(filepath)
    if not path.exists():
        print(f"  [SKIP] {filepath} — file not found")
        return None
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        print(f"  [SKIP] {filepath} — file is empty")
        return None
    return text


def fetch_html(url: str, source_name: str) -> str | None:
    """Fetch an HTML page, strip boilerplate, return main content text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Could not fetch {source_name}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove known boilerplate tags
    for tag in soup(["nav", "header", "footer", "script", "style",
                     "aside", "noscript", "form", "button", "iframe"]):
        tag.decompose()

    # Remove elements whose class/id suggest navigation or ads
    boilerplate_pattern = re.compile(
        r"(nav|menu|sidebar|cookie|banner|advertisement|share|comment-count)", re.I
    )
    for tag in soup.find_all(class_=boilerplate_pattern):
        tag.decompose()
    for tag in soup.find_all(id=boilerplate_pattern):
        tag.decompose()

    # Prefer semantic content containers
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=re.compile(r"content|body|post", re.I))
        or soup.body
    )
    if main is None:
        return None

    return main.get_text(separator="\n")


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove HTML artifacts, CUReviews boilerplate, and normalize whitespace."""
    # Strip leftover HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common HTML entities
    for entity, char in [
        ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
        ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " "),
    ]:
        text = text.replace(entity, char)
    # Remove bare URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove CUReviews structural metadata lines (exact-line matches):
    #   - section headers: Overall, Difficulty, Workload
    #   - standalone rating values: 1–5 or a dash
    #   - Grade / Major lines
    #   - date lines like 3/19/25 or 12/13/19
    #   - UI chrome: FlagReport, Not Liked YetHelpful?..., ...See more
    #   - COVID disclaimer
    #   - === separator lines
    boilerplate = re.compile(
        r"^("
        r"Overall|Difficulty|Workload"           # metadata headers
        r"|\d+|-"                                # standalone rating number or dash
        r"|Grade\b.*|Major\b.*"                  # Grade A / Major CS lines
        r"|\d{1,2}/\d{1,2}/\d{2,4}"             # dates: 3/19/25, 12/13/2019
        r"|FlagReport"                           # UI button text
        r"|Not Liked Yet.*|Helpful\?.*"          # combined or split like/helpful line
        r"|\.\.\. ?See more"                     # truncation link
        r"|My experience was affected.*"         # COVID note
        r"|={3,}"                                # === separator
        r")$",
        re.MULTILINE,
    )
    text = boilerplate.sub("", text)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse runs of spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_documents(documents: list[tuple[str, str]]) -> list[dict]:
    """
    Split (source_name, cleaned_text) pairs into chunks.
    Returns: [{"text": str, "source": str}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for source, text in documents:
        for split in splitter.split_text(text):
            stripped = split.strip()
            if stripped:  # filter zero-length chunks
                chunks.append({"text": stripped, "source": source})
    return chunks


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def load_and_chunk() -> list[dict]:
    """
    Full Milestone 3 pipeline:
      1. Load local .txt files from data/
      2. Fetch HTML pages
      3. Clean each document
      4. Chunk with RecursiveCharacterTextSplitter (450 chars / 75 overlap)
      5. Print diagnostics
    """
    documents: list[tuple[str, str]] = []

    # --- Local files (auto-discover data/*.txt) ---
    print("=" * 60)
    print("Loading local files")
    print("=" * 60)
    txt_files = sorted(DATA_DIR.glob("*.txt"))
    for path in txt_files:
        source_name = path.stem  # filename without extension
        print(f"  {path}...")
        raw = load_local_file(str(path))
        if raw:
            cleaned = clean_text(raw)
            documents.append((source_name, cleaned))
            print(f"    -> {len(cleaned):,} chars")

    # --- HTML ---
    print()
    print("=" * 60)
    print("Fetching HTML pages")
    print("=" * 60)
    for url, source_name in HTML_PAGES:
        print(f"  {source_name}...")
        raw = fetch_html(url, source_name)
        if raw:
            cleaned = clean_text(raw)
            documents.append((source_name, cleaned))
            print(f"    -> {len(cleaned):,} chars")

    # --- Chunk ---
    print()
    print("=" * 60)
    print(f"Chunking {len(documents)} documents")
    print("=" * 60)
    chunks = chunk_documents(documents)
    print(f"Total chunks: {len(chunks)}")

    # if len(chunks) < 50:
    #     print("[WARNING] Fewer than 50 chunks — chunks may be too large or documents too short.")
    # elif len(chunks) > 2000:
    #     print("[WARNING] More than 2,000 chunks — chunks may be too small.")

    # --- Inspect 5 random chunks ---
    # print()
    # print("=" * 60)
    # print("5 representative chunks (random sample)")
    # print("=" * 60)
    # sample = random.sample(chunks, min(5, len(chunks)))
    # for i, chunk in enumerate(sample, 1):
    #     print(f"\n[{i}] source={chunk['source']}  length={len(chunk['text'])} chars")
    #     print("-" * 50)
    #     print(chunk["text"])

    return chunks


if __name__ == "__main__":
    load_and_chunk()
