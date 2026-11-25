"""Document extraction, semantic chunking, and ingestion tools for ThesisForge AI."""

from __future__ import annotations
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import DocumentChunk, DocumentRecord
from database.repository import Repository


def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_text_from_file(file_path: str) -> List[Tuple[int, str]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    pages: List[Tuple[int, str]] = []

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = re.sub(r"\r\n|\r", "\n", text)
                text = re.sub(r"[ \t]+", " ", text).strip()
                if text:
                    pages.append((idx + 1, text))
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF {file_path}: {e}")
    else:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        page_splits = re.split(r"(?:^|\n)---\s*PAGE\s*(\d+)\s*---\n?", content, flags=re.IGNORECASE)
        if len(page_splits) > 1:
            if page_splits[0].strip():
                pages.append((1, page_splits[0].strip()))
            for i in range(1, len(page_splits), 2):
                p_num = int(page_splits[i])
                p_text = page_splits[i + 1].strip()
                if p_text:
                    pages.append((p_num, p_text))
        else:
            chunk_len = 1500
            if len(content) <= chunk_len:
                pages.append((1, content.strip()))
            else:
                for idx, start in enumerate(range(0, len(content), chunk_len)):
                    page_slice = content[start : start + chunk_len].strip()
                    if page_slice:
                        pages.append((idx + 1, page_slice))

    return pages


def chunk_document(
    document_id: str,
    asset_id: str,
    pages: List[Tuple[int, str]],
    chunk_size: int = 500,
    overlap: int = 80,
) -> List[DocumentChunk]:
    chunks: List[DocumentChunk] = []
    chunk_counter = 0

    for page_num, text in pages:
        words = text.split()
        if not words:
            continue

        if len(words) <= chunk_size:
            chunk_content = " ".join(words)
            chunks.append(
                DocumentChunk(
                    id=str(uuid4()),
                    document_id=document_id,
                    asset_id=asset_id,
                    page_number=page_num,
                    chunk_index=chunk_counter,
                    content=chunk_content,
                    metadata={"page": page_num, "word_count": len(words)},
                )
            )
            chunk_counter += 1
        else:
            start = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_content = " ".join(chunk_words)

                chunks.append(
                    DocumentChunk(
                        id=str(uuid4()),
                        document_id=document_id,
                        asset_id=asset_id,
                        page_number=page_num,
                        chunk_index=chunk_counter,
                        content=chunk_content,
                        metadata={
                            "page": page_num,
                            "word_count": len(chunk_words),
                            "start_word": start,
                            "end_word": end,
                        },
                    )
                )
                chunk_counter += 1

                if end == len(words):
                    break
                start += chunk_size - overlap

    return chunks


def get_document_metadata(document_id: str, repo: Repository) -> Dict[str, Any]:
    doc = repo.get_document(document_id)
    if not doc:
        return {"error": f"Document {document_id} not found"}
    return {
        "document_id": doc.id,
        "asset_id": doc.asset_id,
        "filename": doc.filename,
        "source": doc.source,
        "source_date": doc.source_date,
        "content_hash": doc.content_hash,
        "status": doc.status,
        "page_count": doc.page_count,
        "doc_type": doc.doc_type,
    }


def ingest_document_file(
    asset_id: str,
    file_path: str,
    repo: Repository,
    source: str = "Company Filing",
    source_date: Optional[str] = None,
    doc_type: str = "annual_report",
) -> DocumentRecord:
    path = Path(file_path)
    content_hash = compute_file_hash(str(path))

    with repo._get_connection() as conn:
        existing = conn.execute("SELECT * FROM documents WHERE content_hash = ?", (content_hash,)).fetchone()
        if existing:
            return DocumentRecord(**dict(existing))

    pages = extract_text_from_file(str(path))
    doc_id = str(uuid4())

    doc = DocumentRecord(
        id=doc_id,
        asset_id=asset_id,
        filename=path.name,
        source=source,
        source_date=source_date,
        content_hash=content_hash,
        storage_path=str(path.resolve()),
        status="indexed",
        page_count=len(pages),
        doc_type=doc_type,
    )
    repo.add_document(doc)

    chunks = chunk_document(doc_id, asset_id, pages)
    repo.add_chunks(chunks)

    return doc
