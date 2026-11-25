# Phase 2 — Prioritised Backlog & Decision Matrix

**Project:** ThesisForge AI  
**Scope:** Consolidation, Risk Scoring, Backlog Prioritisation & Explicit Rejections  

---

## 1. Prioritisation Framework

Changes are ranked strictly against the following criteria:
1. **User Value:** Does it turn theoretical analysis into an actionable, risk-defined decision?
2. **Evidentiary Integrity:** Does it adhere to strict non-fabrication and reproducible formulas?
3. **Regression Safety:** Does it preserve the existing academic Q18 Bull-Bear-Rebuttal-Risk-Judge workflow without breaking existing tests?
4. **Feasibility:** Can it be implemented cleanly with local deterministic algorithms and available data?

---

## 2. Approved Implementation Backlog

### Priority P0 — Non-Negotiable Core Safe Upgrades
| ID | Enhancement | Affected Modules | Justification & Acceptance Criteria |
|---|---|---|---|
| **P0-1** | **Actionable Signal Card Contract** | `models.py`, `workflow.py`, `frontend/index.html` | Solves the primary critique of Bothra and Sukhani. Provides: Instrument, Research Mode, Decision, Entry Trigger vs Zone, Stop-Loss (invalidation level), Targets (T1/T2), Risk-to-Reward ratio, and Position Size formula `floor(Risk / (Entry - Stop))`. |
| **P0-2** | **Trading Mode Separation (Intraday vs. Swing vs. Positional)** | `workflow.py`, `routes.py`, `frontend/index.html` | Intraday prioritises OHLCV, VWAP, opening range, volume, and sector trend without fundamental veto; Swing balances technical structure with earnings quality; Positional prioritises business moat and valuation. |
| **P0-3** | **Historical Signal Ledger** | `models.py`, `repository.py`, `routes.py` | Additive SQLite table `signal_records` tracking every signal's as-of time, mode, levels, status (`active`, `triggered`, `invalidated`, `target_hit`, `stopped_out`), and revisions. |
| **P0-4** | **Stale & Missing Data Gates** | `workflow.py`, `technical_tools.py` | Forces `WAIT` or `HOLD` with explicit explanation when critical price feeds or filings are missing or stale. |

### Priority P1 — Research & Analytics Enhancements
| ID | Enhancement | Affected Modules | Justification & Acceptance Criteria |
|---|---|---|---|
| **P1-1** | **Deterministic Technical Indicator Engine** | `tools/technical_tools.py` | Calculates EMA (9, 21, 50, 200), RSI (14), ATR (14), VWAP, volume averages, relative strength vs Nifty 50, and opening range breakout (ORB) using unit-tested mathematical algorithms. |
| **P1-2** | **Derivatives & Futures OI Engine** | `tools/derivatives_tools.py` | For F&O securities: analyzes joint price & OI changes to classify Long Buildup, Short Buildup, Short Covering, and Long Unwinding. Computes PCR and option chain walls. Cleanly disabled for non-F&O equities. |
| **P1-3** | **Valuation Context & Quality Scorecard** | `tools/valuation_tools.py`, `models.py` | Implements Agrawal and Kedia recommendations: PE, PB, EV/EBITDA, ROCE, and debt-to-operating-cashflow sanity checks. |
| **P1-4** | **Event Risk & Market Regime Engine** | `tools/regime_tools.py` | Classifies market regime (Bullish, Bearish, Sideways) and detects scheduled high-impact events (earnings dates, RBI policy, budget, F&O expiry). |

### Priority P2 — Contextual & Portfolio Features
| ID | Enhancement | Affected Modules | Justification & Acceptance Criteria |
|---|---|---|---|
| **P2-1** | **Expert Review Lens Tab in Web UI** | `frontend/index.html`, `routes.py` | Displays the 10 persona simulation insights and quality checklists in a dedicated UI tab alongside the existing Research Report and Evidence Ledger. |
| **P2-2** | **Watchlist Sector Exposure & Correlation** | `repository.py`, `routes.py` | Visualizes sector concentration across the asset universe without making unauthorized personal portfolio claims. |
| **P2-3** | **Historical Backtest & Replay Engine** | `evaluation/backtest.py` | Evaluates historical signals chronologically with realistic transaction costs, spread, slippage, reporting win rate, expectancy (R), and drawdown. |

---

## 3. Explicitly Rejected Proposals (With Reasons)

1. **Rejected: Adding 10 New Autonomous LLM Agents to the Core Workflow**
   - *Reason:* Forbidden by Section 1 & Section 3 of the specification. The 10 personas are evaluation lenses, not autonomous agents in the live decision loop. Adding 10 LLM agents would introduce non-determinism, circular debate traps, and latency without improving decision validity.
2. **Rejected: Majority Vote among Review Personas to Determine BUY/SELL**
   - *Reason:* Explicitly prohibited by Section 3: *"Critical design choice: ten reviewers are not ten votes. The existing Judge remains the decision authority; the Risk Agent retains its veto."*
3. **Rejected: Automatic Broker Order Placement / Live Trade Execution**
   - *Reason:* Prohibited by Section 7 & 10. ThesisForge is an academic research decision-support tool. Live broker APIs, credentials, and automated financial execution must not be connected.
4. **Rejected: Complete Aesthetic Redesign of the Web UI**
   - *Reason:* Prohibited by Section 1 & 7. The existing visual identity, color scheme, navigation, and card structure must be preserved.
5. **Rejected: Pretending Synthetic Data is Live Market Data**
   - *Reason:* Violates SEBI compliance rules and the anti-fabrication directive. All data must carry explicit source provenance (`REAL`, `SYNTHETIC`, or `FIXTURE`).
