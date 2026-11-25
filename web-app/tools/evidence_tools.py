"""Evidence ledger management, topic filtering, and claim validation tools for ThesisForge AI."""

from __future__ import annotations
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import DocumentChunk, EvidenceItem
from database.repository import Repository


def create_evidence_pack(
    run_id: str,
    asset_id: str,
    chunks: List[DocumentChunk],
    repo: Repository,
) -> List[EvidenceItem]:
    evidence_items: List[EvidenceItem] = []
    seen_hashes = set()
    counter = 1

    docs_cache = {d.id: d for d in repo.list_documents_for_asset(asset_id)}

    for chunk in chunks:
        doc = docs_cache.get(chunk.document_id)
        doc_name = doc.filename if doc else "Filing Document"

        sentences = re.split(r"(?<=[.!?])\s+", chunk.content.strip())
        paragraphs = []
        curr = ""
        for s in sentences:
            if len(curr) + len(s) < 250:
                curr = f"{curr} {s}".strip()
            else:
                if curr:
                    paragraphs.append(curr)
                curr = s
        if curr:
            paragraphs.append(curr)

        for p in paragraphs:
            p_clean = p.strip()
            if len(p_clean) < 25:
                continue

            content_hash = hashlib.sha256(p_clean.encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            p_lower = p_clean.lower()
            if any(k in p_lower for k in ["risk", "litigation", "scrutiny", "penalty", "debt", "headwind", "restatement", "default"]):
                ev_type = "risk_fact"
            elif any(k in p_lower for k in ["revenue", "profit", "ebitda", "pat", "margin", "crore", "inr", "fy", "q1", "q2", "q3", "q4", "dividend"]):
                ev_type = "financial_fact"
            elif any(k in p_lower for k in ["guidance", "expect", "forecast", "target", "outlook", "pipeline"]):
                ev_type = "management_guidance"
            else:
                ev_type = "business_fact"

            period_match = re.search(r"\b(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4}|FY2[4567])\b", p_clean, re.IGNORECASE)
            reporting_period = period_match.group(0).upper() if period_match else "FY2025-26"

            ev_code = f"EV-{counter:03d}"
            counter += 1

            item = EvidenceItem(
                id=str(uuid4()),
                run_id=run_id,
                document_id=chunk.document_id,
                document_name=doc_name,
                evidence_code=ev_code,
                page_number=chunk.page_number,
                passage_text=p_clean,
                evidence_type=ev_type,
                reporting_period=reporting_period,
                published_at=doc.source_date if doc else None,
                content_hash=content_hash,
                relevance_score=1.0,
            )
            evidence_items.append(item)

    repo.add_evidence_items(evidence_items)
    return evidence_items


def get_evidence_by_topic(topic: str, run_id: str, repo: Repository) -> List[EvidenceItem]:
    all_evidence = repo.get_evidence_for_run(run_id)
    topic_words = set(re.findall(r"\w+", topic.lower()))

    matched = []
    for item in all_evidence:
        passage_words = set(re.findall(r"\w+", item.passage_text.lower()))
        common = topic_words.intersection(passage_words)
        if common or (topic.lower() in item.passage_text.lower()):
            matched.append(item)

    return matched if matched else all_evidence[:5]


def get_financial_facts(metric_names: List[str], run_id: str, repo: Repository) -> List[Dict[str, Any]]:
    all_evidence = repo.get_evidence_for_run(run_id)
    results = []

    for metric in metric_names:
        m_lower = metric.lower()
        for ev in all_evidence:
            text_lower = ev.passage_text.lower()
            if m_lower in text_lower:
                nums = re.findall(r"(?:₹|INR|Rs\.?|\$)?\s*\d+(?:[.,]\d+)?\s*(?:cr(?:ore)?|lakh|%|x|bps)?", ev.passage_text, re.IGNORECASE)
                results.append({
                    "metric": metric,
                    "evidence_id": ev.evidence_code,
                    "document_name": ev.document_name,
                    "page_number": ev.page_number,
                    "value_context": nums[0] if nums else "Reported",
                    "passage": ev.passage_text,
                })
    return results


def get_risk_evidence(topic: str, run_id: str, repo: Repository) -> List[EvidenceItem]:
    all_evidence = repo.get_evidence_for_run(run_id)
    risk_items = [ev for ev in all_evidence if ev.evidence_type == "risk_fact"]

    topic_lower = topic.lower()
    for ev in all_evidence:
        if ev not in risk_items:
            if any(k in ev.passage_text.lower() for k in ["risk", "debt", "decline", "slowdown", "penalty", "margin compression", topic_lower]):
                risk_items.append(ev)

    return risk_items if risk_items else all_evidence[-3:]


def get_contradictory_evidence(claim_ids: List[str], run_id: str, repo: Repository) -> List[Dict[str, Any]]:
    all_evidence = repo.get_evidence_for_run(run_id)
    conflicts = []

    metric_patterns = [
        ("revenue", r"revenue\s*(?:of|is|was|reached)?\s*([₹INR$\s\d.,]+(?:\s*cr|lakh)?)"),
        ("arr", r"arr\s*(?:of|is|was|reached)?\s*([₹INR$\s\d.,]+(?:\s*cr|lakh)?)"),
        ("ebitda", r"ebitda\s*(?:of|is|was)?\s*([₹INR$\s\d.,]+(?:\s*cr|lakh|%)?)"),
        ("growth", r"growth\s*(?:of|at)?\s*(\d+(?:\.\d+)?%)"),
        ("debt", r"debt\s*(?:of|at)?\s*([₹INR$\s\d.,]+(?:\s*cr|lakh)?)"),
        ("margin", r"margin\s*(?:of|at)?\s*(\d+(?:\.\d+)?%)"),
    ]

    for metric_name, pattern in metric_patterns:
        found_values = []
        for ev in all_evidence:
            matches = re.findall(pattern, ev.passage_text, re.IGNORECASE)
            for m in matches:
                found_values.append((m.strip(), ev.evidence_code, ev.document_name, ev.passage_text))

        unique_nums = {v[0] for v in found_values if len(v[0]) > 1}
        if len(unique_nums) > 1:
            # Check if discrepancy is across Audited vs PR documents
            has_pr = any("pr" in v[2].lower() or "press" in v[2].lower() for v in found_values)
            has_audited = any("audited" in v[2].lower() or "statutory" in v[2].lower() or "annual" in v[2].lower() for v in found_values)
            conflict_type = "AUDITED_VS_UNAUDITED_PR_CONFLICT" if (has_pr and has_audited) else "MULTI_DOCUMENT_DISCREPANCY"

            conflicts.append({
                "metric": metric_name,
                "conflict_type": conflict_type,
                "values_found": [{"value": v[0], "evidence_id": v[1], "document": v[2], "text": v[3]} for v in found_values],
                "explanation": f"Conflicting values reported for {metric_name} across documents: {', '.join(unique_nums)} ({conflict_type})",
            })

    return conflicts


def validate_claim_support(claim_text: str, evidence_ids: List[str], run_id: str, repo: Repository) -> Dict[str, Any]:
    if not evidence_ids:
        return {"supported": False, "score": 0.0, "reason": "No evidence IDs provided for claim."}

    all_evidence = {ev.evidence_code: ev for ev in repo.get_evidence_for_run(run_id)}

    missing_ids = [eid for eid in evidence_ids if eid not in all_evidence]
    if missing_ids:
        return {
            "supported": False,
            "score": 0.0,
            "reason": f"Cited evidence IDs not found in evidence ledger: {missing_ids}",
            "missing_ids": missing_ids,
        }

    claim_words = set(re.findall(r"\w+", claim_text.lower()))
    matches = 0
    total = len(evidence_ids)

    for eid in evidence_ids:
        ev = all_evidence[eid]
        passage_words = set(re.findall(r"\w+", ev.passage_text.lower()))
        common = claim_words.intersection(passage_words)
        if len(common) >= 2 or any(num in ev.passage_text for num in re.findall(r"\b\d+\b", claim_text)):
            matches += 1

    support_score = matches / max(total, 1)
    return {
        "supported": support_score >= 0.5,
        "score": support_score,
        "valid_ids": evidence_ids,
        "matched_count": matches,
    }
