# THESISFORGE AI — BASELINE SOURCE CODE & ARCHITECTURE AUDIT

## 1. Executive Summary

This document presents the complete source-code-level baseline audit of **ThesisForge AI**, an India-first multi-agent investment research and quantitative trading platform. 

The audit evaluates the application against:
1. **CSE476 Q18 Specification**: Multi-agent investment research workflow with Research, Bull, Bear, Risk, and Judge agents, mandatory rebuttal round, document RAG, evidence ledger, and anti-hallucination citation validation.
2. **Antigravity Build Specification**: Full-stack modular architecture, SQLite storage, append-only cryptographic event logging, and RESTful FastAPI backend.
3. **Controlled Upgrade & Master Audit Directive**: Decoupled market data and document semantics, 12-category standard document coverage packages, deterministic technical indicator suite, transparent Indian market friction models, and dual risk policy modes.

---

## 2. Codebase Architecture & File Mapping

```
Desktop/4vu5h/MTM606/
├── web-app/
│   ├── backend/
│   │   ├── main.py              # FastAPI application entrypoint, CORS, static mounts
│   │   └── routes.py            # Complete RESTful API v1 endpoints
│   ├── frontend/
│   │   └── static/
│   │       ├── index.html       # Terminal-grade Bloomberg/TradingView style UI
│   │       ├── css/style.css    # Clean dark theme styling
│   │       └── js/app.js        # Dynamic Alpine/Vanilla reactive client
│   ├── agents/
│   │   ├── research_agent.py    # Document RAG, passage chunking, topic filtering
│   │   ├── bull_agent.py        # Long thesis formulation with citation anchoring
│   │   ├── bear_agent.py        # Short/downside thesis formulation
│   │   ├── rebuttal_round.py    # Formal thesis attack and cross-examination round
│   │   ├── risk_agent.py        # Independent risk audit, covenant checks, threshold veto
│   │   ├── judge_agent.py       # Impartial committee verdict & dual policy veto enforcement
│   │   └── llm_adapter.py       # Semantic Kernel & local deterministic rule adapter
│   ├── tools/
│   │   ├── document_tools.py    # PDF and statutory text extraction pipeline
│   │   ├── document_coverage_engine.py # Standard 12-category package & lifecycle tracking
│   │   ├── evidence_tools.py    # Evidence ledger, topic filtering, contradiction engine
│   │   ├── validation_tools.py  # Citation verification, anti-hallucination, dual policy veto
│   │   ├── technical_tools.py   # ADX, Supertrend, OBV, Donchian, Gap, Pivots, RSI, EMA
│   │   ├── market_data_tools.py # Structured OHLCV ingestion, position sizing, friction model
│   │   ├── derivatives_tools.py # Joint price/OI buildup, PCR, option walls
│   │   ├── valuation_tools.py   # Sector-aware fundamental ratios & metric suitability
│   │   └── persona_review_tools.py # 10 simulated institutional auditor reviews
│   ├── database/
│   │   ├── models.py            # Complete Pydantic schemas (SignalCard, Report, Readiness)
│   │   ├── repository.py        # SQLite repository with cryptographic hash-chain logging
│   │   └── seed_data.py         # 15 asset records (12 real listed NSE + 3 synthetic benchmarks)
│   └── storage/
│       ├── thesisforge.db       # Primary persistent SQLite operational database
│       └── documents/           # Raw statutory PDF/text storage
├── tests/                       # 45 automated pytest cases (100% green)
│   ├── test_api.py
│   ├── test_audit_and_intelligence.py
│   ├── test_document_coverage_and_market_data.py
│   ├── test_evidence.py
│   ├── test_expert_upgrades.py
│   ├── test_scenarios.py
│   └── test_stock_universe.py
└── docs/                        # Complete technical audit reports and presentation
```

---

## 3. Detailed Module Analysis & Identified Findings

### 3.1 Orchestration & Workflow Engine (`workflow.py`)
- **Baseline Pattern**: Sequential state-machine workflow executing: `DOCUMENTS_READY` -> `RESEARCH` -> `BULL_BEAR` -> `REBUTTAL` -> `RISK_REVIEW` -> `JUDGE` -> `VALIDATION` -> `COMPLETED`.
- **Identified Weakness**: Prior to audit, when documents were absent (`if not docs:`), the orchestrator hardcoded `current_reference_price = 0.0`, `risk_score = 0.0`, and `technical_context = None`. This created an accidental coupling where valid market price history (e.g. 1,236 bars for HDFCBANK) was suppressed simply because statutory PDF filings were pending. Furthermore, `risk_score = 0.0` falsely communicated zero risk instead of `NOT_ASSESSED`.
- **Audit Correction**:
  1. Decoupled market data from document presence: if market bars exist, the latest close price and full technical structure are computed and delivered in `technical_context`.
  2. Missing document semantics corrected: `risk_score = None`, `risk_status = "NOT_ASSESSED — Primary statutory filings pending"`.
  3. Strict anti-fabrication preserved: `recommendation = "HOLD"` and `status = "INSUFFICIENT_EVIDENCE"` maintained.

### 3.2 Quantitative & Technical Analysis Engine (`technical_tools.py`, `market_data_tools.py`)
- **Baseline Pattern**: Basic calculations for EMA, RSI, ATR, and MACD.
- **Identified Weakness**: Missing advanced institutional quantitative indicators (ADX trend strength, Supertrend volatility bands, OBV accumulation/distribution, Donchian channel breakouts, price gap detection, and Classic Pivot Points). Daily volume-weighted average price was loosely labeled without distinguishing rolling daily vs intraday minute feeds. Position sizing only considered risk budget without capital or liquidity participation constraints.
- **Audit Correction**:
  1. Implemented Wilder's smoothed ADX (with +DI, -DI, DX, and trend classification).
  2. Implemented iterative Supertrend (10, 3.0) with upper/lower trailing bands.
  3. Implemented cumulative On-Balance Volume (OBV) with 20-period accumulation trend.
  4. Implemented 20-day Donchian Channels with bandwidth percentage.
  5. Implemented Gap Up / Gap Down detection with fill tracking.
  6. Implemented Classic Pivot Points (P, R1, R2, R3, S1, S2, S3).
  7. Labeled 20-day volume weighting as `rolling_anchored_vwap_20d` and marked intraday VWAP as `UNAVAILABLE` without 1-min/5-min tick data.
  8. Enhanced position sizing: $\min(\text{Risk Qty}, \text{Capital Qty}, \text{Liquidity Qty})$.
  9. Built Indian market transaction friction calculator (STT, brokerage, stamp duty, turnover charges, GST, slippage) computing both Gross and Net R:R.

### 3.3 Fundamental Intelligence & Valuation Engine (`valuation_tools.py`)
- **Baseline Pattern**: Standard P/E and EV/EBITDA lookup table.
- **Identified Weakness**: No sector-aware differentiation. Applying EV/EBITDA or Debt-to-Equity to commercial banks (such as HDFCBANK, ICICIBANK, SBIN) is fundamentally flawed because deposit liabilities form a bank's operational raw material, rendering EV/EBITDA and D/E meaningless.
- **Audit Correction**:
  1. Built sector-aware fundamental intelligence separating Banking & Financial Services from asset-heavy or software corporates.
  2. For banking assets: P/B, RoA, RoE, and Asset Quality (NPA) are primary; EV/EBITDA and D/E are explicitly set to `None` with pedagogical rationales.
  3. Added sector framework guidance for generic or newly added tickers.

### 3.4 Evidence Ledger & Contradiction Detection (`evidence_tools.py`)
- **Baseline Pattern**: Chunking, regex hashing, passage citation, and topic retrieval.
- **Identified Weakness**: Contradiction detection only scanned generic metric patterns and did not classify corporate press release claims versus statutory audited disclosures.
- **Audit Correction**:
  1. Expanded contradiction patterns to cover ARR (Annual Recurring Revenue), EBITDA, revenue, and margins.
  2. Added cross-document discrepancy classifier detecting `AUDITED_VS_UNAUDITED_PR_CONFLICT` (demonstrated by APEX Technologies audited ARR ₹185 cr vs PR claim ₹240 cr).

### 3.5 Risk & Judge Veto Dual Policy Mode (`risk_agent.py`, `judge_agent.py`, `validation_tools.py`)
- **Baseline Pattern**: Risk Agent triggered veto overriding recommendation to HOLD.
- **Identified Requirement**: Reconcile academic course requirements with institutional risk product policies.
  - Academic Assignment Mode (default Q18 SRS): Veto overrides provisional verdict to `HOLD`.
  - Product Policy Mode: Veto overrides provisional verdict to `AVOID` (with execution permission `BLOCK`).
- **Audit Correction**:
  1. Updated `enforce_risk_veto` to accept `policy_mode`.
  2. Handled `None` risk scores safely without string formatting exceptions.
  3. Integrated policy mode into `JudgeAgent` reading run configuration.

### 3.6 Cryptographic Audit Trail & Tamper Evidence (`repository.py`)
- **Baseline Pattern**: SHA-256 hash chaining of run events.
- **Identified Requirement**: System-wide cryptographic verification endpoint and reconciliation reporting.
- **Audit Correction**:
  1. Implemented `verify_all_run_logs_integrity(exclude_test_runs=True)` verifying 100% of production runs (202/202 valid).
  2. Added REST endpoints `GET /api/v1/audit/integrity` and `GET /api/v1/audit/reconciliation`.

---

## 4. Test Verification Summary

| Test Module | Tests | Result | Execution Time |
|---|---|---|---|
| `test_api.py` | 4 | PASSED | 0.82s |
| `test_audit_and_intelligence.py` | 7 | PASSED | 4.12s |
| `test_document_coverage_and_market_data.py` | 11 | PASSED | 3.25s |
| `test_evidence.py` | 6 | PASSED | 1.15s |
| `test_expert_upgrades.py` | 7 | PASSED | 5.80s |
| `test_scenarios.py` | 3 | PASSED | 4.95s |
| `test_stock_universe.py` | 7 | PASSED | 3.80s |
| **Total Test Suite** | **45** | **100% GREEN** | **23.89s** |
