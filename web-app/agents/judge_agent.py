"""Judge Agent module for ThesisForge AI (SRS Section 6)."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.llm_adapter import LLMServiceAdapter
from database.models import (
    Argument,
    Claim,
    JudgeDecision,
    RebuttalRecord,
    RiskAssessment,
)
from database.repository import Repository
from tools.validation_tools import (
    enforce_risk_veto,
    get_decision_policy,
    get_validated_arguments,
    validate_all_citations,
)


class JudgeAgent:
    """Judge Agent evaluates Bull and Bear arguments and renders a final recommendation.

    Strict rules:
    1. May ONLY use evidence IDs already present in the evidence ledger and debate submissions.
    2. Overridden to HOLD if Risk Agent triggers a Veto.
    Invokes real tools: get_validated_arguments, validate_all_citations, get_decision_policy, enforce_risk_veto.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter):
        self.repo = repo
        self.adapter = adapter
        self.agent_name = "JudgeAgent"

    def execute(
        self,
        run_id: str,
        bull_arg: Argument,
        bear_arg: Argument,
        rebuttals: List[RebuttalRecord],
        risk_assessment: RiskAssessment,
    ) -> JudgeDecision:
        tool_calls: List[str] = []

        val_args = get_validated_arguments(
            run_id=run_id,
            bull_arg=bull_arg,
            bear_arg=bear_arg,
            rebuttals=rebuttals,
            repo=self.repo,
        )
        tool_calls.append("get_validated_arguments")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_validated_arguments",
            payload={"bull_claims": len(bull_arg.claims), "bear_claims": len(bear_arg.claims)},
        )

        all_claims = bull_arg.claims + bear_arg.claims
        citation_check = validate_all_citations(run_id, all_claims, self.repo)
        tool_calls.append("validate_all_citations")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.validate_all_citations",
            payload={
                "is_valid": citation_check["is_valid"],
                "citation_validity_ratio": citation_check["citation_validity_ratio"],
                "uncited_claims": citation_check["uncited_claims"],
            },
        )

        policy = get_decision_policy("default_q18")
        tool_calls.append("get_decision_policy")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_decision_policy",
            payload={"policy_id": policy["policy_id"]},
        )

        bull_score = len(bull_arg.claims) * 1.5 + len(bull_arg.evidence_ids)
        bear_score = len(bear_arg.claims) * 1.5 + len(bear_arg.evidence_ids)

        has_critical_bear = any(
            any(w in c.text.lower() for w in ["inconsistency", "litigation", "covenant", "decline"])
            for c in bear_arg.claims
        )
        if has_critical_bear:
            bear_score += 3.0

        deciding_reasons: List[Claim] = []
        uncertainties: List[str] = []

        if abs(bull_score - bear_score) <= 1.5 or has_critical_bear:
            provisional_rec = "HOLD"
            deciding_reasons.append(
                Claim(
                    claim_id="JUDGE-01",
                    text=f"Balanced evidence profile: Bull strengths ({bull_arg.strongest_point.text[:120]}) are tempered by Bear vulnerabilities ({bear_arg.strongest_point.text[:120]}).",
                    claim_type="interpretation",
                    evidence_ids=bull_arg.strongest_point.evidence_ids + bear_arg.strongest_point.evidence_ids,
                )
            )
        elif bull_score > bear_score:
            provisional_rec = "BUY"
            deciding_reasons.append(
                Claim(
                    claim_id="JUDGE-01",
                    text=f"Compelling fundamental upside substantiated by revenue/margin data: {bull_arg.strongest_point.text}",
                    claim_type="interpretation",
                    evidence_ids=bull_arg.strongest_point.evidence_ids,
                )
            )
            deciding_reasons.append(
                Claim(
                    claim_id="JUDGE-02",
                    text=f"Bear concerns are deemed operational rather than structural: {bear_arg.counterpoints[0] if bear_arg.counterpoints else 'Manageable risks'}.",
                    claim_type="interpretation",
                    evidence_ids=bull_arg.evidence_ids[:2],
                )
            )
        else:
            provisional_rec = "AVOID"
            deciding_reasons.append(
                Claim(
                    claim_id="JUDGE-01",
                    text=f"Structural risks and reporting headwinds outweigh growth prospects: {bear_arg.strongest_point.text}",
                    claim_type="interpretation",
                    evidence_ids=bear_arg.strongest_point.evidence_ids,
                )
            )

        provisional_decision = JudgeDecision(
            recommendation=provisional_rec,
            strongest_bull_claim_id=bull_arg.strongest_point.claim_id,
            strongest_bear_claim_id=bear_arg.strongest_point.claim_id,
            deciding_reasons=deciding_reasons,
            uncertainties=bull_arg.uncertainty + bear_arg.uncertainty,
            evidence_ids=list(set(bull_arg.evidence_ids + bear_arg.evidence_ids)),
            provisional_recommendation=provisional_rec,
            veto_applied=False,
            veto_reason=None,
        )

        policy_mode = "academic_assignment"
        run_record = self.repo.get_run(run_id)
        if run_record and run_record.config:
            policy_mode = run_record.config.get("policy_mode", "academic_assignment")

        final_decision = enforce_risk_veto(provisional_decision, risk_assessment, policy_mode=policy_mode)
        tool_calls.append("enforce_risk_veto")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.enforce_risk_veto",
            payload={
                "provisional_rec": provisional_rec,
                "final_rec": final_decision.recommendation,
                "veto_applied": final_decision.veto_applied,
                "veto_reason": final_decision.veto_reason,
            },
        )

        self.repo.save_agent_output(run_id, self.agent_name, "completed", final_decision.model_dump(mode="json"))
        self.repo.append_event(
            run_id=run_id,
            event_type="AGENT_COMPLETED",
            agent_or_tool=self.agent_name,
            payload={
                "status": "completed",
                "final_recommendation": final_decision.recommendation,
                "veto_applied": final_decision.veto_applied,
            },
        )

        return final_decision
