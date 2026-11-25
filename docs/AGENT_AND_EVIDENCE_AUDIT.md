# THESISFORGE AI — MULTI-AGENT ARCHITECTURE & EVIDENCE AUDIT

## 1. Multi-Agent Committee Workflow

ThesisForge AI implements the full **CSE476 Q18 multi-agent investment research workflow**, enhanced with specialized institutional risk and valuation tools.

```
       [Document Ingestion & RAG Ledger]
                       │
             ┌─────────▼─────────┐
             │   Research Agent  │
             └─────────┬─────────┘
                       │ (Structured Evidence Pack)
             ┌─────────┴─────────┐
             ▼                   ▼
      ┌──────────────┐    ┌──────────────┐
      │  Bull Agent  │    │  Bear Agent  │
      └──────┬───────┘    └──────┬───────┘
             │                   │
             └─────────┬─────────┘
                       ▼
             ┌───────────────────┐
             │  Rebuttal Handler │
             └─────────┬─────────┘
                       ▼
             ┌───────────────────┐
             │    Risk Agent     │ ◄─── (Independent Audit & Veto)
             └─────────┬─────────┘
                       ▼
             ┌───────────────────┐
             │    Judge Agent    │
             └─────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │Citation Validator │
             └─────────┬─────────┘
                       ▼
        [Final Report & Signal Card]
```

---

## 2. Agent Responsibilities & Tool Matrix

| Agent | Responsibility | Inbuilt Python Tools |
|---|---|---|
| **Research Agent** | Parses document chunks, assigns deterministic evidence codes (`EV-001`), filters by financial topics. | `create_evidence_pack`, `get_evidence_by_topic`, `get_financial_facts` |
| **Bull Agent** | Synthesizes affirmative growth thesis, capacity expansion, competitive moat; strictly cites evidence codes. | `get_financial_facts`, `get_evidence_by_topic`, `validate_claim_support` |
| **Bear Agent** | Identifies solvency stress, margin compression, covenant breaches, reporting inconsistencies. | `get_risk_evidence`, `get_contradictory_evidence`, `validate_claim_support` |
| **Rebuttal Handler** | Conducts adversarial cross-examination round; attacks opposing thesis points with direct counter-evidence. | `execute_rebuttal_round`, `rank_rebuttal_arguments`, `check_rebuttal_relevance` |
| **Risk Agent** | Independent safety auditor; computes risk score, checks mandatory disclosure presence, evaluates covenant compliance. | `calculate_risk_score`, `check_required_evidence`, `check_risk_thresholds` |
| **Judge Agent** | Synthesizes final verdict (`BUY`, `HOLD`, `AVOID`), assesses argument strength, enforces Risk Veto overrides. | `get_validated_arguments`, `validate_all_citations`, `get_decision_policy`, `enforce_risk_veto` |

---

## 3. Evidence Ledger, RAG & Anti-Hallucination

1. **Passage Chunking & Hashing**:
   - Documents are split into semantic paragraphs (25–250 characters).
   - Each passage generates an immutable SHA-256 `content_hash`. Duplicate passages across filings are automatically deduplicated.
   - Passages are assigned sequential identifiers (`EV-001`, `EV-002`, ...) scoped uniquely per research run.
2. **Strict Citation Validation**:
   - Claims formulated by Bull, Bear, and Judge agents MUST cite valid evidence IDs present in the run's evidence ledger.
   - Any reference to an unknown ID is rejected by `validate_all_citations`.
3. **Contradiction Engine**:
   - Discrepancy detector cross-references reported figures across documents (revenue, ARR, EBITDA, debt, margins).
   - Classifies conflicts into `AUDITED_VS_UNAUDITED_PR_CONFLICT` or `MULTI_DOCUMENT_DISCREPANCY`.
   - Demonstrated in the APEX Technologies benchmark where statutory audited Q3 accounts disclose Annual Recurring Revenue (ARR) of ₹185 crore, while marketing press releases claim ₹240 crore.

---

## 4. Dual Risk Policy Modes (Academic vs Product)

The Risk Agent is equipped with an immutable safety veto triggered when:
- `calculated_risk_score >= policy_threshold` (default 0.65), OR
- Any critical risk flag is raised (`LEVERAGE_COVENANT_BREACH`, `REGULATORY_INVESTIGATION`, `GOING_CONCERN_WARNING`, `SOLVENCY_DISTRESS`).

### Policy Mode Matrix

| Feature | Academic Assignment Mode (`academic_assignment`) | Product Policy Mode (`product_policy`) |
|---|---|---|
| **Primary Directive** | CSE476 Q18 Specification | Institutional Execution Guardrail |
| **Veto Override Target** | Forces recommendation to **`HOLD`** | Forces recommendation to **`AVOID`** |
| **Execution Permission** | `PERMIT_WITH_RESTRICTION` | `BLOCK` |
| **Rationale** | Preserves academic debate evaluation without premature capital commitment. | Strict capital preservation: safety veto prohibits holding distressed assets. |
| **Signal Actionability** | Inactionable (`is_actionable = False`) | Inactionable (`is_actionable = False`) |

---

## 5. Tamper-Evident Run Event Logging

Every workflow state transition and tool invocation is recorded into an append-only cryptographic event chain in SQLite and JSONL:

$$\text{Event Hash}_t = \text{SHA256}\left(\text{run\_id} : \text{seq} : \text{timestamp} : \text{event\_type} : \text{agent} : \text{payload\_json} : \text{Event Hash}_{t-1}\right)$$

Where $\text{Event Hash}_0 = \text{"GENESIS\_00000000000000000000000000000000"}$.

Any modification to event payloads or previous hashes breaks the cryptographic chain and is detected by `repo.verify_run_log_integrity(run_id)`.
All 202 production research runs in the audit database have verified valid hash chains (`all_valid: true`).
