# THESISFORGE AI — DATA INTEGRITY & AUDIT RECONCILIATION REPORT

## 1. Executive Summary

Data integrity is the foundational design pillar of **ThesisForge AI**. Under SEBI research analyst guidelines and academic anti-hallucination mandates, financial data must never be fabricated, simulated from incorrect instruments, or conflated with missing-data fallbacks.

This report documents the rigorous data audit and corrections applied across:
1. Synthetic benchmark ISIN cleansing
2. Corporate identity and restructuring (Tata Motors Demerger)
3. Decoupling missing-document semantics from market data (HDFCBANK resolution)
4. Comprehensive document count reconciliation and lifecycle stage definitions

---

## 2. Company Identity & ISIN Cleansing

### 2.1 Synthetic Benchmark Cleansing
Prior to the audit, the three synthetic stress-test benchmark companies (`SOLARIS`, `ZENITH`, `APEX`) had placeholder ISIN numbers formatted like real Indian ISINs (`INE123A01020`, `INE456B01030`, `INE789C01040`). Although intended for demonstration, realistic-looking ISINs for non-existent corporate entities violate strict anti-fabrication standards.

**Correction Implemented**:
- Synthetic assets (`SOLARIS`, `ZENITH`, `APEX`) were cleansed across `seed_data.py` and the SQLite database.
- ISIN is now strictly set to `None`.
- `dataset_type` is explicitly marked as `'synthetic_demo'`, and `exchange` is marked as `'BENCHMARK'`.

### 2.2 Tata Motors Demerger Identity (TMPV vs TMCV)
Tata Motors Limited underwent a significant corporate restructuring, demerging its commercial vehicles business (`TMCV`) from its passenger vehicles, electric vehicles, and Jaguar Land Rover business (`TMPV`).

**Correction Implemented**:
- `TATAMOTORS` asset record updated with an explicit corporate restructuring note:
  > *"Corporate Restructuring Demerger: Tata Motors Limited demerged into two separate listed entities — TMPV (Passenger Vehicles, Electric Mobility, and Jaguar Land Rover) and TMCV (Commercial Vehicles). Research analysis reflects consolidated statutory historical filings."*
- Exchange data mappings in `market_data_tools.py` anchored to `TMPV.NS`.

---

## 3. Missing-Data Semantics Decoupling (The HDFCBANK Issue)

### 3.1 Problem Identification
In `orchestration/workflow.py`, when a company lacked ingested primary filings (`if not docs:`):
1. `current_reference_price` was hardcoded to `0.0`.
2. `risk_score` was hardcoded to `0.0`.
3. `technical_context` was hardcoded to `None`.

This created a severe architectural flaw:
- **False Price Suppression**: HDFCBANK had 1,236 real historical daily OHLCV bars stored in the database. Suppressing price to `0.0` was factually inaccurate.
- **Misleading Risk Score**: Setting `risk_score = 0.0` communicated *zero risk* (safe/pristine), when in reality fundamental risk was *completely unassessed* due to absent filings.
- **Unnecessary Technical Blindness**: Technical momentum and regime indicators are purely mathematical functions of price and volume bars and do not require statutory filings.

### 3.2 Implemented Resolution
1. **Real Price Retrieval**: If historical bars exist, the latest close price (~₹809.25 / ₹1,745 adjusted) is retrieved and displayed on the non-actionable Signal Card.
2. **Technical Readiness Activation**: When $\ge 14$ bars exist, `analyze_technical_structure` executes deterministically and populates `technical_context`.
3. **Transparent Risk Semantics**: `risk_score` is set to `None`, and `risk_status` is explicitly set to `"NOT_ASSESSED — Primary statutory filings pending"`.
4. **Anti-Fabrication Enforcement**: Recommendation remains `HOLD` with `status = "INSUFFICIENT_EVIDENCE"` to prevent generating ungrounded financial claims.

---

## 4. Document Count Reconciliation & Lifecycle Stages

### 4.1 Master Reconciliation Matrix

| Layer | Count | Description |
|---|---|---|
| **Monitored Category Slots** | **180** | 15 assets × 12 standard filing categories in `document_coverage_catalog` |
| **Physical Files Indexed** | **9** | Authentic primary statutory text/PDF filings stored in `documents` table |
| **Verified Extracted Disclosure Sections** | **28** | Discrete financial statements, balance sheets, auditor reviews across companies |
| **Catalog Slots Covered by Primary Filings** | **51** | Monitored categories fulfilled through verified primary statutory filings |
| **Pending Category Filings** | **129** | Secondary categories retaining official NSE/IR links awaiting on-demand upload |
| **Total Asset Universe** | **15** | 12 real listed NSE equities + 3 synthetic stress benchmarks |

### 4.2 Explicit 8 Lifecycle Stages
To eliminate any ambiguity between raw files, extracted sections, and pending disclosures, every document catalog entry is assigned one of eight explicit lifecycle stages:

1. `SOURCE_DISCOVERED`: Official disclosure source URL identified on NSE or corporate IR portal.
2. `DOCUMENT_DOWNLOADED`: Document retrieved and stored in temporary physical storage.
3. `DOCUMENT_DOWNLOADED_VERIFIED`: Document checksum (SHA-256) verified and anti-tamper logged.
4. `DOCUMENT_EXTRACTED`: Document text parsed, chunked, and mapped to financial periods.
5. `DOCUMENT_EXTRACTED_INDEXED`: Extracted chunks indexed into SQLite RAG ledger and ready for agent retrieval.
6. `DOCUMENT_PENDING`: Ingestion pending on-demand upload; zero synthetic claims fabricated.
7. `DOCUMENT_UNAVAILABLE`: Filing not published by issuer or not applicable to corporate structure.
8. `DOCUMENT_REJECTED`: Ingested document failed format validation, checksum match, or relevance thresholds.

---

## 5. Verification & REST Endpoint

The database reconciliation and cryptographic integrity can be audited live via:
- `GET /api/v1/audit/reconciliation`: Returns total assets (15), physical documents indexed (9), catalog slots (180), and lifecycle distribution.
- `GET /api/v1/audit/integrity`: Returns cryptographic hash-chain verification across all production runs (`all_valid: true`).
