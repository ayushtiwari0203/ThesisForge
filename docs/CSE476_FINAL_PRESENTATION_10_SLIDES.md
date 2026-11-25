# ThesisForge AI — Final CSE476 Project Presentation (10 Slides)

**Course:** CSE476 — Agentic AI and Intelligent Automation  
**Assignment:** Project 2 / Task 2 (Units III & IV)  
**Selected Topic:** Question 18 — Debate-Driven Investment Committee (BUY / HOLD / AVOID)  
**Evaluation Scheme (30 Marks Total):** Implementation (10 Marks) | Presentation (10 Marks) | Viva Voce (10 Marks)  
**Project Workspace:** `Desktop/4vu5h/MTM606 ThesisForge/`  
**Runnable Web App:** `Desktop/4vu5h/MTM606 ThesisForge/web-app/`  

---

## Slide 1: Title & Executive Summary
### ThesisForge AI: Evidence-Grounded Multi-Agent Investment Committee

#### 1. Core Problem Solved
Single-prompt LLMs fail in capital allocation because they suffer from:
1. **Confirmation Bias** (agreeing with whatever thesis the user prompts).
2. **Financial Hallucinations** (fabricating revenues, margins, and growth figures).
3. **Infinite Rebuttal Loops** (free-form agent chats that burn tokens without converging).
4. **Lack of Downside Protection** (failing to recognize catastrophic bankruptcy risks).

#### 2. ThesisForge AI Solution
An adversarial multi-agent committee where:
- A neutral **Research Agent** extracts facts into an immutable, numbered **Evidence Ledger** (`EV-001`..).
- Specialized **Bull** and **Bear** agents formulate opposing theses and must cite verified evidence IDs.
- A strictly bounded **1-turn rebuttal round** attacks the opponent's strongest argument.
- An autonomous **Risk Agent** audits debt covenants and enforces an asymmetric **Safety Veto** overriding to `HOLD`.
- An evidence-bounded **Judge Agent** renders an impartial verdict (`BUY`, `HOLD`, `AVOID`).

```text
[Statutory Filings] ──> [RAG & Chunking] ──> [Evidence Ledger (EV-001..)]
                                                     │
     ┌───────────────────────────────────────────────┴───────────────────────────────┐
     ▼                                                                               ▼
[Research Agent] ──> [Bull Agent] vs [Bear Agent] ──> [1-Turn Rebuttal] ──> [Risk Agent Veto Gate]
                                                                                     │
                                                                                     ▼
[Final Report: BUY/HOLD/AVOID] <── [Citation Validation] <── [Judge Agent (Evidence-Bounded)]
                                           │
                                           ▼
                    [Cryptographic SHA-256 Hash-Chained Audit Trail]
```

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"Good morning respected examiners and professor. Today I present **ThesisForge AI**, developed for CSE476 Project 2, addressing **Question 18: Debate-Driven Investment Committee**.*  
> *The core insight of our project is that single LLMs cannot be trusted with capital allocation because they fabricate financial metrics and suffer from confirmation bias. We solved this by building an evidence-grounded multi-agent committee: specialized Bull and Bear agents, a bounded one-turn rebuttal round, an autonomous Risk Agent with circuit-breaker veto power, and an evidence-bounded Judge.*  
> *Our implementation runs in Python with Microsoft Semantic Kernel, features an interactive web dashboard, and is backed by 45 passing automated tests and a tamper-evident SHA-256 audit log."*

---

## Slide 2: Assignment Requirement Compliance Matrix (30/30 Marks)
### 100% Verification Against Course Blueprint & Evaluation Rubric

| Assignment Specification | Course Requirement | ThesisForge Implementation Proof | Status |
|---|---|---|:---:|
| **1. Agent Roster** | Minimum 4 separate agent modules, 1 clear role each | 5 dedicated modules: `research_agent.py`, `bull_agent.py`, `bear_agent.py`, `risk_agent.py`, `judge_agent.py` + `rebuttal.py` | **100% Verified** |
| **2. Real Python Tools** | Each working agent must call $\ge 2$ real Python tools (no dummy stubs) | 20 real Python tools implemented across `web-app/tools/` (2 to 4 real tools invoked per agent) | **100% Verified** |
| **3. Framework** | Microsoft Agent Framework or Semantic Kernel | Microsoft Semantic Kernel adapter (`llm_adapter.py`) with plugin abstractions | **100% Verified** |
| **4. RAG Grounding** | RAG over provided document pack; cite factual evidence | Semantic paragraph chunking, stable Evidence Ledger (`EV-001`..), regex citation validator | **100% Verified** |
| **5. Rebuttal Round** | Exactly one rebuttal response per side | Bounded 1-turn cross-examination in `rebuttal.py` targeting opponent's strongest argument | **100% Verified** |
| **6. Group-of-3 Extension**| Autonomous Risk Agent veto forcing HOLD | `risk_agent.py` calculates empirical risk score; $\ge 0.65$ or covenant breach forces HOLD | **100% Verified** |
| **7. Deliverables** | README ($\le 2$ pages), Notebook, Architecture, Run Log, Tests | 2-page `README.md`, pre-executed `demo.ipynb`, architecture diagrams, SHA-256 `run_log.jsonl`, 45 pytest tests | **100% Verified** |

#### Evaluation Breakdown (30 Marks Total):
- **Implementation (10 Marks):** Modular agents, real Python tools, Semantic Kernel, RAG pipeline, SQLite persistence.
- **Presentation (10 Marks):** Clear problem definition, architecture diagrams, live demo, transparent disclosure.
- **Viva Voce (10 Marks):** Defense of agent boundaries, tool calling, citation validation, risk veto, cryptographic hashing.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"Here is our 100% compliance mapping against the 7 official assignment requirements. Every agent lives in its own dedicated Python file—there is no single mega-prompt simulating agents.*  
> *Every working agent calls at least two real Python functions that do actual computation, such as calculating volatility, parsing PDF boundaries, or validating citations. There are zero dummy stubs.*  
> *We have also completely fulfilled the Group-of-3 add-on requirement with an autonomous **Risk Agent Veto**, which acts as an immutable safety circuit breaker overriding any recommendation to `HOLD` when leverage or covenant red flags are breached."*

---

## Slide 3: Problem Formulation & Architecture Rationale
### Why Adversarial Debate and Bounded Rebuttal Are Essential

```text
┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│       FLAWS OF SINGLE-PROMPT LLMs            │       │       THESISFORGE AI ARCHITECTURE            │
├──────────────────────────────────────────────┤       ├──────────────────────────────────────────────┤
│ 1. Confirmation Bias                         │       │ 1. Stance Specialization                     │
│    Agrees with whatever user prompts         │ ───>  │    Bull maximizes upside; Bear maximizes risk│
│                                              │       │                                              │
│ 2. Financial Hallucination                   │       │ 2. Evidence-Bounded RAG                      │
│    Invents revenue growth & P/E multiples    │ ───>  │    Claims must cite [EV-xxx] or be discarded │
│                                              │       │                                              │
│ 3. Infinite Rebuttal Loops                   │       │ 3. Bounded 1-Turn Rebuttal                   │
│    Free-form multi-agent chats loop forever  │ ───>  │    Exactly 1 response; O(1) time complexity  │
│                                              │       │                                              │
│ 4. Symmetric Risk Blindness                  │       │ 4. Asymmetric Risk Circuit Breaker           │
│    Weighs a 10% gain equal to 100% loss      │ ───>  │    Risk Agent veto overrides Judge to HOLD   │
└──────────────────────────────────────────────┘       └──────────────────────────────────────────────┘
```

#### Key Architectural Principles:
1. **Adversarial Decomposition:** In financial markets, every transaction has a buyer and a seller. Forcing separate Bull and Bear agents guarantees that both positive catalysts and critical risks are exhaustively surfaced.
2. **Guaranteed Termination:** By bounding the cross-examination to **exactly one rebuttal round**, our orchestration state machine executes in $O(1)$ time complexity without endless token consumption.
3. **Asymmetric Capital Protection:** Avoiding bankruptcy is more critical than catching an upside rally. The Risk Agent acts independently from the Judge, auditing debt covenants and solvency.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"Why did we choose an adversarial committee architecture? Because finance is fundamentally adversarial.*  
> *When a single LLM is asked to analyze a stock, it produces confirmation bias. By splitting the analysis into dedicated Bull and Bear agents, both upside and downside hypotheses are maximized.*  
> *Crucially, we bound the debate to **exactly one rebuttal turn per debater**. This guarantees our system terminates deterministically without infinite conversational loops.*  
> *Finally, our Risk Agent provides asymmetric capital preservation: even if the Judge is impressed by growth, a covenant breach immediately triggers a mandatory veto to `HOLD`."*

---

## Slide 4: Deterministic 9-Stage Orchestration State Machine
### Predictable, Observable Workflow with Semantic Kernel Integration

```text
[Stage 1: INITIALIZED]          ──> Verify asset existence, dataset type, and document pack status.
            │
[Stage 2: FACT_RETRIEVAL]       ──> Research Agent parses documents -> populates Evidence Ledger (EV-001..).
            │
[Stage 3: BULL_THESIS]          ──> Bull Agent formulates growth catalysts; all claims must cite [EV-xxx].
            │
[Stage 4: BEAR_THESIS]          ──> Bear Agent identifies solvency risks & margin pressure with [EV-xxx].
            │
[Stage 5: REBUTTAL_ROUND]       ──> 1-turn cross-examination; each side attacks opponent's strongest point.
            │
[Stage 6: RISK_AUDIT]           ──> Risk Agent calculates empirical risk score (debt, covenants, volatility).
            │
[Stage 7: JUDGE_DELIBERATION]   ──> Judge weighs validated evidence; renders provisional BUY / HOLD / AVOID.
            │
[Stage 8: VALIDATION_AND_VETO]  ──> Citation engine audits references; enforces Risk Veto override if score >= 0.65.
            │
[Stage 9: REPORT_FINALIZATION]  ──> Generates Final Report & Signal Card; appends SHA-256 event to audit log.
```

#### Why a Deterministic State Machine?
- **Zero Infinite Loops:** Each stage has a single entry, explicit transformation, and exit condition.
- **Graceful Degradation:** If primary documents are missing (e.g., pending filings), the state machine cleanly transitions to `INSUFFICIENT_EVIDENCE` without crashing or inventing numbers.
- **Complete Observability:** Every transition emits an immutable, timestamped event into the database and JSONL log.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"Our workflow is orchestrated by a **deterministic 9-stage state machine** located in `workflow.py`.*  
> *Rather than letting agents speak at random, every research run moves linearly from Fact Retrieval to Bull Thesis, Bear Thesis, Rebuttal, Risk Audit, Judge Deliberation, Citation Validation, and Final Report.*  
> *If an asset lacks documents, the orchestrator handles it gracefully: it emits an `INSUFFICIENT_EVIDENCE` status, outputs a safe `HOLD` recommendation, and refuses to fabricate fake numbers."*

---

## Slide 5: Agent Roster & Real Python Tools Implementation
### 20 Real Python Functions — Zero Dummy Tool Stubs

| Agent Module | File Path | Real Python Tools Called ($\ge 2$ per agent) | Primary Responsibility |
|---|---|---|---|
| **Research Agent** | `web-app/agents/research_agent.py` | 1. `get_document_metadata`<br/>2. `search_documents`<br/>3. `retrieve_chunks`<br/>4. `create_evidence_pack` | Neutral fact extraction; parses document boundaries; strictly forbidden from taking an investment stance. |
| **Bull Agent** | `web-app/agents/bull_agent.py` | 1. `get_evidence_by_topic`<br/>2. `get_financial_facts`<br/>3. `validate_claim_support` | Builds positive investment thesis; identifies revenue growth and moats; must ground every claim in an evidence ID. |
| **Bear Agent** | `web-app/agents/bear_agent.py` | 1. `get_risk_evidence`<br/>2. `get_contradictory_evidence`<br/>3. `validate_claim_support` | Builds downside risk thesis; identifies debt, margin compression, and covenant breaches. |
| **Rebuttal Handler**| `web-app/agents/rebuttal.py` | 1. `rank_arguments`<br/>2. `validate_rebuttal_target`<br/>3. `validate_claim_support` | Conducts bounded 1-turn cross-examination; attacks opponent's top-ranked argument. |
| **Risk Agent** | `web-app/agents/risk_agent.py` | 1. `calculate_risk_score`<br/>2. `check_required_evidence`<br/>3. `check_risk_thresholds` | Quantitative risk evaluation; calculates composite risk score; triggers autonomous safety veto if score $\ge 0.65$. |
| **Judge Agent** | `web-app/agents/judge_agent.py` | 1. `get_validated_arguments`<br/>2. `validate_all_citations`<br/>3. `get_decision_policy`<br/>4. `enforce_risk_veto` | Synthesizes validated debate claims; applies decision policy; strictly evidence-bounded (cannot invent facts). |

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"A fundamental requirement of the CSE476 assignment is that each working agent must call at least two real Python tools.*  
> *As shown in this table, we built 20 real Python tool functions across `web-app/tools/`. There are zero mock stubs.*  
> *For instance, `research_agent.py` calls `search_documents` for BM25 retrieval and `create_evidence_pack` to generate structured Pydantic objects. `risk_agent.py` calls `calculate_risk_score` to evaluate debt-to-equity and market volatility.*  
> *Every agent has a clear, isolated single-responsibility contract."*

---

## Slide 6: Document RAG, Evidence Grounding & Anti-Hallucination
### Three-Tier Verification Pipeline: Chunking, IDs, and Regex Validation

```text
[Raw PDF / Statutory Filing]
           │
           ▼
[Semantic Paragraph Chunking]  ──> 25–250 character passages; page & section boundary tracking
           │
           ▼
[Evidence Ledger Generation]   ──> Stable sequential IDs: [EV-001], [EV-002], [EV-003]...
           │
           ▼
[Asset Isolation Enforcement]  ──> Strict filter: SELECT * WHERE asset_id = :id (Zero cross-stock data leakage)
           │
           ▼
[Citation Validation Engine]   ──> Regex audit: Rejects claims lacking [EV-xxx] or citing non-existent IDs
           │
           ▼
[Judge Evidence Boundary]      ──> Judge is strictly prohibited from considering any fact outside Evidence Ledger
```

#### How Hallucination Is Mathematically & Programmatically Prevented:
1. **Passage Chunking & Deduplication:** Documents are split into semantic paragraphs, each generating an immutable SHA-256 hash. Duplicate text across filings is automatically discarded.
2. **Strict Citation Auditing (`validation_tools.py`):** Agent claims are parsed with regex pattern `\[(EV-\d{3})\]`. If an agent asserts *"Operating revenue grew by 24%"* without attaching a verified `[EV-xxx]` tag, the claim is rejected.
3. **Contradiction Detection:** Cross-references disclosures across multiple filings (e.g. detecting conflicts between marketing press releases and audited annual balance sheets).

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"How does ThesisForge AI prevent financial hallucinations? We implemented a three-tier evidence grounding engine.*  
> *First, during document ingestion, every verified passage is assigned an immutable evidence code—`EV-001`, `EV-002`, and so on.*  
> *Second, when Bull and Bear agents make claims, our citation validator audits their text using regular expressions. If an agent states a financial fact without citing a valid evidence ID, that claim is discarded.*  
> *Third, our Judge Agent is strictly evidence-bounded: it cannot introduce outside knowledge or un-cited facts into its final ruling."*

---

## Slide 7: The 3 Mandatory Assignment Scenarios
### Empirical Validation Across Scenarios A, B, and C

| Scenario | Tested Company | Key Characteristics | Committee Deliberation | Final Verdict |
|---|---|---|---|:---:|
| **Scenario A: Normal Debate** | `SOLARIS` | Strong revenue growth (₹420 cr $\rightarrow$ ₹580 cr), 850MW solar capacity, expanding margins. | Bull highlights clean energy growth; Bear notes receivable delays; Bull successfully rebuts with cash flow data. | **BUY**<br/>*(Constructive structure)* |
| **Scenario B: Risk Agent Veto** | `ZENITH` | High top-line revenue, but massive debt-to-equity (3.41x), ICR 0.85x, and NHAI show-cause notice. | Bull argues infrastructure turnaround; Risk Agent calculates risk score = 0.85 ($\ge 0.65$ threshold) $\rightarrow$ **Veto Triggered**. | **HOLD**<br/>*(Overridden by Risk Veto)* |
| **Scenario C: Conflicting Claims** | `APEX` | Marketing PR claims Annual Recurring Revenue (ARR) of ₹240 cr; audited statutory filing shows ₹185 cr. | Contradiction engine flags discrepancy; Bear challenges unverified claims; debate highlights data uncertainty. | **HOLD**<br/>*(Capital Preservation)* |

#### Automated Verification:
All three scenarios are codified as automated test cases in `tests/test_scenarios.py`:
- `test_scenario_a_normal_debate` $\rightarrow$ **PASSED**
- `test_scenario_b_risk_veto` $\rightarrow$ **PASSED**
- `test_scenario_c_insufficient_or_conflicting_evidence` $\rightarrow$ **PASSED**

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"The assignment explicitly requires demonstrating three distinct behavioral scenarios.*  
> *In **Scenario A**, Solaris demonstrates a healthy debate: strong revenue growth leads to a verified BUY recommendation.*  
> *In **Scenario B**, Zenith illustrates the Risk Agent Veto: although the Bull argues for top-line growth, the Risk Agent detects dangerous leverage (debt/equity of 3.41x) and triggers a mandatory veto overriding the recommendation to HOLD.*  
> *In **Scenario C**, Apex demonstrates contradiction detection: the company's press release claims ₹240 crore ARR, but audited filings reveal ₹185 crore. The committee flags the conflict and defaults to HOLD."*

---

## Slide 8: Stock Universe & Academic Anti-Fabrication Policy
### Transparent Disclosure: 12 Real Listed Equities + 3 Synthetic Stress Benchmarks

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                THESISFORGE 15-STOCK UNIVERSE                                    │
├────────────────────────────────────────┬────────────────────────────────────────────────────────┤
│ 12 REAL LISTED NSE EQUITIES            │ 3 SYNTHETIC BENCHMARK SCENARIOS                        │
├────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ • RELIANCE     • HDFCBANK (Pending)    │ • SOLARIS (Clean Energy Infrastructure — Scenario A)   │
│ • TCS          • ICICIBANK (Pending)   │ • ZENITH  (Highway Infrastructure — Scenario B Veto)   │
│ • INFY         • SBIN      (Pending)   │ • APEX    (Enterprise Software SaaS — Scenario C Cont.)│
│ • TATAMOTORS   • BHARTIARTL (Pending)  │                                                        │
│ • ITC (Pending)• KOTAKBANK (Pending)   │ Benchmark ISINs Cleansed: ISIN = None                  │
│ • LT (Pending) • HINDUNILVR (Pending)  │ Strictly marked dataset_type = 'synthetic_demo'        │
└────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

#### Strict Anti-Fabrication Guarantees:
1. **Zero Fake Filings:** For the 8 real companies awaiting uploaded annual reports (`HDFCBANK`, `ICICIBANK`, etc.), ThesisForge refuses to synthesize fake financial numbers.
2. **Graceful Degradation:** When research is run on a pending company, the system outputs `INSUFFICIENT_EVIDENCE / HOLD` with unassessed fundamental risk (`score = None`), while keeping live market prices and technical structure active.
3. **On-Demand Ingestion:** The Web UI includes an interactive statutory document uploader so analysts can ingest authentic filings anytime.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"We maintain complete transparency regarding our stock universe. Our database contains 15 companies: 12 real NSE equities and 3 synthetic stress benchmarks.*  
> *Four real equities—Reliance, TCS, Infosys, and Tata Motors—have authentic statutory Q2 FY25 filings indexed.*  
> *The remaining 8 real companies are registered with status `documents_pending`. We deliberately refused to fabricate fake numbers for companies like HDFC Bank. Instead, the system outputs `INSUFFICIENT_EVIDENCE` and issues a safe `HOLD`, while keeping real market prices and technical indicators live."*

---

## Slide 9: Automated Testing & Cryptographic Audit Trail
### 45 Passing Automated Tests & SHA-256 Tamper-Evident Run Log

#### 1. Automated Test Suite (45/45 Tests Passing in 23.89s):
- `tests/test_api.py` (4 tests): Health check, asset search, document listing, run creation.
- `tests/test_audit_and_intelligence.py` (7 tests): Missing-data decoupling, ADX, Supertrend, OBV, position sizing, dual risk modes, audit hash integrity.
- `tests/test_document_coverage_and_market_data.py` (11 tests): 12-category catalog, market data ingestion, timeframe stop-loss, R:R constraints.
- `tests/test_evidence.py` (6 tests): Semantic chunking, asset isolation, citation rejection, hash chaining.
- `tests/test_expert_upgrades.py` (7 tests): Deterministic math, derivatives buildup, actionable signal cards, backtest replay.
- `tests/test_scenarios.py` (3 tests): Scenarios A, B, and C.
- `tests/test_stock_universe.py` (7 tests): Universe sizing, ticker uniqueness, anti-fabrication labels.

#### 2. Cryptographic Run Log (`logs/run_log.jsonl` — 2,500+ Events):
$$\text{Event Hash}_t = \text{SHA256}\left(\text{run\_id} : \text{seq} : \text{time} : \text{event\_type} : \text{agent} : \text{payload} : \text{Event Hash}_{t-1}\right)$$
- **Blockchain-Style Chaining:** Each event incorporates the hash of the preceding event.
- **Tamper Evidence:** Modifying a single character in historical arguments severs the hash chain.
- **100% Production Verification:** All production runs in SQLite verify `all_valid: true`.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"System reliability is verified by **45 unit and integration tests** executing under `pytest`, achieving a 100% green pass rate.*  
> *For regulatory compliance and auditability, every agent thought, tool call, and verdict is recorded in an append-only JSONL run log.*  
> *Each event is linked using SHA-256 cryptographic chaining, exactly like a blockchain block. If an adversary attempts to modify a historical argument, the hash chain breaks immediately. 100% of our production runs pass cryptographic verification."*

---

## Slide 10: Live Demonstration & Viva Examination Defense Guide
### 3-Minute Live Demo Script and Top 5 Viva Questions & Answers

#### Step-by-Step 3-Minute Live Demo Script:
1. **Launch:** Run `Start ThesisForge.bat` $\rightarrow$ Web dashboard opens at `http://localhost:8000`.
2. **Normal Debate (Scenario A):** Select `RELIANCE` or `SOLARIS` $\rightarrow$ Click **Start Research Run** $\rightarrow$ Watch the 9 states transition live $\rightarrow$ Inspect Bull case, Bear case, and cited statutory evidence `[EV-001]`.. $\rightarrow$ Show Final Report (`BUY`).
3. **Risk Veto Circuit Breaker (Scenario B):** Select `ZENITH` $\rightarrow$ Run debate $\rightarrow$ Point out Bull's positive stance $\rightarrow$ Show **Risk Agent detecting 3.41x debt-to-equity covenant breach** $\rightarrow$ **Veto triggered $\rightarrow$ Final recommendation overridden to `HOLD`**.
4. **Anti-Fabrication & Pending Filings:** Select `HDFCBANK` $\rightarrow$ Show `documents_pending` badge $\rightarrow$ System produces `INSUFFICIENT_EVIDENCE / HOLD` without fabricating numbers, while displaying live market price.
5. **Audit Trail Verification:** Open `/api/v1/audit/integrity` in browser $\rightarrow$ Show live verification returning `all_valid: true`.

#### Top 5 Viva Examination Questions & Answers:
- **Q1: Why separate agent files instead of a single LLM prompt?**  
  *Answer:* A single prompt cannot enforce adversarial independence because attention mechanisms create semantic bleed across roles. Separate modules enforce distinct system prompts, independent tool execution, and deterministic validation boundaries.
- **Q2: How do you guarantee zero financial hallucinations?**  
  *Answer:* Through strict three-tier evidence grounding: passages are assigned immutable evidence IDs (`EV-001`..); regex validators reject any claims lacking citations; and the Judge is evidence-bounded, prohibited from introducing external facts.
- **Q3: What makes the rebuttal round bounded?**  
  *Answer:* In unconstrained chat, agents loop indefinitely. We implemented a 1-turn rebuttal algorithm: `rank_arguments` identifies the opponent's strongest point, and each debater executes exactly one response targeting that specific claim. Time complexity is $O(1)$.
- **Q4: How does the Risk Agent veto work under the hood?**  
  *Answer:* The Risk Agent computes an empirical risk score across leverage, solvency, and regulatory flags. If the score $\ge 0.65$ or a covenant breach occurs, `enforce_risk_veto` programmatically overrides the Judge's provisional verdict to `HOLD`.
- **Q5: What frameworks and technologies did you use?**  
  *Answer:* Python 3.13, Microsoft Semantic Kernel adapter, FastAPI backend, SQLite database, Pydantic v2 data models, and an HTML5/CSS3/JavaScript responsive web interface.

#### Presenter Notes & Viva Talking Points (30 Seconds):
> *"To conclude, ThesisForge AI is not a generic LLM wrapper. It is a rigorously engineered, evidence-grounded multi-agent system that fulfills 100% of the CSE476 Project 2 Q18 requirements.*  
> *The codebase is modular, verified by 45 automated tests, fully documented, and ready for examination. Thank you, and I am now ready for your questions."*
