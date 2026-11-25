"""Risk Agent module for ThesisForge AI (SRS Section 6 & Group-of-3 add-on)."""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.llm_adapter import LLMServiceAdapter
from database.models import RiskAssessment
from database.repository import Repository
from tools.risk_tools import calculate_risk_score, check_required_evidence, check_risk_thresholds


class RiskAgent:
    """Risk Agent independently audits risk disclosures and enforces a strict safety veto.

    SRS Section 2.2 requirement:
    "Risk Agent with one veto that can force HOLD when a stated risk threshold is crossed, overriding Judge."
    Invokes real tools: calculate_risk_score, check_required_evidence, check_risk_thresholds.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter, threshold: float = 0.65):
        self.repo = repo
        self.adapter = adapter
        self.threshold = float(os.getenv("RISK_VETO_THRESHOLD", str(threshold)))
        self.agent_name = "RiskAgent"

    def execute(self, run_id: str, asset_id: str) -> RiskAssessment:
        tool_calls: List[str] = []

        req_check = check_required_evidence(asset_id=asset_id, run_id=run_id, repo=self.repo)
        tool_calls.append("check_required_evidence")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.check_required_evidence",
            payload={"all_present": req_check["all_present"], "missing": req_check["missing_categories"]},
        )

        evidence_items = self.repo.get_evidence_for_run(run_id)
        facts = [
            {"passage_text": ev.passage_text, "evidence_code": ev.evidence_code, "evidence_type": ev.evidence_type}
            for ev in evidence_items
        ]

        risk_score_result = calculate_risk_score(facts)
        tool_calls.append("calculate_risk_score")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.calculate_risk_score",
            payload={
                "calculated_score": risk_score_result["score"],
                "flags": risk_score_result["flags"],
                "evidence_ids": risk_score_result["evidence_ids"],
            },
        )

        flags = list(risk_score_result["flags"])
        calc_score = risk_score_result["score"]
        if not req_check["all_present"]:
            flags.append("MISSING_MANDATORY_DISCLOSURES")
            calc_score = min(round(calc_score + 0.25, 3), 1.0)

        # Incorporate empirical market risk (volatility from structured OHLCV)
        asset = self.repo.get_asset(asset_id)
        if asset:
            try:
                from tools.market_data_tools import compute_quantitative_market_structure
                mkt_data = compute_quantitative_market_structure(asset.symbol, self.repo)
                vol = mkt_data.get("indicators", {}).get("volatility_annualized")
                if vol is not None and vol > 45.0:
                    flags.append("ELEVATED_MARKET_VOLATILITY")
                    calc_score = min(round(calc_score + 0.10, 3), 1.0)
            except Exception:
                pass

        threshold_eval = check_risk_thresholds(
            risk_score=calc_score,
            flags=flags,
            policy_threshold=self.threshold,
        )
        tool_calls.append("check_risk_thresholds")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.check_risk_thresholds",
            payload={
                "veto": threshold_eval["veto"],
                "threshold": self.threshold,
                "reasons": threshold_eval["reasons"],
            },
        )

        assessment = RiskAssessment(
            score=calc_score,
            threshold=self.threshold,
            veto=threshold_eval["veto"],
            reasons=threshold_eval["reasons"],
            evidence_ids=risk_score_result["evidence_ids"],
            flags=flags,
        )

        self.repo.save_agent_output(run_id, self.agent_name, "completed", assessment.model_dump(mode="json"))
        self.repo.append_event(
            run_id=run_id,
            event_type="AGENT_COMPLETED",
            agent_or_tool=self.agent_name,
            payload={
                "status": "completed",
                "score": assessment.score,
                "veto_triggered": assessment.veto,
                "flags_count": len(flags),
            },
        )

        return assessment
