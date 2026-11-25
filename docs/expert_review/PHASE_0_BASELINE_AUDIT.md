# Phase 0 — Baseline Architecture & Inventory Audit

**Project:** ThesisForge AI  
**Audit Date:** 18 November 2026  
**Location:** `Desktop/4vu5h/MTM606/`  
**Controlled Upgrade Scope:** 10 Methodology-Inspired Expert Review Personas, Trading Intelligence Upgrades (Intraday/Swing/Positional), Actionable Signal Cards, Signal Ledger, Technical & Derivatives Context, and Historical Evaluation Replay.

---

## 1. System Inventory Baseline

### A. Environment & Frameworks
- **Python Version:** 3.13.15 (Windows 64-bit)
- **Web Backend:** FastAPI 0.115+ with Uvicorn ASGI server
- **Orchestration & LLM:** Microsoft Semantic Kernel 1.47 pattern with deterministic local LLM service adapter
- **Persistence:** SQLite at `web-app/storage/thesisforge.db` with WAL mode and PRAGMA foreign keys
- **Audit Logging:** Append-only SHA-256 cryptographic hash-chained JSONL at `logs/run_log.jsonl` (1,050+ verified events)
- **Testing:** Pytest 9.2.0 with 20 passing unit/integration tests

### B. Core Application Modules (`web-app/`)
| Directory / File | Description | Baseline Status |
|---|---|---|
| `backend/main.py` | FastAPI application factory, CORS, static file mounts | Operational (Port 8000) |
| `backend/routes.py` | REST API routes (`/api/v1/assets`, `/sectors`, `/research-runs`, `/documents/ingest`) | Operational (7 endpoints) |
| `frontend/index.html` | Single-page interface with real-time search, sector filter, tabs, evidence ledger | Operational |
| `orchestration/workflow.py` | Deterministic 9-stage state machine (Research -> Bull/Bear -> Rebuttal -> Risk -> Judge -> Validation -> Report) | Operational |
| `orchestration/state.py` | State enum (`CREATED`, `DOCUMENTS_READY`, `EVIDENCE_READY`, `RESEARCH_COMPLETE`, `BULL_BEAR_COMPLETE`, `REBUTTAL_COMPLETE`, `RISK_REVIEW_COMPLETE`, `JUDGE_COMPLETE`, `VALIDATION_COMPLETE`, `COMPLETED`, `INSUFFICIENT_EVIDENCE`, `FAILED`) | Operational |
| `agents/research_agent.py` | Ingests documents, extracts facts, creates Evidence Pack (`EV-001`..) without taking a stance | Operational (4 tools) |
| `agents/bull_agent.py` | Positive thesis formulation with strict evidence citations | Operational (3 tools) |
| `agents/bear_agent.py` | Downside vulnerability and risk formulation with strict citations | Operational (3 tools) |
| `agents/rebuttal.py` | 1-turn bounded rebuttal handler targeting opposing strongest argument | Operational (3 tools) |
| `agents/risk_agent.py` | Debt covenant and regulatory notice auditor enforcing safety veto (`threshold=0.65`) | Operational (3 tools) |
| `agents/judge_agent.py` | Adjudicates BUY / HOLD / AVOID based exclusively on cited evidence IDs | Operational (4 tools) |
| `agents/llm_adapter.py` | Local semantic adapter with fallback deterministic logic | Operational |
| `tools/document_tools.py` | File text extraction (PDF / TXT), page splitting, semantic chunking, deduplication | Operational |
| `tools/retrieval_tools.py` | BM25 hybrid keyword retrieval filtered strictly by `asset_id` | Operational |
| `tools/evidence_tools.py` | Stable evidence code generation (`EV-001`), quote normalization | Operational |
| `tools/validation_tools.py` | Citation validator rejecting unknown or ungrounded evidence IDs | Operational |
| `tools/risk_tools.py` | Empirical risk scoring, leverage calculation, covenant breach checks | Operational |
| `database/models.py` | Shared Pydantic models and database entity schemas | Operational |
| `database/repository.py` | SQLite persistence, thread-safe connections, cryptographic hash verification | Operational |
| `database/seed_data.py` | Seeding script for 14 companies (11 real NSE stocks + 3 synthetic benchmarks) | Operational |

### C. Test Suite Baseline (`tests/`)
All 20 tests pass cleanly before any modifications:
1. `tests/test_api.py::test_health_endpoint` -> PASSED
2. `tests/test_api.py::test_list_assets_endpoint` -> PASSED
3. `tests/test_api.py::test_list_asset_documents_endpoint` -> PASSED
4. `tests/test_api.py::test_create_and_fetch_research_run_endpoints` -> PASSED
5. `tests/test_evidence.py::test_text_extraction_and_chunking` -> PASSED
6. `tests/test_evidence.py::test_retrieval_filters_by_selected_asset` -> PASSED
7. `tests/test_evidence.py::test_citation_validator_rejects_unknown_ids` -> PASSED
8. `tests/test_evidence.py::test_rebuttal_rank_arguments` -> PASSED
9. `tests/test_evidence.py::test_risk_threshold_boundary_and_veto_override` -> PASSED
10. `tests/test_evidence.py::test_append_only_log_hash_chaining` -> PASSED
11. `tests/test_scenarios.py::test_scenario_a_normal_debate` -> PASSED
12. `tests/test_scenarios.py::test_scenario_b_risk_veto` -> PASSED
13. `tests/test_scenarios.py::test_scenario_c_insufficient_or_conflicting_evidence` -> PASSED
14. `tests/test_stock_universe.py::test_universe_contains_minimum_11_real_stocks_plus_benchmarks` -> PASSED
15. `tests/test_stock_universe.py::test_unique_ticker_symbols` -> PASSED
16. `tests/test_stock_universe.py::test_asset_search_and_filtering_api` -> PASSED
17. `tests/test_stock_universe.py::test_document_status_and_anti_fabrication_labeling` -> PASSED
18. `tests/test_stock_universe.py::test_graceful_handling_of_pending_document_company` -> PASSED
19. `tests/test_stock_universe.py::test_strict_evidence_isolation_across_companies` -> PASSED
20. `tests/test_stock_universe.py::test_dynamic_asset_registration_api` -> PASSED

---

## 2. Identified Functional Gaps relative to the Expert Specification

1. **Lack of Explicit Research Modes (Intraday vs. Swing vs. Positional):**
   - Current prototype evaluates assets purely on fundamental filings without time-horizon conditioning.
   - Intraday traders cannot use a 12-month annual filing as their primary trigger without OHLCV, VWAP, or opening range data.
   - Positional investors require macro/sector cycle context and deeper valuation comparisons.

2. **Absence of Actionable Signal Contracts (The "Trade Card"):**
   - The current output is an investment judgement (`BUY`, `HOLD`, `AVOID`) with deciding reasons, but lacks actionable execution levels: Entry Trigger vs. Entry Zone, Stop-Loss (invalidation level), Profit Targets (T1/T2), Risk-to-Reward ratio (R:R), and position-sizing formula based on explicit risk capital.

3. **Absence of Technical Structure & Indicators Engine:**
   - No deterministic calculations for EMA/SMA trends, RSI momentum, ATR volatility, VWAP deviations, or volume spikes.

4. **Absence of Derivatives & Futures OI Analytics:**
   - No tracking of futures OI and price dynamics (Long Buildup, Short Buildup, Short Covering, Long Unwinding).
   - No Put-Call Ratio (PCR) or option chain wall context for F&O-eligible securities.

5. **Absence of Versioned Signal Ledger & Historical Replay Evaluation:**
   - Research runs record agent events, but there is no dedicated signal ledger tracking the lifecycle of an idea (`active` -> `triggered` -> `target_hit` / `stopped_out`) across historical bars with realistic transaction costs and slippage.

6. **Absence of Stored Expert Review Personas:**
   - The ten methodology-inspired review personas need a dedicated, isolated evaluation layer to review runs, provide quality assurance checklists, and identify gaps without interfering with the Judge's decision authority or the Risk Agent's veto.

---

## 3. Baseline Audit Sign-off
Baseline status is verified clean, fully functional, and ready for incremental, additive enhancements.
