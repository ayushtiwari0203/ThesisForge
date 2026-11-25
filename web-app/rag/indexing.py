"""Document indexing and chunking module for RAG pipeline."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Tuple

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from tools.document_tools import chunk_document, compute_file_hash, extract_text_from_file, ingest_document_file


class DocumentIndexer:
    """Manages document text extraction, metadata normalization, and chunk indexing."""

    @staticmethod
    def extract_pages(file_path: str) -> List[Tuple[int, str]]:
        return extract_text_from_file(file_path)

    @staticmethod
    def hash_file(file_path: str) -> str:
        return compute_file_hash(file_path)
