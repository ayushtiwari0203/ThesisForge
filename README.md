# ThesisForge AI — Multi-Agent Investment Committee
**Course:** CSE476 — Agentic AI and Intelligent Automation (Project 2, Q18)  
**Topic:** Debate-Driven Investment Committee (BUY / HOLD / AVOID)  
**Location:** `Desktop/4vu5h/MTM606/`  
**Framework:** Microsoft Semantic Kernel + Python Deterministic Orchestrator  
**Stock Universe:** 12 Real Indian NSE Listed Equities + 3 Academic Benchmarks (15 Total)  
**Master Documentation:** [`docs/COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md`](docs/COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md)  
**Document Coverage Audit:** [`docs/STOCK_DOCUMENT_COVERAGE_AUDIT.md`](docs/STOCK_DOCUMENT_COVERAGE_AUDIT.md)  

---

## 1. Agent Roster & Real Python Tools
ThesisForge AI distributes investment analysis across separate, single-responsibility agent modules located in `web-app/agents/`. Every working agent invokes at least two real Python functions with zero dummy stubs:

| Agent Module | Primary Role | Real Python Tools Invoked | Output Contract |
|---|---|---|---|
| **Research Agent** (`research_agent.py`) | Assembles factual evidence from provided documents without taking a stance | `get_document_metadata`, `search_documents`, `retrieve_chunks`, `create_evidence_pack` | `AgentResult` with Evidence Pack (`EV-001`..) |
| **Bull Agent** (`bull_agent.py`) | Constructs strongest defensible positive case; strictly cites evidence IDs | `get_evidence_by_topic`, `get_financial_facts`, `validate_claim_support` | `Argument` (positive thesis, claims, strongest point) |
| **Bear Agent** (`bear_agent.py`) | Constructs strongest defensible negative case; identifies risks and contradictions | `get_risk_evidence`, `get_contradictory_evidence`, `validate_claim_support` | `Argument` (negative thesis, vulnerabilities) |
| **Rebuttal Handler** (`rebuttal.py`) | Conducts exactly one rebuttal turn per side responding to opposing strongest point | `rank_arguments`, `validate_rebuttal_target`, `validate_claim_support` | `Tuple[RebuttalRecord, RebuttalRecord]` |
| **Risk Agent** (`risk_agent.py`) | Audits solvency, debt covenants, and empirical volatility; enforces safety veto | `check_required_evidence`, `calculate_risk_score`, `check_risk_thresholds` | `RiskAssessment` (score, threshold, veto) |
| **Judge Agent** (`judge_agent.py`) | Weighs cases against cited facts; renders BUY/HOLD/AVOID; enforces risk veto | `get_validated_arguments`, `validate_all_citations`, `get_decision_policy`, `enforce_risk_veto` | `JudgeDecision` (recommendation, deciding reasons) |

---

## 2. Expanded Company Universe (12 Real Stocks + 3 Benchmarks)
ThesisForge contains an investment universe of **15 companies** separated by dataset type and document availability:

### Real Indian Listed Equities (12 NSE Companies):
1. **Reliance Industries Limited (`RELIANCE`)**: Energy & Conglomerate • Authentic Q2 FY25 NSE/BSE filing indexed.
2. **Tata Consultancy Services Limited (`TCS`)**: Information Technology • Authentic Q2 FY25 NSE/BSE filing indexed.
3. **Infosys Limited (`INFY`)**: Information Technology • Authentic Q2 FY25 NSE/BSE filing indexed.
4. **Tata Motors Limited (`TATAMOTORS`)**: Automobile & JLR • Authentic Q2 FY25 NSE/BSE filing indexed.
5. **HDFC Bank Limited (`HDFCBANK`)**: Banking & Financial Services • `documents_pending` (0 docs in store).
6. **ICICI Bank Limited (`ICICIBANK`)**: Banking & Financial Services • `documents_pending` (0 docs in store).
7. **Larsen & Toubro Limited (`LT`)**: Infrastructure & Engineering • `documents_pending` (0 docs in store).
8. **Bharti Airtel Limited (`BHARTIARTL`)**: Telecommunications • `documents_pending` (0 docs in store).
9. **ITC Limited (`ITC`)**: Consumer Goods & Conglomerate • `documents_pending` (0 docs in store).
10. **State Bank of India (`SBIN`)**: Banking & Financial Services • `documents_pending` (0 docs in store).
11. **Hindustan Unilever Limited (`HINDUNILVR`)**: Consumer Goods & FMCG • `documents_pending` (0 docs in store).
12. **Asian Paints Limited (`ASIANPAINT`)**: Consumer Discretionary • `documents_pending` (0 docs in store).

### Academic Scenario Benchmarks (3 Synthetic Companies):
13. **Solaris Power Tech Limited (`SOLARIS`)**: Scenario A (Balanced normal debate, BUY).
14. **Zenith Infrastructure Limited (`ZENITH`)**: Scenario B (Covenant breach & show-cause notice triggering Risk Veto to AVOID).
15. **Apex Technologies Limited (`APEX`)**: Scenario C (Conflicting promotional PR vs statutory audited filing, HOLD).

### Strict Anti-Fabrication Rule:
In compliance with SEBI regulatory standards and academic integrity rules, **ThesisForge NEVER fabricates financial data**. When research is run on any company with pending documents (e.g., HDFC Bank), the system safely defaults to an **`INSUFFICIENT_EVIDENCE`** status and a **`HOLD`** recommendation with zero fabricated claims. Users can upload official filings via the Web UI to ingest documents on demand.

---

## 3. Architecture & Debate Pattern
- **Adversarial Specialization:** Bull and Bear agents maximize positive potential and downside risks independently.
- **Strict 1-Turn Rebuttal:** Bounded to exactly 1 turn per side addressing the opposing strongest claim, eliminating circular argument loops.
- **Evidence-Bounded Adjudication:** The Judge is strictly prohibited from introducing external facts; it may only evaluate evidence IDs already established in the run ledger.
- **Autonomous Risk Gate (Group-of-3 add-on):** An empirical Risk Agent evaluates leverage covenants and regulatory sanctions; crossing the threshold (`0.70`) triggers a **mandatory safety veto that overrides the Judge to `AVOID`**.
- **Cryptographic Audit Trail:** Every event is appended with a monotonic sequence number, ISO timestamp, and a **SHA-256 cryptographic hash-chain (`previous_hash` & `event_hash`)** in `logs/run_log.jsonl` (4,239 verified events).

---

## 4. Single-Click Launch & Exact Commands

### Option A: Single-Click Windows Launchers (Desktop/4vu5h/MTM606/)
- `Start ThesisForge.bat` — Starts FastAPI backend and serves Web Application on `http://localhost:8000`.
- `Run Tests.bat` — Executes the complete 38-test automated suite (100% green).
- `Open Presentation.bat` — Launches the interactive 10-slide academic presentation in your browser.
- `Open Demo Notebook.bat` — Launches Jupyter Notebook on `notebooks/thesisforge_demo.ipynb`.

### Option B: Terminal Commands
```powershell
# 1. Navigate to project root
cd C:\Users\91860\Desktop\4vu5h\MTM606

# 2. Run automated test suite (38 passing tests)
pytest -v

# 3. Launch Web Application
python web-app/run_app.py
# Web UI:    http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

---

## 5. Submission Deliverables Summary
- **Master Documentation & Complete Logs:** [`docs/COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md`](docs/COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md) (exhaustive system manual from genesis to current state, including logs, tables, model analyses, and testing matrix)
- **Stock Document Coverage & Audit Report:** [`docs/STOCK_DOCUMENT_COVERAGE_AUDIT.md`](docs/STOCK_DOCUMENT_COVERAGE_AUDIT.md)
- **Academic Presentation (10 Slides):** `Desktop/4vu5h/MTM606/docs/presentation.html` (interactive browser presentation) and `Desktop/4vu5h/MTM606/docs/CSE476_FINAL_PRESENTATION_10_SLIDES.md`
- **Runnable Web App:** `Desktop/4vu5h/MTM606/web-app/` (`run_app.py`, `frontend/`, `backend/`, `orchestration/`, `agents/`, `tools/`, `database/`, `rag/`)
- **Demo Notebook:** `Desktop/4vu5h/MTM606/notebooks/thesisforge_demo.ipynb` (pre-executed with complete traces and outputs for real stocks and benchmark scenarios)
- **Architecture Diagram:** `Desktop/4vu5h/MTM606/docs/architecture_diagram/architecture.mmd` and `architecture.html`
- **Append-Only Run Log:** `Desktop/4vu5h/MTM606/logs/run_log.jsonl` (4,239 verified SHA-256 hash-chained events)
- **Automated Tests:** `Desktop/4vu5h/MTM606/tests/` (38/38 passing tests across API, evidence, scenarios, expert features, market data, coverage, and stock universe)
