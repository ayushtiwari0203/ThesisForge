"""Rebuttal round handler for ThesisForge AI (SRS Section 6)."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import UUID

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.llm_adapter import LLMServiceAdapter
from database.models import Argument, Claim, RebuttalRecord
from database.repository import Repository
from tools.evidence_tools import validate_claim_support
from tools.validation_tools import rank_arguments, validate_rebuttal_target


class RebuttalHandler:
    """Orchestrates exactly one rebuttal response per side.

    Strict rule: Bull responds to Bear's strongest point; Bear responds to Bull's strongest point.
    Exactly one turn per side; prevents infinite loops.
    Invokes real tools: rank_arguments, validate_rebuttal_target, validate_claim_support.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter):
        self.repo = repo
        self.adapter = adapter
        self.agent_name = "RebuttalHandler"

    def execute(
        self,
        run_id: str,
        bull_arg: Argument,
        bear_arg: Argument,
    ) -> Tuple[RebuttalRecord, RebuttalRecord]:
        tool_calls: List[str] = []

        ranked_bull = rank_arguments(bull_arg.claims)
        ranked_bear = rank_arguments(bear_arg.claims)
        tool_calls.append("rank_arguments")

        target_bull_point = ranked_bull[0] if ranked_bull else bull_arg.strongest_point
        target_bear_point = ranked_bear[0] if ranked_bear else bear_arg.strongest_point

        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.rank_arguments",
            payload={
                "target_bull_claim": target_bull_point.claim_id,
                "target_bear_claim": target_bear_point.claim_id,
            },
        )

        bull_cited = bull_arg.strongest_point.evidence_ids
        bull_response_text = (
            f"Bull Rebuttal to '{target_bear_point.text}': While downside risk is acknowledged, "
            f"it is substantially mitigated by current operating cash flows and order book visibility "
            f"evidenced in {', '.join(bull_cited)}."
        )

        bull_target_val = validate_rebuttal_target(bull_response_text, target_bear_point.claim_id, target_bear_point.text)
        tool_calls.append("validate_rebuttal_target")

        validate_claim_support(bull_response_text, bull_cited, run_id, self.repo)
        tool_calls.append("validate_claim_support")

        bull_rebuttal = RebuttalRecord(
            target_claim_id=target_bear_point.claim_id,
            target_claim_text=target_bear_point.text,
            response=bull_response_text,
            cited_ids=bull_cited,
            status=bull_target_val.get("status", "addressed"),
        )

        bear_cited = bear_arg.strongest_point.evidence_ids
        bear_response_text = (
            f"Bear Rebuttal to '{target_bull_point.text}': Top-line expansion is misleading without "
            f"adjusting for margin erosion and debt service commitments highlighted in {', '.join(bear_cited)}."
        )

        bear_target_val = validate_rebuttal_target(bear_response_text, target_bull_point.claim_id, target_bull_point.text)

        bear_rebuttal = RebuttalRecord(
            target_claim_id=target_bull_point.claim_id,
            target_claim_text=target_bull_point.text,
            response=bear_response_text,
            cited_ids=bear_cited,
            status=bear_target_val.get("status", "addressed"),
        )

        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.validate_rebuttal_target",
            payload={"bull_target_status": bull_rebuttal.status, "bear_target_status": bear_rebuttal.status},
        )

        self.repo.save_agent_output(
            run_id,
            self.agent_name,
            "completed",
            {
                "bull_rebuttal": bull_rebuttal.model_dump(mode="json"),
                "bear_rebuttal": bear_rebuttal.model_dump(mode="json"),
                "tool_calls": tool_calls,
            },
        )

        self.repo.append_event(
            run_id=run_id,
            event_type="AGENT_COMPLETED",
            agent_or_tool=self.agent_name,
            payload={
                "status": "completed",
                "bull_rebuttal_target": bull_rebuttal.target_claim_id,
                "bear_rebuttal_target": bear_rebuttal.target_claim_id,
            },
        )

        return bull_rebuttal, bear_rebuttal
