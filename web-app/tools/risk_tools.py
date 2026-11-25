"""Risk assessment, threshold evaluation, and veto gate tools for ThesisForge AI."""

from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.repository import Repository


def calculate_risk_score(facts: List[Dict[str, Any]]) -> Dict[str, Any]:
    base_score = 0.20
    flags: List[str] = []
    evidence_ids: List[str] = []

    risk_factors = [
        (r"\b(show[\s-]cause|sebi|regulatory[\s-]action|investigation|enforcement|penalty)\b", 0.40, "REGULATORY_INVESTIGATION"),
        (r"\b(restatement|accounting[\s-]irregularit|adverse[\s-]opinion|auditor[\s-]resignation|material[\s-]weakness)\b", 0.45, "AUDIT_INTEGRITY_FLAG"),
        (r"\b(debt[\s-]to[\s-]equity\s*(?:>|exceeding|of)?\s*[2-9](?:\.\d+)?|high[\s-]leverage|default[\s-]risk|covenant[\s-]breach)\b", 0.35, "LEVERAGE_COVENANT_BREACH"),
        (r"\b(customer\s*concentration|top\s*\d+\s*customers?\s*account\s*for\s*(?:[5-9]\d|100)%)\b", 0.25, "CUSTOMER_CONCENTRATION_RISK"),
        (r"\b(declining\s*margin|margin\s*compression|operating\s*loss|negative\s*cash\s*flow)\b", 0.20, "MARGIN_COMPRESSION_FLAG"),
        (r"\b(litigation|contingent\s*liabilit(?:y|ies)|dispute)\b", 0.15, "LITIGATION_EXPOSURE"),
    ]

    for fact in facts:
        text = fact.get("passage_text", "") or fact.get("text", "")
        ev_id = fact.get("evidence_code") or fact.get("evidence_id")

        for pattern, weight, flag_name in risk_factors:
            if re.search(pattern, text, re.IGNORECASE):
                if flag_name not in flags:
                    flags.append(flag_name)
                    base_score += weight
                    if ev_id and ev_id not in evidence_ids:
                        evidence_ids.append(ev_id)

    final_score = min(round(base_score, 3), 1.0)

    return {
        "score": final_score,
        "flags": flags,
        "evidence_ids": evidence_ids,
        "summary": f"Calculated risk score {final_score:.2f} across {len(flags)} risk flags.",
    }


def check_required_evidence(asset_id: str, run_id: str, repo: Repository) -> Dict[str, Any]:
    evidence = repo.get_evidence_for_run(run_id)
    all_text = " ".join(ev.passage_text.lower() for ev in evidence)

    checks = {
        "has_revenue_metric": bool(re.search(r"revenue|turnover|sales", all_text)),
        "has_profit_metric": bool(re.search(r"profit|ebitda|pat|operating\s*income", all_text)),
        "has_balance_sheet_debt": bool(re.search(r"debt|borrowing|liability|leverage", all_text)),
        "has_auditor_note": bool(re.search(r"auditor|audit|opinion|notes\s*to\s*financial", all_text)),
    }

    missing = [k for k, present in checks.items() if not present]
    return {
        "asset_id": asset_id,
        "all_present": len(missing) == 0,
        "checks": checks,
        "missing_categories": missing,
        "total_evidence_count": len(evidence),
    }


def check_risk_thresholds(
    risk_score: float,
    flags: List[str],
    policy_threshold: float = 0.65,
    critical_flags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if critical_flags is None:
        critical_flags = ["REGULATORY_INVESTIGATION", "AUDIT_INTEGRITY_FLAG", "LEVERAGE_COVENANT_BREACH"]

    triggered_critical = [f for f in flags if f in critical_flags]
    score_breach = risk_score >= policy_threshold

    veto = bool(score_breach or triggered_critical)

    reasons: List[str] = []
    if score_breach:
        reasons.append(f"Risk score {risk_score:.2f} exceeds strict safety threshold {policy_threshold:.2f}.")
    if triggered_critical:
        reasons.append(f"Critical risk red-flag detected: {', '.join(triggered_critical)}.")

    return {
        "score": risk_score,
        "threshold": policy_threshold,
        "veto": veto,
        "triggered_critical_flags": triggered_critical,
        "reasons": reasons if veto else ["Risk parameters within acceptable tolerance."],
    }
