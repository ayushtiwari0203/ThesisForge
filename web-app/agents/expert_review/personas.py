"""Expert Review Layer: 10 Methodology-Inspired Review Personas (Simulated Lenses).

IMPORTANT GOVERNANCE NOTICE:
These review personas are simulated analytical quality-control lenses inspired by public
methodologies and documented investing principles. They DO NOT represent personal endorsements,
testing, or direct participation by the named market professionals. Output is strictly for
internal quality review and risk audit.
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PersonaReviewFinding(BaseModel):
    """Structured audit finding produced by a methodology-inspired review persona."""
    persona_id: str
    persona_name: str
    lens_title: str
    observed_issue: str
    evidence_in_prototype: str
    suggested_change: str
    affected_module: str
    expected_user_value: Literal["HIGH", "MEDIUM", "LOW"]
    data_dependency: str
    regression_risk: Literal["LOW", "MEDIUM", "HIGH"]
    implementation_effort: Literal["LOW", "MEDIUM", "HIGH"]
    priority: Literal["P0", "P1", "P2", "REJECTED"]
    acceptance_test: str
    confidence: float
    status: Literal["APPROVED", "REJECTED", "DEFERRED"] = "APPROVED"
    rejection_reason: Optional[str] = None
    checklist_items: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Specification Definition for the 10 Review Personas
# ---------------------------------------------------------------------------

PERSONA_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "persona_id": "vijay_kedia",
        "persona_name": "Vijay Kedia (Simulation Lens)",
        "lens_title": "Growth, Business Quality & Scalable Opportunity",
        "review_question": "Does the business possess a credible growth runway, improving unit economics, competent promoter governance, and scalable moat?",
        "suggested_change": "Add a Growth-Quality Checklist for swing candidates: 3-year sales/profit trend, ROCE/ROE trajectory, working capital cash-flow conversion, promoter pledging, and customer/supplier concentration.",
        "affected_module": "web-app/tools/risk_tools.py, web-app/database/models.py",
        "expected_user_value": "HIGH",
        "data_dependency": "Annual and quarterly statutory balance sheet and P&L disclosures.",
        "regression_risk": "LOW",
        "implementation_effort": "MEDIUM",
        "priority": "P1",
        "acceptance_test": "Checklist produces verifiable scores for indexed companies and flags missing metrics without breaking core Bull/Bear arguments.",
        "guardrail": "Do not use long-term growth traits as a hard gate for intraday trades. Flag missing or stale financials honestly.",
    },
    {
        "persona_id": "raamdeo_agrawal",
        "persona_name": "Raamdeo Agrawal (Simulation Lens)",
        "lens_title": "Quality, Valuation & Disciplined Fundamentals (QGLP)",
        "review_question": "Are return ratios durable, is growth already fully discounted in valuation multiples, and what is the margin of safety?",
        "suggested_change": "Introduce a Valuation Context Panel: Trailing PE, PB, and EV/EBITDA ratios with sector-specific applicability, earnings growth consistency, and debt-to-cashflow sanity checks.",
        "affected_module": "web-app/tools/document_tools.py, web-app/database/models.py",
        "expected_user_value": "HIGH",
        "data_dependency": "Reported market cap, enterprise value, and audited trailing operating profits.",
        "regression_risk": "LOW",
        "implementation_effort": "MEDIUM",
        "priority": "P1",
        "acceptance_test": "Multiples are displayed only for sectors where meaningful (e.g. EV/EBITDA for Infra/Energy, PB for Banks) with clear peer/historical caveats.",
        "guardrail": "Never infer intrinsic value from a single ratio. Sector-specific metric applicability must be explicit.",
    },
    {
        "persona_id": "porinju_veliyath",
        "persona_name": "Porinju Veliyath (Simulation Lens)",
        "lens_title": "Contrarian & Under-Followed Opportunity",
        "review_question": "Why is the market skeptical or overlooking the company, what is the specific operational catalyst, and what is the downside trigger?",
        "suggested_change": "Add a Contrarian Thesis Field to Bear/Bull debate: Market's current primary concern, verifiable evidence supporting an alternative turnaround thesis, upcoming operational catalyst, and governance downside trigger.",
        "affected_module": "web-app/agents/bull_agent.py, web-app/agents/bear_agent.py",
        "expected_user_value": "MEDIUM",
        "data_dependency": "Disclosed management commentary, capex plans, debt restructuring notes.",
        "regression_risk": "LOW",
        "implementation_effort": "LOW",
        "priority": "P1",
        "acceptance_test": "Bear agent identifies market skepticism; Bull rebuttal surfaces turnaround evidence without overriding risk veto.",
        "guardrail": "Small-cap illiquidity and corporate governance red flags must be prominent. No automatic contrarian BUY recommendations.",
    },
    {
        "persona_id": "basant_maheshwari",
        "persona_name": "Basant Maheshwari (Simulation Lens)",
        "lens_title": "Earnings Acceleration & Growth-Momentum",
        "review_question": "Is earnings growth accelerating sequentially (QoQ and YoY) and supported by relative price strength against the benchmark?",
        "suggested_change": "Add Earnings Acceleration & Relative Strength Trend features: Compare recent quarterly revenue/PAT growth with prior 4 quarters and compare stock returns against Nifty 50 benchmark.",
        "affected_module": "web-app/tools/technical_tools.py, web-app/tools/document_tools.py",
        "expected_user_value": "HIGH",
        "data_dependency": "Sequential quarterly EPS / PAT numbers and benchmark price indices.",
        "regression_risk": "LOW",
        "implementation_effort": "MEDIUM",
        "priority": "P1",
        "acceptance_test": "Computes QoQ and YoY acceleration rates; flags one-off exceptional quarters from durable trends.",
        "guardrail": "Use verified results dates and consistent reporting periods. Avoid extrapolating single-quarter windfalls.",
    },
    {
        "persona_id": "sudarshan_sukhani",
        "persona_name": "Sudarshan Sukhani (Simulation Lens)",
        "lens_title": "Pure Technical Structure & Risk-Defined Setup",
        "review_question": "What is the prevailing trend structure, breakout/breakdown level, support/resistance, volume confirmation, and exact thesis invalidation level?",
        "suggested_change": "Create a deterministic Technical Setup Card: Multi-timeframe trend (Daily/Weekly), EMA 20/50/200, RSI, ATR, VWAP, breakout trigger level, entry zone, hard stop-loss, target 1 & 2, and setup expiry.",
        "affected_module": "web-app/tools/technical_tools.py, web-app/orchestration/workflow.py",
        "expected_user_value": "HIGH",
        "data_dependency": "Timestamped daily and intraday OHLCV time-series.",
        "regression_risk": "LOW",
        "implementation_effort": "HIGH",
        "priority": "P0",
        "acceptance_test": "All indicators are calculated mathematically via unit-tested formulas; zero hallucinated levels; no signal if OHLCV data is stale.",
        "guardrail": "No actionable signal when price data is stale or stop distance makes the trade uneconomic.",
    },
    {
        "persona_id": "kunal_bothra",
        "persona_name": "Kunal Bothra (Simulation Lens)",
        "lens_title": "Actionable Trading Plan & Execution Discipline",
        "review_question": "Can this analytical thesis be translated into an exact, unambiguous trade plan with trigger vs entry zone, initial SL, trailing rules, and position sizing?",
        "suggested_change": "Standardize the Mandatory Signal Card: Research mode (Intraday/Swing), Setup type, Entry Trigger vs Entry Zone, Initial Stop-Loss, Targets (T1/T2), Trailing Stop rule, Risk-Reward ratio, and Position Size formula.",
        "affected_module": "web-app/database/models.py, web-app/backend/routes.py, web-app/frontend/index.html",
        "expected_user_value": "HIGH",
        "data_dependency": "Calculated technical levels, risk budget input (or default 1% equity risk).",
        "regression_risk": "LOW",
        "implementation_effort": "HIGH",
        "priority": "P0",
        "acceptance_test": "Signal Card is persisted with every run; displays exact levels or explicit 'NO TRADE / STALE DATA' condition.",
        "guardrail": "Do not convert commentary into a trade call unless exact trigger and invalidation are defined. Track revision timestamps.",
    },
    {
        "persona_id": "sunil_singhania",
        "persona_name": "Sunil Singhania (Simulation Lens)",
        "lens_title": "Portfolio Construction, Sector Allocation & Diversification",
        "review_question": "Does this recommendation introduce sector concentration or duplicate existing portfolio risk factors?",
        "suggested_change": "Add Sector/Industry Exposure and Correlation Context: Track watchlist sector weightings, flag clustered ideas in correlated industries, and report average daily turnover.",
        "affected_module": "web-app/database/repository.py, web-app/backend/routes.py",
        "expected_user_value": "MEDIUM",
        "data_dependency": "Asset sector metadata, average daily turnover.",
        "regression_risk": "LOW",
        "implementation_effort": "LOW",
        "priority": "P2",
        "acceptance_test": "Returns sector concentration metrics for multi-stock watchlists without implying individual portfolio suitability.",
        "guardrail": "Do not imply personalized portfolio suitability without user portfolio inputs. Keep strictly as research context.",
    },
    {
        "persona_id": "ashish_kacholia",
        "persona_name": "Ashish Kacholia (Simulation Lens)",
        "lens_title": "Emerging Small/Mid-Cap Business Discovery",
        "review_question": "What is the business niche, impact cost/liquidity, promoter pledging, related-party disclosure quality, and cash conversion cycle?",
        "suggested_change": "Add Small/Mid-Cap Diligence Checklist: Market cap category, bid-ask spread/impact cost estimate, promoter pledging %, related-party transaction flags, and CFO-to-EBITDA ratio.",
        "affected_module": "web-app/tools/risk_tools.py",
        "expected_user_value": "MEDIUM",
        "data_dependency": "Shareholding pattern disclosures, annual report related-party tables.",
        "regression_risk": "LOW",
        "implementation_effort": "MEDIUM",
        "priority": "P2",
        "acceptance_test": "Flags promoter pledging > 15% and working capital stretch in Risk Agent review.",
        "guardrail": "Do not equate public shareholding with a recommendation. Apply strict liquidity safeguards.",
    },
    {
        "persona_id": "ramesh_damani",
        "persona_name": "Ramesh Damani (Simulation Lens)",
        "lens_title": "Market Cycles, Patience & Long-Horizon Context",
        "review_question": "Is the investment thesis aligned with a multi-year macro/sector cycle, and does the holding horizon match the fundamental catalyst?",
        "suggested_change": "Add Market-Cycle and Catalyst Context: Classify sector cycle phase (Early / Mid / Late / Recessionary), state expected catalyst timeline, and provide explicit thesis review date.",
        "affected_module": "web-app/database/models.py, web-app/orchestration/workflow.py",
        "expected_user_value": "MEDIUM",
        "data_dependency": "Macro cycle indicators (Interest rates, RBI stance, sector capex cycles).",
        "regression_risk": "LOW",
        "implementation_effort": "LOW",
        "priority": "P2",
        "acceptance_test": "Positional and Swing reports include catalyst timeline and formal review horizon.",
        "guardrail": "Do not let long-horizon narrative override a failed short-term technical invalidation level or Risk Agent veto.",
    },
    {
        "persona_id": "asim_jain",
        "persona_name": "Asim Jain (Simulation Lens)",
        "lens_title": "Data-Driven Equity + Derivatives Defined-Risk Trade Plan",
        "review_question": "Does the trade combine technical trigger with futures/options Open Interest (OI) buildup, clear risk-reward, and explicit no-trade conditions?",
        "suggested_change": "Add Derivatives & Futures OI Analysis Engine: Capture futures OI change vs price change (Long/Short Buildup, Short Covering, Long Unwinding), Put-Call Ratio (PCR), and Max Pain/Call Wall resistance.",
        "affected_module": "web-app/tools/derivatives_tools.py, web-app/database/models.py",
        "expected_user_value": "HIGH",
        "data_dependency": "NSE F&O Bhavcopy or timestamped Futures/Options contract data.",
        "regression_risk": "LOW",
        "implementation_effort": "HIGH",
        "priority": "P1",
        "acceptance_test": "Computes joint price/OI interpretation; labels ambiguous cases; disables derivatives panel cleanly for non-F&O equities.",
        "guardrail": "Never use stale snapshots as live positioning. Display source, exchange timestamp, and delay status clearly.",
    },
]


def audit_research_run(
    run_id: str,
    asset_id: str,
    asset_name: str,
    symbol: str,
    sector: str,
    recommendation: str,
    risk_veto: bool,
    risk_score: float,
    evidence_count: int,
    research_mode: str = "swing",
) -> List[PersonaReviewFinding]:
    """Execute the 10 simulated persona checklists against a research run output."""
    findings: List[PersonaReviewFinding] = []

    for p in PERSONA_DEFINITIONS:
        pid = p["persona_id"]
        observed = ""
        proto_evidence = ""
        checklist: List[Dict[str, Any]] = []

        if pid == "sudarshan_sukhani":
            observed = "Current output is an academic recommendation (BUY/HOLD/AVOID) without actionable technical entry triggers, invalidation levels, or stop-loss."
            proto_evidence = f"Run {run_id} produced {recommendation} without numerical price trigger, stop-loss price, or setup expiration."
            checklist = [
                {"item": "Multi-timeframe trend structure identified", "status": "PENDING_ENHANCEMENT"},
                {"item": "Exact breakout/reversal trigger price defined", "status": "PENDING_ENHANCEMENT"},
                {"item": "Thesis invalidation stop-loss specified", "status": "PENDING_ENHANCEMENT"},
                {"item": "Risk-to-reward ratio >= 1.5x verified", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "kunal_bothra":
            observed = "Lack of a standardized, actionable Trade Signal Card with risk budget sizing formula and holding horizon."
            proto_evidence = f"Deciding reasons cite factual claims but offer no share quantity formula or slippage/liquidity caveats."
            checklist = [
                {"item": "Clear distinction between entry trigger and entry zone", "status": "PENDING_ENHANCEMENT"},
                {"item": "Initial SL and trailing stop mechanism documented", "status": "PENDING_ENHANCEMENT"},
                {"item": "Position size formula: floor(risk / (entry - stop))", "status": "PENDING_ENHANCEMENT"},
                {"item": "Explicit setup expiry timestamp attached", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "asim_jain":
            observed = "No derivatives positioning context (Futures Open Interest buildup, PCR, or strike concentration) for F&O securities."
            proto_evidence = f"Research Agent retrieves document text but does not inspect joint price/OI changes."
            checklist = [
                {"item": "Futures price vs OI classification (Long/Short Buildup)", "status": "PENDING_ENHANCEMENT"},
                {"item": "Put-Call Ratio (PCR) and Call/Put walls evaluated", "status": "PENDING_ENHANCEMENT"},
                {"item": "Non-F&O securities cleanly labeled without fabricated OI", "status": "VERIFIED"},
            ]
        elif pid == "vijay_kedia":
            observed = "Growth durability and ROCE metrics are present in narrative text but lack structured multi-year trend verification."
            proto_evidence = f"Extracted {evidence_count} evidence items; balance sheet metrics embedded in quotes rather than structured scorecard."
            checklist = [
                {"item": "Sales & profit trajectory verified across 3+ periods", "status": "PENDING_ENHANCEMENT"},
                {"item": "ROCE / ROE capital efficiency check", "status": "PENDING_ENHANCEMENT"},
                {"item": "Promoter pledging and governance sanity check", "status": "VERIFIED" if risk_score < 0.5 else "FLAGGED"},
            ]
        elif pid == "raamdeo_agrawal":
            observed = "Valuation multiples (PE, PB, EV/EBITDA) lack peer context and historical band perspective."
            proto_evidence = "Judge decision weighs claims but does not explicitly assess whether growth is already priced into multiples."
            checklist = [
                {"item": "Sector-appropriate valuation multiple applied", "status": "PENDING_ENHANCEMENT"},
                {"item": "Margin of safety evaluated against earnings durability", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "porinju_veliyath":
            observed = "Contrarian turnaround angles and market skepticism drivers are not formally separated from consensus views."
            proto_evidence = "Bear Agent focuses on operational risks; does not explicitly document what market is overly pessimistic about."
            checklist = [
                {"item": "Identified market consensus skepticism/concern", "status": "PENDING_ENHANCEMENT"},
                {"item": "Identified verifiable turnaround catalyst", "status": "PENDING_ENHANCEMENT"},
                {"item": "Liquidity and governance downside triggers prominent", "status": "VERIFIED"},
            ]
        elif pid == "basant_maheshwari":
            observed = "Sequential quarterly earnings acceleration rates (QoQ vs YoY) and relative strength vs benchmark are uncomputed."
            proto_evidence = "Reports single-quarter figures without delta momentum acceleration calculations."
            checklist = [
                {"item": "Sequential QoQ and YoY earnings acceleration calculated", "status": "PENDING_ENHANCEMENT"},
                {"item": "Relative price strength against Nifty 50 computed", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "sunil_singhania":
            observed = "Watchlist and multi-candidate runs lack sector concentration and correlation flags."
            proto_evidence = "Each run is evaluated in isolation without portfolio-level correlation warnings."
            checklist = [
                {"item": "Sector exposure classified", "status": "VERIFIED"},
                {"item": "Clustered industry risk flagged for watchlist", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "ashish_kacholia":
            observed = "Small/Mid-cap due diligence checklist (promoter pledging %, CFO/EBITDA, related-party disclosure) is unformalized."
            proto_evidence = f"Risk Agent checks covenant breaches but does not systematically scorecard working capital conversion."
            checklist = [
                {"item": "Market cap tier and liquidity impact cost estimated", "status": "PENDING_ENHANCEMENT"},
                {"item": "Cash conversion cycle and CFO/EBITDA audited", "status": "PENDING_ENHANCEMENT"},
            ]
        elif pid == "ramesh_damani":
            observed = "Lack of explicit market-cycle phase and catalyst timeline alignment with the selected time horizon."
            proto_evidence = f"Run performed under mode '{research_mode}' without formal catalyst horizon or review date."
            checklist = [
                {"item": "Macro and sector cycle stage identified", "status": "PENDING_ENHANCEMENT"},
                {"item": "Catalyst timeline aligned with research holding period", "status": "PENDING_ENHANCEMENT"},
                {"item": "Explicit thesis review date scheduled", "status": "PENDING_ENHANCEMENT"},
            ]

        finding = PersonaReviewFinding(
            persona_id=pid,
            persona_name=p["persona_name"],
            lens_title=p["lens_title"],
            observed_issue=observed,
            evidence_in_prototype=proto_evidence,
            suggested_change=p["suggested_change"],
            affected_module=p["affected_module"],
            expected_user_value=p["expected_user_value"],
            data_dependency=p["data_dependency"],
            regression_risk=p["regression_risk"],
            implementation_effort=p["implementation_effort"],
            priority=p["priority"],
            acceptance_test=p["acceptance_test"],
            confidence=0.88,
            status="APPROVED",
            checklist_items=checklist,
        )
        findings.append(finding)

    return findings
