"""Citation validation, argument ranking, and policy enforcement tools for ThesisForge AI."""

from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import (
    Argument,
    Claim,
    JudgeDecision,
    RebuttalRecord,
    RiskAssessment,
)
from database.repository import Repository


def validate_all_citations(run_id: str, claims: List[Claim], repo: Repository) -> Dict[str, Any]:
    valid_evidence = {e.evidence_code: e for e in repo.get_evidence_for_run(run_id)}

    uncited_claims: List[str] = []
    invalid_citations: List[Dict[str, Any]] = []
    total_citations = 0
    valid_citations_count = 0

    for c in claims:
        if not c.evidence_ids:
            uncited_claims.append(c.claim_id)
            continue

        for eid in c.evidence_ids:
            total_citations += 1
            if eid in valid_evidence:
                valid_citations_count += 1
            else:
                invalid_citations.append({"claim_id": c.claim_id, "invalid_evidence_id": eid})

    is_valid = (len(uncited_claims) == 0) and (len(invalid_citations) == 0)
    citation_validity_ratio = (valid_citations_count / max(total_citations, 1)) if total_citations > 0 else 0.0

    return {
        "is_valid": is_valid,
        "total_claims": len(claims),
        "uncited_claims": uncited_claims,
        "invalid_citations": invalid_citations,
        "citation_validity_ratio": round(citation_validity_ratio, 4),
        "ledger_size": len(valid_evidence),
    }


def rank_arguments(claims: List[Claim]) -> List[Claim]:
    def score_claim(c: Claim) -> float:
        score = len(c.evidence_ids) * 2.0
        nums = re.findall(r"\b\d+(?:\.\d+)?%?\b", c.text)
        score += len(nums) * 1.5
        if c.claim_type == "fact":
            score += 2.0
        elif c.claim_type == "calculation":
            score += 1.5
        return score

    return sorted(claims, key=score_claim, reverse=True)


def validate_rebuttal_target(response: str, target_claim_id: str, target_claim_text: str) -> Dict[str, Any]:
    resp_words = set(re.findall(r"\w+", response.lower()))
    target_words = set(re.findall(r"\w+", target_claim_text.lower()))

    overlap = resp_words.intersection(target_words)
    addressed = len(overlap) >= 2 or len(resp_words) > 15

    return {
        "target_claim_id": target_claim_id,
        "addressed": addressed,
        "overlap_terms": list(overlap)[:5],
        "status": "addressed" if addressed else "partially_addressed",
    }


def get_validated_arguments(
    run_id: str,
    bull_arg: Argument,
    bear_arg: Argument,
    rebuttals: List[RebuttalRecord],
    repo: Repository,
) -> Dict[str, Any]:
    all_claims: List[Claim] = []
    all_claims.extend(bull_arg.claims)
    all_claims.extend(bear_arg.claims)

    validation = validate_all_citations(run_id, all_claims, repo)

    return {
        "run_id": run_id,
        "bull_thesis": bull_arg.thesis,
        "bull_strongest_point": bull_arg.strongest_point.model_dump(),
        "bear_thesis": bear_arg.thesis,
        "bear_strongest_point": bear_arg.strongest_point.model_dump(),
        "rebuttals": [r.model_dump() for r in rebuttals],
        "validation_summary": validation,
        "all_evidence_ids": list({eid for c in all_claims for eid in c.evidence_ids}),
    }


def get_decision_policy(policy_id: str = "default_q18") -> Dict[str, Any]:
    return {
        "policy_id": policy_id,
        "recommendations_supported": ["BUY", "HOLD", "AVOID"],
        "buy_criteria": "Bull case demonstrates superior revenue/earnings growth with strong competitive moat; key bear concerns are refuted or manageable; risk veto is NOT triggered.",
        "avoid_criteria": "Bear case proves fundamental structural deterioration, insolvency/governance distress, or severe margin collapse; bull rebuttals are insufficient; risk veto is NOT triggered.",
        "hold_criteria": "Balanced bull vs bear tensions, high valuation offsetting growth, significant data uncertainty/conflicts, OR Risk Agent Veto triggered.",
        "risk_veto_override_rule": "If Risk Agent veto is True, provisional recommendation MUST be overridden to HOLD immediately.",
    }


def enforce_risk_veto(
    judge_decision: JudgeDecision,
    risk_assessment: RiskAssessment,
    policy_mode: str = "academic_assignment",
) -> JudgeDecision:
    if risk_assessment.veto:
        provisional = judge_decision.recommendation
        judge_decision.provisional_recommendation = provisional

        # Dual Policy Mode:
        # Academic Assignment Mode (default Q18 SRS): overrides to HOLD
        # Product Policy Mode: overrides to AVOID (with risk permission BLOCK)
        if policy_mode == "product_policy":
            override_rec = "AVOID"
            risk_permission = "BLOCK"
        else:
            override_rec = "HOLD"
            risk_permission = "PERMIT_WITH_RESTRICTION"

        judge_decision.recommendation = override_rec
        judge_decision.veto_applied = True
        judge_decision.veto_reason = "; ".join(risk_assessment.reasons)

        score_disp = f"{risk_assessment.score:.2f}" if risk_assessment.score is not None else "N/A"
        thresh_disp = f"{risk_assessment.threshold:.2f}" if risk_assessment.threshold is not None else "0.65"

        veto_claim = Claim(
            claim_id="RISK-VETO-01",
            text=f"Risk Veto Enforced [{policy_mode.upper()}]: Risk score ({score_disp} >= {thresh_disp}) or critical flags triggered mandatory {override_rec} override (provisional stance was {provisional}, execution permission {risk_permission}).",
            claim_type="interpretation",
            evidence_ids=risk_assessment.evidence_ids,
        )
        judge_decision.deciding_reasons.insert(0, veto_claim)
        judge_decision.evidence_ids = list(set(judge_decision.evidence_ids + risk_assessment.evidence_ids))

    return judge_decision
