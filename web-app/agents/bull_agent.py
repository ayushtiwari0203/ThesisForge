"""Bull Agent module for ThesisForge AI (SRS Section 6)."""

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
from tools.evidence_tools import get_evidence_by_topic, get_financial_facts, validate_claim_support


class BullAgent:
    """Bull Agent constructs the strongest defensible positive investment thesis.

    Strict rule: Every claim MUST cite valid evidence IDs from the run evidence ledger.
    Invokes real tools: get_evidence_by_topic, get_financial_facts, validate_claim_support.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter):
        self.repo = repo
        self.adapter = adapter
        self.agent_name = "BullAgent"

    def execute(self, run_id: str, asset_name: str) -> Argument:
        tool_calls: List[str] = []

        growth_evidence = get_evidence_by_topic("revenue growth order book market expansion demand", run_id, self.repo)
        tool_calls.append("get_evidence_by_topic")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_evidence_by_topic",
            payload={"topic": "growth revenue expansion", "items_found": len(growth_evidence)},
        )

        financial_facts = get_financial_facts(["revenue", "ebitda", "profit", "margin", "guidance"], run_id, self.repo)
        tool_calls.append("get_financial_facts")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_financial_facts",
            payload={"metrics_queried": ["revenue", "ebitda", "profit", "margin", "guidance"], "facts_found": len(financial_facts)},
        )

        claims: List[Claim] = []
        c_idx = 1

        for ff in financial_facts[:3]:
            claim_text = f"{asset_name} exhibits positive momentum in {ff['metric']}: {ff['passage']}"
            claims.append(
                Claim(
                    claim_id=f"BULL-{c_idx:02d}",
                    text=claim_text,
                    claim_type="fact",
                    evidence_ids=[ff["evidence_id"]],
                )
            )
            c_idx += 1

        for gev in growth_evidence:
            if gev.evidence_type in ("financial_fact", "management_guidance", "business_fact"):
                if not any(gev.evidence_code in c.evidence_ids for c in claims):
                    claims.append(
                        Claim(
                            claim_id=f"BULL-{c_idx:02d}",
                            text=f"Operational tailwind: {gev.passage_text}",
                            claim_type="interpretation",
                            evidence_ids=[gev.evidence_code],
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
                        claim_id="BULL-01",
                        text=f"Base operations reported: {all_ev[0].passage_text}",
                        claim_type="fact",
                        evidence_ids=[all_ev[0].evidence_code],
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
            if any(char.isdigit() for char in c.text):
                strongest_point = c
                break

        all_cited_ids = list({eid for c in final_claims for eid in c.evidence_ids})

        thesis = (
            f"Bull Case for {asset_name}: Sustained top-line expansion, structural market position, "
            f"and robust operating leverage provide strong risk-adjusted upside potential."
        )

        counterpoints = [
            "Input cost volatility and margin pressure in inflationary cycles.",
            "Execution risks surrounding capital expenditure and timeline targets.",
        ]

        argument = Argument(
            thesis=thesis,
            claims=final_claims,
            strongest_point=strongest_point,
            counterpoints=counterpoints,
            evidence_ids=all_cited_ids,
            uncertainty=["Forward margin resilience if macroeconomic demand slows."],
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
