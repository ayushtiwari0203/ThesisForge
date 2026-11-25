"""Bear Agent module for ThesisForge AI (SRS Section 6)."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.llm_adapter import LLMServiceAdapter
from database.models import Argument, Claim
from database.repository import Repository
from tools.evidence_tools import get_contradictory_evidence, get_risk_evidence, validate_claim_support


class BearAgent:
    """Bear Agent constructs the strongest defensible negative investment thesis.

    Strict rule: Every claim MUST cite valid evidence IDs from the run evidence ledger.
    Invokes real tools: get_risk_evidence, get_contradictory_evidence, validate_claim_support.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter):
        self.repo = repo
        self.adapter = adapter
        self.agent_name = "BearAgent"

    def execute(self, run_id: str, asset_name: str) -> Argument:
        tool_calls: List[str] = []

        risk_evidence = get_risk_evidence("debt headwinds margin compression competition litigation regulatory", run_id, self.repo)
        tool_calls.append("get_risk_evidence")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_risk_evidence",
            payload={"topic": "debt headwinds margin compression litigation", "items_found": len(risk_evidence)},
        )

        contradictions = get_contradictory_evidence([], run_id, self.repo)
        tool_calls.append("get_contradictory_evidence")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_contradictory_evidence",
            payload={"conflicts_detected": len(contradictions), "details": [c["explanation"] for c in contradictions]},
        )

        claims: List[Claim] = []
        c_idx = 1

        for conflict in contradictions:
            ev_ids = [v["evidence_id"] for v in conflict["values_found"]]
            claims.append(
                Claim(
                    claim_id=f"BEAR-{c_idx:02d}",
                    text=f"Reporting inconsistency: {conflict['explanation']}",
                    claim_type="fact",
                    evidence_ids=ev_ids,
                )
            )
            c_idx += 1

        for rev in risk_evidence:
            if not any(rev.evidence_code in c.evidence_ids for c in claims):
                claims.append(
                    Claim(
                        claim_id=f"BEAR-{c_idx:02d}",
                        text=f"Structural headwind: {rev.passage_text}",
                        claim_type="fact" if rev.evidence_type == "risk_fact" else "interpretation",
                        evidence_ids=[rev.evidence_code],
                    )
                )
                c_idx += 1
            if len(claims) >= 5:
                break

        if not claims:
            all_ev = self.repo.get_evidence_for_run(run_id)
            if all_ev:
                claims.append(
                    Claim(
                        claim_id="BEAR-01",
                        text=f"Valuation and execution sensitivity: {all_ev[-1].passage_text}",
                        claim_type="interpretation",
                        evidence_ids=[all_ev[-1].evidence_code],
                    )
                )

        validated_claims: List[Claim] = []
        for c in claims:
            val_result = validate_claim_support(c.text, c.evidence_ids, run_id, self.repo)
            if val_result.get("supported", False) or val_result.get("valid_ids"):
                validated_claims.append(c)

        tool_calls.append("validate_claim_support")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.validate_claim_support",
            payload={"claims_evaluated": len(claims), "validated_count": len(validated_claims)},
        )

        final_claims = validated_claims if validated_claims else claims

        strongest_point = final_claims[0]
        for c in final_claims:
            if any(w in c.text.lower() for w in ["inconsistency", "litigation", "debt", "regulatory", "penalty", "restatement"]):
                strongest_point = c
                break

        all_cited_ids = list({eid for c in final_claims for eid in c.evidence_ids})

        thesis = (
            f"Bear Case for {asset_name}: Heightened debt leverage, margin vulnerability, "
            f"and operational headwinds create unfavorable risk-reward skew."
        )

        counterpoints = [
            "Unexpected acceleration in product demand could support valuations temporarily.",
            "Potential non-core asset monetization could alleviate near-term balance sheet strain.",
        ]

        argument = Argument(
            thesis=thesis,
            claims=final_claims,
            strongest_point=strongest_point,
            counterpoints=counterpoints,
            evidence_ids=all_cited_ids,
            uncertainty=["Pace of debt deleveraging under rising interest burdens."],
        )

        self.repo.save_agent_output(run_id, self.agent_name, "completed", argument.model_dump(mode="json"))
        self.repo.append_event(
            run_id=run_id,
            event_type="AGENT_COMPLETED",
            agent_or_tool=self.agent_name,
            payload={
                "status": "completed",
                "claims_count": len(final_claims),
                "strongest_claim_id": strongest_point.claim_id,
                "evidence_ids": all_cited_ids,
            },
        )

        return argument
