"""Hybrid retrieval and ranking module for ThesisForge AI RAG."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Optional

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import DocumentChunk
from database.repository import Repository
from tools.retrieval_tools import retrieve_chunks, search_documents


class HybridRetriever:
    """Performs hybrid BM25 and keyword scoring strictly filtered by asset documents."""

    def __init__(self, repo: Repository):
        self.repo = repo

    def search(self, asset_id: str, query: str, top_k: int = 8) -> List[DocumentChunk]:
        return search_documents(asset_id=asset_id, query=query, repo=self.repo, top_k=top_k)

    def retrieve_from_document(self, document_id: str, query: str, top_k: int = 5) -> List[DocumentChunk]:
        return retrieve_chunks(document_id=document_id, query=query, repo=self.repo, top_k=top_k)
