"""Hybrid retrieval and semantic search tools for ThesisForge AI."""

from __future__ import annotations
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import DocumentChunk
from database.repository import Repository


def _tokenize(text: str) -> List[str]:
    clean = re.sub(r"[^\w\s\.\%\-]", " ", text.lower())
    tokens = clean.split()
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
        "by", "of", "from", "as", "is", "was", "were", "are", "be", "this", "that",
    }
    return [t for t in tokens if t not in stopwords and len(t) > 1]


def _bm25_score(query_tokens: List[str], doc_tokens: List[str], avg_doc_len: float, k1: float = 1.5, b: float = 0.75) -> float:
    if not doc_tokens or not query_tokens:
        return 0.0

    doc_len = len(doc_tokens)
    score = 0.0

    doc_tf: Dict[str, int] = {}
    for t in doc_tokens:
        doc_tf[t] = doc_tf.get(t, 0) + 1

    for qt in query_tokens:
        if qt in doc_tf:
            tf = doc_tf[qt]
            num = tf * (k1 + 1)
            den = tf + k1 * (1 - b + b * (doc_len / (avg_doc_len or 1.0)))
            score += num / den

    return score


def search_documents(
    asset_id: str,
    query: str,
    repo: Repository,
    doc_types: Optional[List[str]] = None,
    top_k: int = 8,
) -> List[DocumentChunk]:
    all_chunks = repo.get_chunks_for_asset(asset_id)
    if not all_chunks:
        return []

    if doc_types:
        docs = {d.id: d for d in repo.list_documents_for_asset(asset_id)}
        all_chunks = [ch for ch in all_chunks if docs.get(ch.document_id) and docs[ch.document_id].doc_type in doc_types]

    if not all_chunks:
        return []

    query_tokens = _tokenize(query)
    query_phrase = query.lower().strip()

    tokenized_chunks: List[Tuple[DocumentChunk, List[str]]] = []
    total_len = 0
    for ch in all_chunks:
        tokens = _tokenize(ch.content)
        tokenized_chunks.append((ch, tokens))
        total_len += len(tokens)

    avg_len = total_len / max(len(tokenized_chunks), 1)
    scored_chunks: List[Tuple[DocumentChunk, float]] = []
    priority_keywords = {"ebitda", "revenue", "profit", "debt", "margin", "risk", "guidance", "order", "cash"}

    for ch, tokens in tokenized_chunks:
        bm25 = _bm25_score(query_tokens, tokens, avg_len)
        content_lower = ch.content.lower()

        phrase_bonus = 3.0 if query_phrase in content_lower else 0.0
        metric_bonus = 0.0
        for kw in priority_keywords:
            if kw in query_tokens and kw in tokens:
                metric_bonus += 1.5

        has_numbers = 1.0 if bool(re.search(r"\b\d+(?:\.\d+)?%?\b", ch.content)) else 0.0
        total_score = bm25 + phrase_bonus + metric_bonus + has_numbers
        scored_chunks.append((ch, total_score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [ch for ch, score in scored_chunks[:top_k]]


def retrieve_chunks(
    document_id: str,
    query: str,
    repo: Repository,
    top_k: int = 5,
) -> List[DocumentChunk]:
    doc = repo.get_document(document_id)
    if not doc:
        return []

    all_chunks = repo.get_chunks_for_asset(doc.asset_id)
    doc_chunks = [ch for ch in all_chunks if ch.document_id == document_id]
    if not doc_chunks:
        return []

    query_tokens = _tokenize(query)
    total_len = sum(len(_tokenize(ch.content)) for ch in doc_chunks)
    avg_len = total_len / max(len(doc_chunks), 1)

    scored: List[Tuple[DocumentChunk, float]] = []
    for ch in doc_chunks:
        tokens = _tokenize(ch.content)
        score = _bm25_score(query_tokens, tokens, avg_len)
        if query.lower() in ch.content.lower():
            score += 2.0
        scored.append((ch, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [ch for ch, s in scored[:top_k]]
