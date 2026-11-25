# ThesisForge AI — Stock Universe & Autonomous Build Report
**Course:** CSE476 — Agentic AI and Intelligent Automation (Project 2, Q18)  
**Deliverable:** Stock Universe Expansion (Minimum 11 Real Stocks) & Autonomous System Build  
**Location:** `Desktop/4vu5h/MTM606/`  
**Execution Mode:** Fully Autonomous (Zero Permission Interruptions)  
**Date:** November 2026  

---

## 1. Executive Summary
ThesisForge AI has been autonomously expanded to support an investment universe of **14 companies**, including **11 distinct Indian publicly listed companies on the National Stock Exchange (NSE)** alongside the 3 controlled academic scenario benchmarks. 

All core assignment requirements (SRS Sections 1 through 14) and supplementary autonomous instructions have been implemented and rigorously tested:
- **Zero Financial Fabrication:** Authentic quarterly and annual financial filings were sourced and ingested for real companies. Companies awaiting documents are strictly and honestly labeled as `"documents_pending"` (`0` documents), safely defaulting to an `INSUFFICIENT_EVIDENCE` status with a `HOLD` recommendation in accordance with SEBI disclosure standards.
- **Strict Evidence Isolation:** All document ingestion, chunk retrieval, and evidence synthesis operations are strictly filtered by `asset_id`. Cross-company evidence contamination is verified to be impossible by automated test suites.
- **Search & Filtering Architecture:** Multi-field search (by company name and symbol) and multi-dimensional filtering (by sector, dataset type, and document status) are implemented across the SQLite repository, FastAPI REST API, and modern Web Application interface.
- **Dynamic Asset Registration:** New equities can be added dynamically via `POST /api/v1/assets` and the interactive Web UI modal without altering underlying code.
- **100% Automated Test Pass Rate:** All 20 tests across 4 test suites pass cleanly.

---

## 2. Complete Asset Master Universe (14 Companies)

| # | Company Name | Symbol | Exchange | ISIN | Sector | Dataset Type | Document Status | Filings / Proof Ingested |
|---|---|---|---|---|---|---|---|---|
| 1 | **Reliance Industries Limited** | `RELIANCE` | NSE | INE002A01018 | Energy & Conglomerate | `real_listed` | `indexed` (1 doc, 5 pages) | Authentic Q2 FY25 Regulatory Filing (NSE/BSE) |
| 2 | **Tata Consultancy Services Ltd** | `TCS` | NSE | INE467B01029 | Information Technology | `real_listed` | `indexed` (1 doc, 5 pages) | Authentic Q2 FY25 Regulatory Filing (NSE/BSE) |
| 3 | **Infosys Limited** | `INFY` | NSE | INE009A01021 | Information Technology | `real_listed` | `indexed` (1 doc, 5 pages) | Authentic Q2 FY25 Regulatory Filing (NSE/BSE) |
| 4 | **Tata Motors Limited** | `TATAMOTORS` | NSE | INE155A01022 | Automobile | `real_listed` | `indexed` (1 doc, 5 pages) | Authentic Q2 FY25 Regulatory Filing (NSE/BSE) |
| 5 | **HDFC Bank Limited** | `HDFCBANK` | NSE | INE040A01034 | Banking & Financial Services | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 6 | **ICICI Bank Limited** | `ICICIBANK` | NSE | INE090A01021 | Banking & Financial Services | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 7 | **Larsen & Toubro Limited** | `LT` | NSE | INE018A01030 | Infrastructure & Engineering | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 8 | **Bharti Airtel Limited** | `BHARTIARTL` | NSE | INE397D01024 | Telecommunications | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 9 | **ITC Limited** | `ITC` | NSE | INE154A01025 | Consumer Goods & Conglomerate | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 10 | **State Bank of India** | `SBIN` | NSE | INE062A01020 | Banking & Financial Services | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 11 | **Hindustan Unilever Limited** | `HINDUNILVR` | NSE | INE030A01027 | Consumer Goods & FMCG | `real_listed` | `documents_pending` (0 docs) | Official records pending upload |
| 12 | **Solaris Power Tech Limited** | `SOLARIS` | NSE | INE123A01020 | Renewable Energy & Infra | `synthetic_demo` | `indexed` (6 docs) | Academic Benchmark: Scenario A (Balanced debate) |
| 13 | **Zenith Infrastructure Limited** | `ZENITH` | NSE | INE456B01030 | Civil & Highway Infra | `synthetic_demo` | `indexed` (1 doc) | Academic Benchmark: Scenario B (Risk Veto trigger) |
| 14 | **Apex Technologies Limited** | `APEX` | NSE | INE789C01040 | Information Technology | `synthetic_demo` | `indexed` (2 docs) | Academic Benchmark: Scenario C (Conflicting facts) |

---

## 3. Strict Anti-Fabrication & Evidence Isolation Guarantee

### 3.1 Non-Fabrication Policy
In strict compliance with academic standards and financial regulatory principles (SEBI Research Analyst Regulations):
- For real companies with available primary filings (`RELIANCE`, `TCS`, `INFY`, `TATAMOTORS`), only authentic audited/unaudited quarterly figures extracted from statutory exchange filings are indexed.
- For real companies without ingested filings (`HDFCBANK`, `ICICIBANK`, `LT`, etc.), the database stores `document_count = 0` and `document_status = "documents_pending"`.
- When an orchestrator run is initiated on a pending-document company, the system **never invents synthetic metrics**. It creates an append-only audit event (`INSUFFICIENT_EVIDENCE`), maps safely to a `HOLD` recommendation, and provides an explicit disclosure note stating that filings are pending.

### 3.2 Evidence Isolation
- Each document chunk is bound to a specific `asset_id` and `document_id`.
- The RAG search tool executes BM25 retrieval exclusively over chunks matching the target asset (`repo.get_chunks_for_asset(asset_id)`).
- Cross-company leakage is prevented at the database query level: a search for Reliance cannot see Infosys chunks, and vice versa. Verified by `tests/test_stock_universe.py::test_strict_evidence_isolation_across_companies`.

---

## 4. Web Application Features & Architecture

The application is fully contained in `Desktop/4vu5h/MTM606/web-app/`:
1. **Interactive Search & Filter Header:**
   - Real-time search by company name and ticker symbol.
   - Sector dropdown filter dynamically populated from `/api/v1/sectors`.
   - Dataset filter tabs (`All (14)`, `Real Listed (11)`, `Academic Demos (3)`).
2. **Dynamic Stock Selection & Metadata Display:**
   - Visual badges for Dataset Type (`Real Listed Equity` vs `Academic Demo`).
   - Visual badges for Document Status (`Authentic Filings (X Docs)` vs `Company added — documents pending`).
   - Advisory notice for pending-document assets detailing SEBI anti-fabrication guidelines.
3. **In-Browser Document Ingestion:**
   - Integrated file upload input allowing evaluators to upload PDF or TXT statutory filings directly into the RAG ledger for any company.
4. **Dynamic Stock Registration Modal:**
   - "+ Add Stock" button opens a modal to register any new NSE ticker with symbol, name, sector, and ISIN without changing backend code.
5. **Multi-Agent Committee Visualizer:**
   - Decision banner with recommendation badge (`BUY`, `HOLD`, `AVOID`).
   - Prominent Risk Veto alert banner with justification when the safety veto is tripped.
   - Dual-card Bull vs. Bear debate layout with clickable evidence tags (`EV-001`..).
   - Structured 1-Turn Rebuttal viewer displaying opposing arguments.
   - Tamper-evident Audit Trail viewer verifying cryptographic SHA-256 hash chaining.
   - Company Master Universe table tab detailing all 14 equities.

---

## 5. Verification & Test Results

The test suite consists of 20 automated tests executed via `pytest`:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\91860\Desktop\4vu5h\MTM606
collected 20 items

tests/test_api.py::test_health_endpoint PASSED                           [  5%]
tests/test_api.py::test_list_assets_endpoint PASSED                      [ 10%]
tests/test_api.py::test_list_asset_documents_endpoint PASSED             [ 15%]
tests/test_api.py::test_create_and_fetch_research_run_endpoints PASSED   [ 20%]
tests/test_evidence.py::test_text_extraction_and_chunking PASSED         [ 25%]
tests/test_evidence.py::test_retrieval_filters_by_selected_asset PASSED  [ 30%]
tests/test_evidence.py::test_citation_validator_rejects_unknown_ids PASSED [ 35%]
tests/test_evidence.py::test_rebuttal_rank_arguments PASSED              [ 40%]
tests/test_evidence.py::test_risk_threshold_boundary_and_veto_override PASSED [ 45%]
tests/test_evidence.py::test_append_only_log_hash_chaining PASSED        [ 50%]
tests/test_scenarios.py::test_scenario_a_normal_debate PASSED            [ 55%]
tests/test_scenarios.py::test_scenario_b_risk_veto PASSED                [ 60%]
tests/test_scenarios.py::test_scenario_c_insufficient_or_conflicting_evidence PASSED [ 65%]
tests/test_stock_universe.py::test_universe_contains_minimum_11_real_stocks_plus_benchmarks PASSED [ 70%]
tests/test_stock_universe.py::test_unique_ticker_symbols PASSED          [ 75%]
tests/test_stock_universe.py::test_asset_search_and_filtering_api PASSED [ 80%]
tests/test_stock_universe.py::test_document_status_and_anti_fabrication_labeling PASSED [ 85%]
tests/test_stock_universe.py::test_graceful_handling_of_pending_document_company PASSED [ 90%]
tests/test_stock_universe.py::test_strict_evidence_isolation_across_companies PASSED [ 95%]
tests/test_stock_universe.py::test_dynamic_asset_registration_api PASSED [100%]

======================== 20 passed, 1 warning in 5.05s ========================
```

---

## 6. Exact Run Commands

From the project root: `C:\Users\91860\Desktop\4vu5h\MTM606\`

### Single-Click Launchers:
- `Start ThesisForge.bat` — Launches the complete web application.
- `Run Tests.bat` — Executes all 20 automated tests.
- `Open Demo Notebook.bat` — Opens the executed demonstration notebook in Jupyter.

### Command-Line Execution:
```powershell
# Navigate to project
cd C:\Users\91860\Desktop\4vu5h\MTM606

# Run full test suite
pytest -v

# Launch the Application
python run_app.py

# Access Web App:
# UI:       http://localhost:8000
# OpenAPI:  http://localhost:8000/docs
```
