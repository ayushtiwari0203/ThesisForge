# ThesisForge AI — Multi-Agent Investment Committee
**Course:** CSE476 — Agentic AI and Intelligent Automation (Project 2, Q18)  
**Topic:** Debate-Driven Investment Committee (BUY / HOLD / AVOID)  
**Location:** `Desktop/4vu5h/MTM606/`  
**Framework:** Microsoft Semantic Kernel + Python Deterministic Orchestrator  
**Master System Documentation & Complete Logs:** [`docs/COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md`](COMPLETE_PROJECT_DOCUMENTATION_AND_AUDIT_LOGS.md)  
**Document Coverage & Research Engine Audit:** [`docs/STOCK_DOCUMENT_COVERAGE_AUDIT.md`](STOCK_DOCUMENT_COVERAGE_AUDIT.md)  

---

## 1. Agent Roster
ThesisForge AI distributes investment analysis across separate, single-responsibility agent modules located in `web-app/agents/`:

| Agent Module | Primary Role | Real Python Tools Invoked | Output Contract |
|---|---|---|---|
| **Research Agent** (`research_agent.py`) | Assembles factual evidence from provided documents without taking a stance | `get_document_metadata`, `search_documents`, `retrieve_chunks`, `create_evidence_pack` | `AgentResult` with Evidence Pack (`EV-001`..) |
| **Bull Agent** (`bull_agent.py`) | Constructs strongest defensible positive case; strictly cites evidence IDs | `get_evidence_by_topic`, `get_financial_facts`, `validate_claim_support` | `Argument` (positive thesis, claims, strongest point) |
| **Bear Agent** (`bear_agent.py`) | Constructs strongest defensible negative case; identifies risks and contradictions | `get_risk_evidence`, `get_contradictory_evidence`, `validate_claim_support` | `Argument` (negative thesis, vulnerabilities) |
| **Rebuttal Handler** (`rebuttal.py`) | Conducts exactly one rebuttal turn per side responding to opposing strongest point | `rank_arguments`, `validate_rebuttal_target`, `validate_claim_support` | `Tuple[RebuttalRecord, RebuttalRecord]` |
| **Risk Agent** (`risk_agent.py`) | Audits solvency, debt covenants, and regulatory flags; enforces safety veto | `check_required_evidence`, `calculate_risk_score`, `check_risk_thresholds` | `RiskAssessment` (score, threshold, veto) |
| **Judge Agent** (`judge_agent.py`) | Weighs cases against cited facts; renders BUY/HOLD/AVOID; enforces risk veto | `get_validated_arguments`, `validate_all_citations`, `get_decision_policy`, `enforce_risk_veto` | `JudgeDecision` (recommendation, deciding reasons) |

---

## 2. Architecture & Why the Debate Pattern Fits
Single-prompt LLM evaluation suffers from confirmation bias and ungrounded extrapolations. The **adversarial debate pattern (proponent vs. opponent plus judge)** overcomes this via:
1. **Adversarial Specialization:** Bull and Bear agents maximize positive potential and downside risks independently.
2. **Strict 1-Turn Rebuttal:** Rebuttal is bounded to exactly 1 turn per side addressing the opposing strongest claim, eliminating circular argument loops.
3. **Evidence-Bounded Adjudication:** The Judge is strictly prohibited from introducing external facts; it may only evaluate evidence IDs already established in the run ledger.
4. **Autonomous Risk Gate (Group-of-3 add-on):** An empirical Risk Agent evaluates leverage covenants and regulatory sanctions; crossing the threshold (`0.65`) triggers a **mandatory safety veto that overrides the Judge to `HOLD`**.

---

## 3. Real Python Tools
Every working agent invokes at least two real Python functions that parse text, query the database, calculate metrics, or validate data (no decorative stubs):
- `search_documents(asset_id, query, top_k)`: Hybrid BM25 keyword search with length normalization and financial term weighting.
- `create_evidence_pack(run_id, asset_id, chunks)`: Deduplicates passages, assigns sequential stable codes (`EV-001`..), and registers source page metadata.
- `get_financial_facts(metric_names, run_id)`: Extracts reported metrics (revenue, EBITDA, margins, debt) and ties them to ledger IDs.
- `get_contradictory_evidence(claim_ids, run_id)`: Cross-references documents to detect divergent numbers for the same period.
- `calculate_risk_score(facts)`: Computes an empirical weighted score (0.0 to 1.0) based on regulatory notices, leverage breaches, and audit qualifications.
- `validate_all_citations(run_id, claims)`: Rejects claims with missing citations or nonexistent evidence IDs.

---

## 4. What Retrieval and Memory Hold
- **Document Store & RAG:** Primary filings in `assets/sample_documents/` chunked with preserved page boundaries and document hashes.
- **Evidence Ledger:** Persisted in SQLite (`web-app/storage/thesisforge.db`) containing stable evidence codes (`EV-001`), document provenance, page numbers, and exact quotes.
- **Append-Only Run Log (`logs/run_log.jsonl`):** Every agent execution, tool call, and state transition is appended with a monotonic sequence number, ISO timestamp, and a **SHA-256 cryptographic hash-chain (`previous_hash` & `event_hash`)** for tamper evidence.

---

## 5. One Honest Failure Handled
**Scenario B (Risk Veto Override on Zenith Infrastructure):**  
Zenith Infrastructure boasts a ₹7,850 Cr toll concession backlog, supporting a strong positive growth case. However, its annual filing reveals a **debt-to-equity ratio of 3.41x (breaching its 2.0x covenant)** and a **SEBI regulatory show-cause notice**.  
- *Failure Handled:* Rather than allowing the Bull thesis or provisional BUY stance to prevail, the Risk Agent calculated a risk score of `1.00`, tripped critical flags (`REGULATORY_INVESTIGATION`, `LEVERAGE_COVENANT_BREACH`), and executed a **mandatory veto override to `HOLD`**.  
- *Conflicting Disclosures (Scenario C):* When an unaudited press release claimed 28% growth while audited filings reported 9%, `get_contradictory_evidence` detected the discrepancy and safely resolved to `HOLD` rather than guessing a midpoint.

---

## 6. Exact Install & Run Commands

```powershell
# 1. Navigate to project location on Desktop
cd C:\Users\91860\Desktop\4vu5h\MTM606

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed demo data and ingest documents
cd web-app
python -m database.seed_data
cd ..

# 4. Run automated test suite (13 passing tests)
pytest -v

# 5. Launch the Web Application
python run_app.py
# (or double-click run_app.bat)
# Web UI:    http://localhost:8000
# API Docs:  http://localhost:8000/docs

# 6. Open runnable demo notebook
jupyter notebook notebooks/thesisforge_demo.ipynb
```

---

## 7. Submission Deliverables Summary
- **Runnable Web App:** Located at `Desktop/4vu5h/MTM606/web-app/` (`run_app.py`, `frontend/`, `backend/`)
- **Demo Notebook:** `Desktop/4vu5h/MTM606/notebooks/thesisforge_demo.ipynb` (pre-executed with complete traces and outputs)
- **Architecture Diagram:** `Desktop/4vu5h/MTM606/docs/architecture_diagram/architecture.mmd` and `architecture.html`
- **Append-Only Run Log:** `Desktop/4vu5h/MTM606/logs/run_log.jsonl` (360+ verified hash-chained events)
- **Automated Tests:** `Desktop/4vu5h/MTM606/tests/test_scenarios.py`, `test_evidence.py`, `test_api.py` (13/13 passing)
