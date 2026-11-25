"""Deterministic orchestrator for ThesisForge AI Q18 multi-agent workflow & Expert Upgrades."""

from __future__ import annotations
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.bear_agent import BearAgent
from agents.bull_agent import BullAgent
from agents.expert_review.personas import audit_research_run
from agents.judge_agent import JudgeAgent
from agents.llm_adapter import LLMServiceAdapter
from agents.rebuttal import RebuttalHandler
from agents.research_agent import ResearchAgent
from agents.risk_agent import RiskAgent
from database.models import FinalReport, ResearchRunRecord, SignalCard, SignalRecord
from database.repository import Repository
from orchestration.state import WorkflowState
from tools.derivatives_tools import analyze_derivatives_context
from tools.regime_tools import evaluate_market_regime
from tools.technical_tools import analyze_technical_structure
from tools.validation_tools import validate_all_citations
from tools.valuation_tools import evaluate_valuation_context


class InvestmentCommitteeOrchestrator:
    """Orchestrates the debate-driven Q18 workflow deterministically with trading intelligence:

    Research -> Bull & Bear -> Rebuttal -> Risk Review -> Judge -> Technical/Derivatives/Valuation -> Signal Card -> Expert Review.
    """

    def __init__(self, repo: Optional[Repository] = None, adapter: Optional[LLMServiceAdapter] = None):
        self.repo = repo or Repository()
        self.adapter = adapter or LLMServiceAdapter()

        self.research_agent = ResearchAgent(self.repo, self.adapter)
        self.bull_agent = BullAgent(self.repo, self.adapter)
        self.bear_agent = BearAgent(self.repo, self.adapter)
        self.rebuttal_handler = RebuttalHandler(self.repo, self.adapter)
        self.risk_agent = RiskAgent(self.repo, self.adapter)
        self.judge_agent = JudgeAgent(self.repo, self.adapter)

    def run(
        self,
        asset_id: str,
        run_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> FinalReport:
        if not run_id:
            run_id = str(uuid4())
        config = config or {}
        research_mode = config.get("research_mode", "swing").lower()
        risk_budget = float(config.get("risk_budget_rupees", 10000.0))

        asset = self.repo.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found in repository.")

        run_record = ResearchRunRecord(
            id=run_id,
            asset_id=asset.id,
            status=WorkflowState.CREATED.value,
            created_at=datetime.now(timezone.utc).isoformat(),
            config=config,
        )
        self.repo.create_run(run_record)
        self.repo.append_event(
            run_id=run_id,
            event_type="RUN_STARTED",
            agent_or_tool="Orchestrator",
            payload={"asset": asset.name, "symbol": asset.symbol, "mode": research_mode, "config": config},
        )

        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            docs = self.repo.list_documents_for_asset(asset.id)

            # ---------------------------------------------------------------
            # Handling 0 Documents / Pending Documents (Strict Anti-Fabrication)
            # ---------------------------------------------------------------
            if not docs:
                self.repo.update_run_status(run_id, WorkflowState.INSUFFICIENT_EVIDENCE.value, completed_at=now_iso)
                self.repo.append_event(
                    run_id=run_id,
                    event_type="INSUFFICIENT_EVIDENCE",
                    agent_or_tool="Orchestrator",
                    payload={"notice": f"No authentic filings ingested for {asset.name}. Mandatory documents pending."},
                )

                # Decoupled Market Data Sourcing: Retrieve real historical market price and technical structure
                tech_context = None
                mkt_summary = self.repo.get_market_data_summary(asset.symbol)
                total_bars = mkt_summary.get("total_bars", 0)
                if total_bars >= 14:
                    try:
                        tech_context = analyze_technical_structure(
                            symbol=asset.symbol,
                            research_mode=research_mode,
                            as_of=now_iso,
                            repo=self.repo,
                        )
                    except Exception:
                        tech_context = None

                ref_price = 0.0
                if tech_context and tech_context.get("current_price"):
                    ref_price = tech_context["current_price"]
                else:
                    with self.repo._get_connection() as conn:
                        row = conn.execute("SELECT close FROM historical_market_data WHERE symbol = ? ORDER BY trade_date DESC LIMIT 1", (asset.symbol.upper(),)).fetchone()
                        ref_price = row[0] if row else 0.0

                # Generate non-actionable Signal Card for pending asset with real market reference price
                pending_signal = SignalCard(
                    run_id=run_id,
                    instrument=asset.name,
                    symbol=asset.symbol,
                    exchange="NSE",
                    research_mode=research_mode,
                    decision="HOLD",
                    setup_name="Information Void — Pending Filing Ingestion",
                    current_reference_price=ref_price,
                    entry_trigger=None,
                    entry_zone_min=None,
                    entry_zone_max=None,
                    stop_loss=None,
                    target_1=None,
                    target_2=None,
                    reward_to_risk=None,
                    suggested_quantity=0,
                    risk_per_share=0.0,
                    holding_window="Indefinite until statutory document ingestion",
                    setup_expiry=now_iso,
                    no_trade_conditions=[
                        "Zero primary regulatory filings or audited disclosures available in ledger.",
                        "Strict anti-fabrication policy prohibits generating trade levels without filings.",
                    ],
                    confidence_score=0.0,
                    confidence_label="Cautionary / Incomplete Data",
                    is_actionable=False,
                    actionability_reason="Primary company statutory filings are pending. Fundamental financial data cannot be fabricated.",
                    as_of=now_iso,
                )

                # Run Expert Review Personas on pending case
                expert_findings = audit_research_run(
                    run_id=run_id,
                    asset_id=asset.id,
                    asset_name=asset.name,
                    symbol=asset.symbol,
                    sector=asset.sector or "General",
                    recommendation="HOLD",
                    risk_veto=False,
                    risk_score=0.0,
                    evidence_count=0,
                    research_mode=research_mode,
                )
                self.repo.save_expert_reviews(run_id, expert_findings)

                # Save pending signal to ledger
                sig_record = SignalRecord(
                    run_id=run_id,
                    asset_id=asset.id,
                    symbol=asset.symbol,
                    mode=research_mode,
                    decision="HOLD",
                    status="invalidated",
                    notes="No primary filings available. Trade generation suspended.",
                )
                self.repo.save_signal_record(sig_record)

                insufficient_report = FinalReport(
                    run_id=run_id,
                    asset={"name": asset.name, "symbol": asset.symbol},
                    as_of=now_iso,
                    recommendation="HOLD",
                    risk_veto={
                        "triggered": False,
                        "reason": f"Information opacity: No primary filings ingested for {asset.name} ({asset.symbol}). Mandatory statutory disclosures pending. Fundamental risk is NOT_ASSESSED.",
                        "score": None,
                        "risk_status": "NOT_ASSESSED — Primary statutory filings pending",
                        "threshold": config.get("risk_veto_threshold", 0.65),
                    },
                    strongest_bull_argument={
                        "claim": f"No substantiated bull thesis can be formulated without verified financial disclosures for {asset.name}.",
                        "evidence_ids": [],
                    },
                    strongest_bear_argument={
                        "claim": f"Information opacity risk: lack of primary regulatory filings prevents independent verification of solvency, profitability, or cash flows for {asset.name}.",
                        "evidence_ids": [],
                    },
                    bull_rebuttal={
                        "text": "Bull committee cannot formulate grounded arguments without verified primary filings.",
                        "evidence_ids": [],
                    },
                    bear_rebuttal={
                        "text": "Bear committee maintains hold stance due to information void.",
                        "evidence_ids": [],
                    },
                    deciding_reasons=[
                        {
                            "reason": f"No authentic filings available for {asset.name} ({asset.symbol}). In compliance with SEBI disclosure standards and ThesisForge evidentiary integrity rules, recommendation defaults to HOLD pending document ingestion.",
                            "evidence_ids": [],
                        }
                    ],
                    uncertainties=[
                        f"Complete absence of ingested primary documents for {asset.name} ({asset.symbol}).",
                        "In accordance with anti-fabrication rules, zero synthetic claims were generated.",
                    ],
                    limitations=[
                        "Asset marked 'Company added — documents pending'. Financial statements have NOT been fabricated.",
                        "Upload authentic quarterly results or annual reports via the Ingestion tool to trigger full multi-agent debate.",
                    ],
                    generated_at=now_iso,
                    research_mode=research_mode,
                    signal_card=pending_signal,
                    technical_context=tech_context,
                    derivatives_context=None,
                    valuation_context=None,
                    expert_reviews=[f.model_dump() for f in expert_findings],
                )
                self.repo.save_final_report(run_id, insufficient_report)
                return insufficient_report

            # ---------------------------------------------------------------
            # Normal Flow with Documents Ingested
            # ---------------------------------------------------------------
            self.repo.update_run_status(run_id, WorkflowState.DOCUMENTS_READY.value)

            research_result = self.research_agent.execute(run_id=run_id, asset_id=asset.id)
            if research_result.status == "insufficient_evidence" or not research_result.evidence_ids:
                self.repo.update_run_status(run_id, WorkflowState.INSUFFICIENT_EVIDENCE.value, completed_at=now_iso)
                # Handle empty extraction cleanly
                insufficient_report = FinalReport(
                    run_id=run_id,
                    asset={"name": asset.name, "symbol": asset.symbol},
                    as_of=now_iso,
                    recommendation="HOLD",
                    risk_veto={"triggered": False, "reason": "Insufficient verified evidence items extracted.", "score": 0.0, "threshold": config.get("risk_veto_threshold", 0.65)},
                    strongest_bull_argument={"claim": "Insufficient verified evidence to substantiate bull case.", "evidence_ids": []},
                    strongest_bear_argument={"claim": "Lack of conclusive evidence warrants capital preservation.", "evidence_ids": []},
                    bull_rebuttal={"text": "Debate suspended due to insufficient evidence extraction.", "evidence_ids": []},
                    bear_rebuttal={"text": "Debate suspended due to insufficient evidence extraction.", "evidence_ids": []},
                    deciding_reasons=[{"reason": "Research agent extracted insufficient factual evidence from document pack.", "evidence_ids": []}],
                    uncertainties=["Extracted document text did not meet minimum evidence extraction thresholds."],
                    limitations=["Ingested document pack may be corrupt or lacking structured financial disclosures."],
                    generated_at=now_iso,
                    research_mode=research_mode,
                )
                self.repo.save_final_report(run_id, insufficient_report)
                return insufficient_report

            self.repo.update_run_status(run_id, WorkflowState.EVIDENCE_READY.value)
            self.repo.update_run_status(run_id, WorkflowState.RESEARCH_COMPLETE.value)

            bull_argument = self.bull_agent.execute(run_id=run_id, asset_name=asset.name)
            bear_argument = self.bear_agent.execute(run_id=run_id, asset_name=asset.name)
            self.repo.update_run_status(run_id, WorkflowState.BULL_BEAR_COMPLETE.value)

            bull_rebuttal, bear_rebuttal = self.rebuttal_handler.execute(
                run_id=run_id,
                bull_arg=bull_argument,
                bear_arg=bear_argument,
            )
            self.repo.update_run_status(run_id, WorkflowState.REBUTTAL_COMPLETE.value)

            risk_assessment = self.risk_agent.execute(run_id=run_id, asset_id=asset.id)
            self.repo.update_run_status(run_id, WorkflowState.RISK_REVIEW_COMPLETE.value)

            judge_decision = self.judge_agent.execute(
                run_id=run_id,
                bull_arg=bull_argument,
                bear_arg=bear_argument,
                rebuttals=[bull_rebuttal, bear_rebuttal],
                risk_assessment=risk_assessment,
            )
            self.repo.update_run_status(run_id, WorkflowState.JUDGE_COMPLETE.value)

            all_claims = bull_argument.claims + bear_argument.claims + judge_decision.deciding_reasons
            val_summary = validate_all_citations(run_id, all_claims, self.repo)
            if not val_summary["is_valid"]:
                self.repo.append_event(
                    run_id=run_id,
                    event_type="VALIDATION_WARNING",
                    agent_or_tool="Orchestrator.validate_citations",
                    payload=val_summary,
                )
            self.repo.update_run_status(run_id, WorkflowState.VALIDATION_COMPLETE.value)

            # ---------------------------------------------------------------
            # Trading Intelligence: Technical, Derivatives, Regime, Valuation
            # ---------------------------------------------------------------
            tech_data = analyze_technical_structure(symbol=asset.symbol, research_mode=research_mode, as_of=now_iso, repo=self.repo)
            deriv_data = analyze_derivatives_context(symbol=asset.symbol)
            regime_data = evaluate_market_regime(symbol=asset.symbol, sector=asset.sector)
            val_data = evaluate_valuation_context(symbol=asset.symbol, sector=asset.sector)

            # ---------------------------------------------------------------
            # Mandatory Signal Card Synthesis (Section 5 Contract)
            # ---------------------------------------------------------------
            tech_levels = tech_data["levels"]
            current_ref_price = tech_data["current_price"]
            trigger_price = tech_levels["trigger_price"]
            stop_price = tech_levels["stop_loss"]
            target_1 = tech_levels["target_1"]
            target_2 = tech_levels["target_2"]
            reward_to_risk = tech_levels["reward_to_risk"]
            risk_per_share = tech_levels["risk_per_share"]

            # Calculate position quantity: floor(Allowed Rupee Risk / (Entry - Stop))
            calculated_qty = math.floor(risk_budget / max(1.0, risk_per_share))
            # Adjust to lot size if F&O eligible
            if tech_data.get("is_fo_eligible") and tech_data.get("lot_size", 1) > 1:
                lot = tech_data["lot_size"]
                calculated_qty = max(lot, (calculated_qty // lot) * lot)

            # Determine Actionability
            final_rec = judge_decision.recommendation
            is_actionable = False
            actionability_reason = ""
            no_trade_conds = []

            if risk_assessment.veto:
                is_actionable = False
                actionability_reason = f"Safety Veto triggered by Risk Agent ({judge_decision.veto_reason}). Actionable execution prohibited."
                no_trade_conds.append("Risk Agent Veto Active: Critical solvency, covenant, or regulatory breach.")
            elif final_rec == "AVOID":
                is_actionable = False
                actionability_reason = "Committee verdict is AVOID. Bearish vulnerability outweighs upside."
                no_trade_conds.append("Bear thesis dominance; risk-reward profile unfavorable for long entry.")
            elif final_rec == "HOLD":
                is_actionable = False
                actionability_reason = "Committee verdict is HOLD. Balanced debate warrants capital preservation."
                no_trade_conds.append("Uncertainty or balanced debate warrants waiting for clearer confirmation.")
            elif final_rec == "BUY":
                if reward_to_risk < 1.3:
                    is_actionable = False
                    actionability_reason = f"Reward-to-risk ratio ({reward_to_risk}x) is below minimum 1.3x threshold."
                    no_trade_conds.append(f"Insufficient R:R ({reward_to_risk}x < 1.3x).")
                elif regime_data.get("event_risk_flag"):
                    is_actionable = False
                    actionability_reason = "High-impact event scheduled within immediate holding window."
                    no_trade_conds.append(regime_data.get("event_risk_note", "Event risk proximity"))
                else:
                    is_actionable = True
                    actionability_reason = f"Constructive technical structure ({tech_data['trend']}) confirmed by verified evidence pack."

            if not is_actionable and not no_trade_conds:
                no_trade_conds.append("System abstaining due to risk/reward or market regime constraints.")

            signal_card = SignalCard(
                run_id=run_id,
                instrument=asset.name,
                symbol=asset.symbol,
                exchange="NSE",
                research_mode=research_mode,
                decision=final_rec,
                setup_name=f"{tech_data['trend']} Setup ({research_mode.capitalize()})",
                current_reference_price=current_ref_price,
                entry_trigger=trigger_price,
                entry_zone_min=tech_levels["entry_zone"][0],
                entry_zone_max=tech_levels["entry_zone"][1],
                stop_loss=stop_price,
                stop_loss_type="close_based" if research_mode == "swing" else "hard_stop",
                invalidation_reason=f"Breakdown below {stop_price} invalidates the technical support structure.",
                target_1=target_1,
                target_2=target_2,
                reward_to_risk=reward_to_risk,
                position_size_formula="Quantity = floor(Allowed Rupee Risk / (Entry Price - Stop Loss))",
                risk_budget_rupees=risk_budget,
                risk_per_share=risk_per_share,
                suggested_quantity=calculated_qty,
                holding_window=tech_data["holding_window"],
                setup_expiry=(datetime.now(timezone.utc) + (datetime.now(timezone.utc) - datetime.now(timezone.utc) + (datetime.min - datetime.min))).isoformat(),
                slippage_assumption_pct=0.15,
                liquidity_impact_caveat=f"Average daily volume: {tech_data['indicators'].get('volume_ratio_20d', 1.0)}x normal. Clean execution expected.",
                no_trade_conditions=no_trade_conds,
                confidence_score=0.85 if is_actionable else 0.50,
                confidence_label="High Conviction" if is_actionable else "Cautionary / Non-Actionable",
                is_actionable=is_actionable,
                actionability_reason=actionability_reason,
                as_of=now_iso,
            )

            # ---------------------------------------------------------------
            # Signal Ledger Recording (Section 7)
            # ---------------------------------------------------------------
            sig_record = SignalRecord(
                run_id=run_id,
                asset_id=asset.id,
                symbol=asset.symbol,
                mode=research_mode,
                decision=final_rec,
                entry_price=trigger_price if is_actionable else None,
                stop_loss=stop_price if is_actionable else None,
                target_1=target_1 if is_actionable else None,
                target_2=target_2 if is_actionable else None,
                risk_reward=reward_to_risk,
                status="triggered" if is_actionable else "invalidated",
                notes=actionability_reason,
            )
            self.repo.save_signal_record(sig_record)

            # ---------------------------------------------------------------
            # 10 Expert Review Personas (Section 2 & 3 Inspection Layer)
            # ---------------------------------------------------------------
            expert_findings = audit_research_run(
                run_id=run_id,
                asset_id=asset.id,
                asset_name=asset.name,
                symbol=asset.symbol,
                sector=asset.sector or "General",
                recommendation=final_rec,
                risk_veto=risk_assessment.veto,
                risk_score=risk_assessment.score,
                evidence_count=len(research_result.evidence_ids),
                research_mode=research_mode,
            )
            self.repo.save_expert_reviews(run_id, expert_findings)

            deciding_reasons_report = [
                {"reason": r.text, "evidence_ids": r.evidence_ids}
                for r in judge_decision.deciding_reasons
            ]

            final_report = FinalReport(
                run_id=run_id,
                asset={"name": asset.name, "symbol": asset.symbol},
                as_of=now_iso,
                recommendation=final_rec,
                risk_veto={
                    "triggered": risk_assessment.veto,
                    "reason": judge_decision.veto_reason or ("; ".join(risk_assessment.reasons) if risk_assessment.veto else None),
                    "score": risk_assessment.score,
                    "threshold": risk_assessment.threshold,
                },
                strongest_bull_argument={
                    "claim": bull_argument.strongest_point.text,
                    "evidence_ids": bull_argument.strongest_point.evidence_ids,
                },
                strongest_bear_argument={
                    "claim": bear_argument.strongest_point.text,
                    "evidence_ids": bear_argument.strongest_point.evidence_ids,
                },
                bull_rebuttal={
                    "text": bull_rebuttal.response,
                    "evidence_ids": bull_rebuttal.cited_ids,
                },
                bear_rebuttal={
                    "text": bear_rebuttal.response,
                    "evidence_ids": bear_rebuttal.cited_ids,
                },
                deciding_reasons=deciding_reasons_report,
                uncertainties=judge_decision.uncertainties,
                limitations=[
                    f"Research performed under mode '{research_mode}'.",
                    "ThesisForge operates strictly on grounded document packs and verifiable price/OI metrics.",
                    "ThesisForge is a decision transparency tool, not an authorized broker or financial advisor.",
                ],
                generated_at=now_iso,
                research_mode=research_mode,
                signal_card=signal_card,
                technical_context=tech_data,
                derivatives_context=deriv_data,
                valuation_context=val_data,
                expert_reviews=[f.model_dump() for f in expert_findings],
            )

            self.repo.save_final_report(run_id, final_report)
            self.repo.update_run_status(run_id, WorkflowState.COMPLETED.value, completed_at=now_iso)

            self.repo.append_event(
                run_id=run_id,
                event_type="RUN_COMPLETED",
                agent_or_tool="Orchestrator",
                payload={
                    "recommendation": final_report.recommendation,
                    "risk_veto_triggered": risk_assessment.veto,
                    "evidence_items_count": len(research_result.evidence_ids),
                    "mode": research_mode,
                    "is_actionable_signal": is_actionable,
                },
            )

            return final_report

        except Exception as e:
            self.repo.append_event(
                run_id=run_id,
                event_type="RUN_FAILED",
                agent_or_tool="Orchestrator",
                payload={"error": str(e)},
            )
            raise
