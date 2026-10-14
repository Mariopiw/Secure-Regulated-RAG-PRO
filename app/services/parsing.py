import io
import re
from dataclasses import dataclass
from docx import Document as DocxDocument
from pypdf import PdfReader
from app.core.config import settings

@dataclass(frozen=True)
class TextUnit:
    locator: str
    text: str

INJECTION_PATTERNS = [
    re.compile(r"ignore (all |any |the )?(previous|prior) instructions", re.I),
    re.compile(r"reveal (the )?(system|developer) prompt", re.I),
    re.compile(r"override (the )?(system|developer) instructions", re.I),
    re.compile(r"do not follow (the )?(system|previous) instructions", re.I),
    re.compile(r"exfiltrat(e|ion)", re.I),
]

def looks_like_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)

def extract_units(filename: str, raw: bytes) -> list[TextUnit]:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return [TextUnit(locator=f"page {i}", text=(p.extract_text() or "")) for i,p in enumerate(reader.pages,1) if (p.extract_text() or "").strip()]
    if lower.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(raw))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return [TextUnit(locator="document", text="\n\n".join(paragraphs))] if paragraphs else []
    if lower.endswith(".txt"):
        text = raw.decode("utf-8", errors="replace").strip()
        return [TextUnit(locator="document", text=text)] if text else []
    raise ValueError("Supported formats are .pdf, .docx, and .txt")

def chunk_text(text: str) -> list[str]:
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return []
    chunks, current = [], ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= settings.chunk_size_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            overlap = current[-settings.chunk_overlap_chars:]
            current = f"{overlap}\n\n{paragraph}"
        else:
            start = 0
            while start < len(paragraph):
                end = min(start + settings.chunk_size_chars, len(paragraph))
                chunks.append(paragraph[start:end])
                if end == len(paragraph):
                    current = ""
                    break
                start = max(end - settings.chunk_overlap_chars, start + 1)
    if current.strip():
        chunks.append(current.strip())
    return chunks
