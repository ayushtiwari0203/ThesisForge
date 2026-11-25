"""Domain models, Pydantic contracts, and shared schemas for ThesisForge AI."""

from __future__ import annotations
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Section 6.1 Shared Pydantic Contracts from SRS
# ---------------------------------------------------------------------------

class EvidenceRef(BaseModel):
    """Reference to a verified piece of evidence in the evidence ledger."""
    evidence_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    quote: str
    source_date: Optional[date] = None


class Claim(BaseModel):
    """An individual assertion made by an agent, strictly backed by evidence IDs."""
    claim_id: str
    text: str
    claim_type: Literal["fact", "calculation", "interpretation"]
    evidence_ids: List[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    """Standardized result returned by working agents."""
    agent_name: str
    run_id: UUID
    status: Literal["completed", "failed", "insufficient_evidence"]
    summary: str
    claims: List[Claim] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    tool_calls: List[str] = Field(default_factory=list)


class Argument(BaseModel):
    """Structured debate case presented by Bull or Bear agents."""
    thesis: str
    claims: List[Claim] = Field(default_factory=list)
    strongest_point: Claim
    counterpoints: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    uncertainty: List[str] = Field(default_factory=list)


class RebuttalRecord(BaseModel):
    """Single-turn rebuttal response targeting opposing strongest argument."""
    target_claim_id: str
    target_claim_text: str
    response: str
    cited_ids: List[str] = Field(default_factory=list)
    status: Literal["addressed", "partially_addressed", "unanswered"] = "addressed"


class RiskAssessment(BaseModel):
    """Structured output of the Risk Agent enforcing the veto threshold."""
    score: Optional[float] = None
    threshold: float = 0.70
    veto: bool = False
    risk_status: Literal["assessed", "not_assessed", "insufficient_data"] = "assessed"
    reasons: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)


class JudgeDecision(BaseModel):
    """Final decision rendered by the Judge Agent before and after risk veto."""
    recommendation: Literal["BUY", "HOLD", "AVOID"]
    strongest_bull_claim_id: str
    strongest_bear_claim_id: str
    deciding_reasons: List[Claim] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    provisional_recommendation: Optional[Literal["BUY", "HOLD", "AVOID"]] = None
    veto_applied: bool = False
    veto_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Section 5 & 7 Actionable Signal Card & Versioned Signal Ledger
# ---------------------------------------------------------------------------

class SignalCard(BaseModel):
    """Structured, actionable trade plan complying with Section 5 of Expert Spec."""
    signal_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    instrument: str
    symbol: str
    exchange: str = "NSE"
    research_mode: Literal["intraday", "swing", "positional"] = "swing"
    decision: Literal["BUY", "SELL", "HOLD"] = "HOLD"
    setup_name: str = "Regime Trend Structure"
    current_reference_price: float = 0.0
    entry_trigger: Optional[float] = None
    entry_zone_min: Optional[float] = None
    entry_zone_max: Optional[float] = None
    stop_loss: Optional[float] = None
    stop_loss_type: Literal["hard_stop", "close_based", "time_stop"] = "close_based"
    invalidation_reason: str = "Price breakdown below key moving average or safety threshold breach."
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    reward_to_risk: Optional[float] = None
    position_size_formula: str = "Quantity = floor(Allowed Rupee Risk / (Entry Price - Stop Loss))"
    risk_budget_rupees: float = 10000.0
    risk_per_share: Optional[float] = None
    suggested_quantity: int = 0
    holding_window: str = "3–10 Trading Sessions"
    setup_expiry: str = ""
    slippage_assumption_pct: float = 0.15
    liquidity_impact_caveat: str = "Normal market hours execution."
    no_trade_conditions: List[str] = Field(default_factory=list)
    confidence_score: float = 0.75
    confidence_label: str = "Moderate Conviction"
    is_actionable: bool = False
    actionability_reason: str = ""
    as_of: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SignalRecord(BaseModel):
    """Persistent ledger entity tracking historical trade signals and outcomes."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    asset_id: str
    symbol: str
    mode: str
    decision: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    risk_reward: Optional[float] = None
    status: Literal["active", "triggered", "target_hit", "stopped_out", "expired", "invalidated"] = "active"
    outcome_r_multiple: Optional[float] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Section 4.2 Final Report Schema
# ---------------------------------------------------------------------------

class FinalReport(BaseModel):
    """Complete, immutable output artifact for an investment research run."""
    run_id: str
    asset: Dict[str, str]  # e.g., {"name": "...", "symbol": "..."}
    as_of: str
    recommendation: Literal["BUY", "HOLD", "AVOID"]
    risk_veto: Dict[str, Any]  # {"triggered": bool, "reason": Optional[str]}
    strongest_bull_argument: Dict[str, Any]  # {"claim": str, "evidence_ids": List[str]}
    strongest_bear_argument: Dict[str, Any]  # {"claim": str, "evidence_ids": List[str]}
    bull_rebuttal: Dict[str, Any]  # {"text": str, "evidence_ids": List[str]}
    bear_rebuttal: Dict[str, Any]  # {"text": str, "evidence_ids": List[str]}
    deciding_reasons: List[Dict[str, Any]]  # [{"reason": str, "evidence_ids": List[str]}]
    uncertainties: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    research_mode: Literal["intraday", "swing", "positional"] = "swing"
    signal_card: Optional[SignalCard] = None
    technical_context: Optional[Dict[str, Any]] = None
    derivatives_context: Optional[Dict[str, Any]] = None
    valuation_context: Optional[Dict[str, Any]] = None
    expert_reviews: Optional[List[Dict[str, Any]]] = None


# ---------------------------------------------------------------------------
# Ingestion and Storage Entities (Section 8 Schema)
# ---------------------------------------------------------------------------

class Asset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    symbol: str
    exchange: str = "NSE"
    isin: Optional[str] = None
    asset_type: str = "equity"
    sector: Optional[str] = None
    description: Optional[str] = None
    dataset_type: Literal["real_listed", "synthetic_demo"] = "real_listed"
    document_status: str = "documents_pending"
    document_count: int = 0
    last_document_update: Optional[str] = None
    market_cap_category: Optional[str] = "Large Cap"


class DocumentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    asset_id: str
    filename: str
    source: str
    source_date: Optional[str] = None
    content_hash: str
    storage_path: str
    status: str = "indexed"
    page_count: int = 1
    doc_type: str = "annual_report"


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    asset_id: str
    page_number: int
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    document_id: str
    document_name: str
    evidence_code: str  # e.g., EV-001
    page_number: Optional[int] = 1
    passage_text: str
    evidence_type: str = "financial_fact"
    reporting_period: Optional[str] = "FY2025-26"
    published_at: Optional[str] = None
    content_hash: str = ""
    relevance_score: float = 1.0


class RunEvent(BaseModel):
    id: int
    run_id: str
    sequence_no: int
    occurred_at: str
    event_type: str
    agent_or_tool: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str


class ResearchRunRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    asset_id: str
    status: str = "CREATED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Section 8 & Audit Extension: Document Coverage & Historical Market Data
# ---------------------------------------------------------------------------

class DocumentCoverageItem(BaseModel):
    """Specific document record within the 12-category standard document package."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    asset_id: str
    symbol: str
    category_key: str  # e.g., 'annual_report', 'quarterly_results', 'balance_sheet', etc.
    category_name: str
    period: str  # e.g., 'FY2024-25', 'Q2 FY25', 'Latest 12M'
    document_id: Optional[str] = None  # FK to documents table if ingested
    title: str
    status: Literal["available", "missing", "outdated", "failed", "pending"] = "pending"
    lifecycle_stage: Literal[
        "SOURCE_DISCOVERED",
        "DOCUMENT_DOWNLOADED",
        "DOCUMENT_DOWNLOADED_VERIFIED",
        "DOCUMENT_EXTRACTED",
        "DOCUMENT_EXTRACTED_INDEXED",
        "DOCUMENT_REJECTED",
        "DOCUMENT_UNAVAILABLE",
        "DOCUMENT_PENDING",
    ] = "DOCUMENT_PENDING"
    source_name: str = "NSE Statutory Filing"
    source_url: str = ""
    publication_date: Optional[str] = None
    page_count: int = 0
    extraction_status: Literal["success", "failed", "not_extracted", "pending"] = "pending"
    notes: Optional[str] = None
    last_checked: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HistoricalBar(BaseModel):
    """Structured daily OHLCV market price record with corporate-action adjustments."""
    symbol: str
    trade_date: str  # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: float
    corporate_action_notes: Optional[str] = None


class AssetReadinessRecord(BaseModel):
    """Audited research-readiness summary across documents, fundamentals, and market data."""
    asset_id: str
    symbol: str
    name: str
    total_required_categories: int = 12
    available_docs_count: int = 0
    missing_docs_count: int = 0
    outdated_docs_count: int = 0
    pending_docs_count: int = 0
    failed_docs_count: int = 0
    market_data_bars: int = 0
    market_data_start_date: Optional[str] = None
    market_data_end_date: Optional[str] = None
    historical_market_coverage_pct: float = 0.0
    fundamental_coverage_pct: float = 0.0
    technical_coverage_pct: float = 0.0
    technical_readiness: str = "TECHNICAL_READY"
    fundamental_readiness: str = "DOCUMENTS_PENDING"
    event_readiness: str = "EVENT_TRACKING_PENDING"
    overall_readiness: Literal["READY_FOR_RESEARCH", "PARTIALLY_READY", "DOCUMENTS_PENDING", "INSUFFICIENT_DATA"] = "DOCUMENTS_PENDING"
    readiness_explanation: str = ""
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

