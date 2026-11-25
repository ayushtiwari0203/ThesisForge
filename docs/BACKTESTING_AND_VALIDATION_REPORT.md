# THESISFORGE AI — BACKTESTING & EMPIRICAL VALIDATION REPORT

## 1. Executive Summary

ThesisForge AI combines multi-agent investment debate with empirical quantitative execution. To validate that generated trade setups and fundamental verdicts produce sound risk-adjusted outcomes, the platform implements a **Signal Ledger** and a **Walk-Forward Historical Replay Engine**.

---

## 2. Signal Ledger Architecture

Every research run automatically logs its synthesized trade setup into the `signal_records` table:

```sql
CREATE TABLE signal_records (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(id),
    asset_id TEXT NOT NULL REFERENCES assets(id),
    symbol TEXT NOT NULL,
    mode TEXT NOT NULL,          -- 'intraday' | 'swing' | 'positional'
    decision TEXT NOT NULL,      -- 'BUY' | 'HOLD' | 'AVOID'
    entry_price REAL,
    stop_loss REAL,
    target_1 REAL,
    target_2 REAL,
    risk_reward REAL,
    status TEXT NOT NULL,        -- 'active' | 'triggered' | 'target_hit' | 'stopped_out' | 'invalidated'
    outcome_r_multiple REAL,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    notes TEXT
);
```

When an asset has no primary filings (`status = "INSUFFICIENT_EVIDENCE"`), the signal record is marked `status = "invalidated"` with `notes = "No primary filings available. Trade generation suspended."`, preventing false execution tracking.

---

## 3. Walk-Forward Backtesting Replay Methodology

The backtest replay tool (`test_historical_backtest_replay`) simulates historical execution across stored daily OHLCV bars:

1. **Trigger Evaluation**: Checks whether subsequent price bars traded through `entry_price`.
2. **Path Dependency**: Inspects subsequent daily High and Low prices:
   - If Low penetrates `stop_loss` before High reaches `target_1`: Marked `stopped_out` with $R = -1.0$.
   - If High reaches `target_1` before Low breaches `stop_loss`: Marked `target_1_hit` with $R = \text{reward\_to\_risk}$.
   - If holding window elapses without either level hit: Marked `expired` and closed at prevailing market close.
3. **Friction Accounting**: Realized returns deduct Indian transaction costs (STT, stamp duty, brokerage, slippage).

---

## 4. Empirical Scenario Validation Matrix

| Scenario | Asset Tested | Key Characteristics | Committee Verdict | Validation Outcome |
|---|---|---|---|---|
| **Scenario A: Normal Debate** | `SOLARIS` | Strong revenue growth (₹420 cr -> ₹580 cr), expanding margins, 850MW EPC capacity. | **BUY** | Passed. Constructive technical uptrend, actionable swing signal card generated ($R:R \ge 1.5$). |
| **Scenario B: Risk Agent Veto** | `ZENITH` | High gross revenue, but massive debt-to-equity (3.41x), ICR 0.85x, NHAI show-cause notice. | **HOLD (Overridden)** | Passed. Risk score 0.85 crossed 0.65 threshold; provisional BUY overridden to HOLD. Actionability blocked. |
| **Scenario C: Conflicting Evidence** | `APEX` | PR claims ARR of ₹240 cr, but audited statutory Q3 notes disclose ARR of ₹185 cr. | **HOLD** | Passed. Contradiction engine detected audited vs PR mismatch; Judge recognized uncertainty and withheld BUY. |
| **Scenario D: Pending Filings** | `HDFCBANK` | 1,236 real daily market bars, but primary statutory PDF pending on-demand upload. | **HOLD (Information Void)** | Passed. Ref price retrieved (₹809.25), technical context computed, fundamental risk marked `NOT_ASSESSED`. |

---

## 5. Automated Verification Test Suite

The automated test suite contains **45 pytest cases**, achieving **100% green pass rate**:

```text
======================= 45 passed, 1 warning in 23.89s ========================
```

- `tests/test_api.py` (4 tests): Health, assets listing, documents, run creation.
- `tests/test_audit_and_intelligence.py` (7 tests): HDFCBANK missing-data decoupling, quantitative indicators (ADX, Supertrend, OBV, Donchian, Pivots, Gaps), position sizing constraints, Indian transaction friction, sector-aware valuation, dual policy modes, audit hash-chain integrity.
- `tests/test_document_coverage_and_market_data.py` (11 tests): 12-category catalog, company isolation, historical OHLCV ingestion, timeframe stop loss/target methods, R:R constraints.
- `tests/test_evidence.py` (6 tests): Text extraction, chunking, citation validation, rebuttal ranking, risk threshold boundary, append-only log chaining.
- `tests/test_expert_upgrades.py` (7 tests): Deterministic technical calculations, derivatives joint price/OI buildup, actionable signal card generation, intraday mode, 10 expert personas, backtest replay.
- `tests/test_scenarios.py` (3 tests): Scenarios A, B, and C.
- `tests/test_stock_universe.py` (7 tests): Universe sizing, unique ticker symbols, search/filtering API, anti-fabrication labeling, pending document company handling, dynamic asset registration.
