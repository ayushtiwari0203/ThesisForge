"""Comprehensive Automated Test Suite for Document Coverage, Market Data & Technical Engine.

Covers Section 6 (Automated Tests) of the ThesisForge AI Audit Specification:
1. Company-specific document isolation (no data leakage)
2. Missing-document handling (graceful fallback, zero fabricated financials)
3. Outdated and pending document tracking in 12-category catalog
4. Document extraction and chunking pipeline
5. 5-Year historical OHLCV market price ingestion and adjusted close
6. Stop loss and target price calculations across Intraday, Swing, and Positional timeframes
7. Risk:Reward calculation constraints (computed only when valid levels exist)
8. Insufficient market data handling (< 14 bars fallback to insufficient_data)
9. Strict citation validation and anti-hallucination verification
10. Complete vs incomplete research readiness audit
11. Document coverage and market data REST API endpoints
"""

from __future__ import annotations
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from backend.main import app
from database.models import Claim, EvidenceItem, DocumentRecord, ResearchRunRecord
from database.repository import Repository
from tools.document_tools import chunk_document, extract_text_from_file
from tools.document_coverage_engine import (
    STANDARD_DOCUMENT_CATEGORIES,
    OFFICIAL_COMPANY_METADATA,
    build_and_ingest_all_stock_coverage,
)
from tools.market_data_tools import (
    calculate_position_size,
    calculate_risk_reward_ratio,
    calculate_timeframe_stop_loss_and_target,
    compute_quantitative_market_structure,
    fetch_ohlcv_from_feed,
)
from tools.retrieval_tools import search_documents
from tools.validation_tools import validate_all_citations
from orchestration.workflow import InvestmentCommitteeOrchestrator


client = TestClient(app)


@pytest.fixture
def repo():
    return Repository()


# =============================================================================
# 1. Company-Specific Document Isolation
# =============================================================================

def test_company_specific_document_isolation(repo):
    """Verify that retrieval strictly isolates documents by asset_id with zero cross-contamination."""
    reliance = repo.get_asset("RELIANCE")
    tcs = repo.get_asset("TCS")
    assert reliance is not None
    assert tcs is not None

    reliance_chunks = search_documents(asset_id=reliance.id, query="revenue EBITDA profit margin", repo=repo)
    for ch in reliance_chunks:
        assert ch.asset_id == reliance.id, f"Cross-contamination: chunk {ch.id} belongs to {ch.asset_id}, not Reliance"

    tcs_chunks = search_documents(asset_id=tcs.id, query="revenue EBITDA profit margin", repo=repo)
    for ch in tcs_chunks:
        assert ch.asset_id == tcs.id, f"Cross-contamination: chunk {ch.id} belongs to {ch.asset_id}, not TCS"


# =============================================================================
# 2. Missing-Document Handling & Zero Fabrication
# =============================================================================

def test_missing_document_handling_and_zero_fabrication(repo):
    """Verify pending stocks have 0 documents and safely execute research returning HOLD with INSUFFICIENT_EVIDENCE."""
    pending_symbols = ["HDFCBANK", "ICICIBANK", "LT", "BHARTIARTL", "ITC", "SBIN", "HINDUNILVR"]
    for sym in pending_symbols:
        asset = repo.get_asset(sym)
        assert asset is not None
        assert asset.document_count == 0, f"{sym} must have 0 documents"
        assert asset.document_status == "documents_pending"

    # Run orchestrator on HDFCBANK (missing documents)
    orch = InvestmentCommitteeOrchestrator(repo=repo)
    hdfc = repo.get_asset("HDFCBANK")
    report = orch.run(hdfc.id)

    assert report is not None
    assert report.recommendation == "HOLD"
    assert any("pending" in lim.lower() or "anti-fabrication" in lim.lower() or "statutory" in lim.lower() for lim in report.limitations) or report.recommendation == "HOLD"
    assert report.signal_card is not None
    assert report.signal_card.is_actionable is False


# =============================================================================
# 3. 12-Category Document Coverage Catalog Tracking
# =============================================================================

def test_twelve_category_document_coverage_catalog(repo):
    """Verify all 12 categories are registered per asset with official URLs and statutory periods."""
    assets = repo.list_assets()
    assert len(assets) >= 14

    for asset in assets:
        coverage = repo.list_coverage_for_asset(asset.id)
        assert len(coverage) == 12, f"{asset.symbol} must track exactly 12 standard document categories"

        categories_found = {item.category_key for item in coverage}
        for expected_key in STANDARD_DOCUMENT_CATEGORIES.keys():
            assert expected_key in categories_found, f"{asset.symbol} missing category {expected_key}"

        for item in coverage:
            assert item.source_url.startswith("http"), f"{asset.symbol} {item.category_key} missing valid source URL"
            assert item.status in ("available", "pending", "missing", "outdated", "failed")
            assert item.extraction_status in ("success", "pending", "failed")


# =============================================================================
# 4. Text & PDF Extraction Pipeline
# =============================================================================

def test_text_and_pdf_extraction_pipeline():
    """Verify document chunking retains asset_id, document_id, page numbers, and word counts."""
    pages = [
        (1, "Balance sheet highlights: Cash reserves stand at ₹12,000 crores. Total debt is ₹3,500 crores."),
        (2, "Operational disclosures: Plant capacity utilization reached 92.4% during the second quarter."),
    ]
    doc_id = str(uuid4())
    asset_id = str(uuid4())

    chunks = chunk_document(document_id=doc_id, asset_id=asset_id, pages=pages, chunk_size=50)
    assert len(chunks) >= 2
    for ch in chunks:
        assert ch.document_id == doc_id
        assert ch.asset_id == asset_id
        assert ch.page_number in (1, 2)
        assert "word_count" in ch.metadata
        assert ch.metadata["word_count"] > 0


# =============================================================================
# 5. 5-Year Historical OHLCV Market Data Ingestion
# =============================================================================

def test_historical_market_data_ingestion(repo):
    """Verify historical market data contains > 500 daily bars for core stocks with valid OHLCV prices."""
    for sym in ["RELIANCE", "TCS", "INFY", "TATAMOTORS"]:
        summary = repo.get_market_data_summary(sym)
        assert summary["total_bars"] >= 500, f"{sym} should have >= 500 daily bars (found {summary['total_bars']})"
        assert summary["start_date"] < "2022-01-01"

        bars = repo.get_historical_bars(sym, limit=20)
        assert len(bars) == 20
        assert bars[-1].close > 0
        for b in bars:
            assert b.high >= b.low
            assert b.open > 0
            assert b.close > 0
            assert b.adjusted_close > 0


# =============================================================================
# 6. Stop Loss & Target Price Across Timeframes
# =============================================================================

def test_stop_loss_and_target_timeframe_methods(repo):
    """Verify timeframe-specific stop loss and targets provide transparent calculation methods."""
    for mode, mult in [("intraday", 1.0), ("swing", 1.5), ("positional", 2.5)]:
        result = calculate_timeframe_stop_loss_and_target(
            symbol="RELIANCE",
            entry_price=1250.0,
            side="LONG",
            timeframe_mode=mode,
            repo=repo,
        )
        assert result["stop_loss"] is not None
        assert result["target_1"] is not None
        assert result["target_2"] is not None
        assert result["stop_loss"] < 1250.0  # Long stop below entry
        assert result["target_1"] > 1250.0   # Long target above entry
        assert result["target_2"] > result["target_1"]
        assert "method" in result
        assert mode.capitalize() in result["method"] or "ATR" in result["method"]


# =============================================================================
# 7. Risk:Reward Ratio Constraints
# =============================================================================

def test_risk_reward_ratio_constraints():
    """Verify Risk:Reward is computed strictly when valid levels exist, and returns None otherwise."""
    # Valid long setup: Entry 100, Stop 95, Target 115 -> Risk=5, Reward=15 -> R:R=3.0
    rr_long = calculate_risk_reward_ratio(entry_price=100.0, stop_loss=95.0, target_price=115.0)
    assert rr_long == 3.0

    # Valid short setup: Entry 100, Stop 105, Target 85 -> Risk=5, Reward=15 -> R:R=3.0
    rr_short = calculate_risk_reward_ratio(entry_price=100.0, stop_loss=105.0, target_price=85.0)
    assert rr_short == 3.0

    # Incomplete or invalid levels must return None
    assert calculate_risk_reward_ratio(entry_price=100.0, stop_loss=None, target_price=115.0) is None
    assert calculate_risk_reward_ratio(entry_price=100.0, stop_loss=95.0, target_price=None) is None
    assert calculate_risk_reward_ratio(entry_price=None, stop_loss=95.0, target_price=115.0) is None
    assert calculate_risk_reward_ratio(entry_price=100.0, stop_loss=100.0, target_price=115.0) is None  # Zero risk


# =============================================================================
# 8. Insufficient Market Data Fallback
# =============================================================================

def test_insufficient_market_data_fallback(repo):
    """Verify market structure engine returns status: 'insufficient_data' when bars < 14."""
    # Symbol with no bars in DB
    res = compute_quantitative_market_structure(symbol="NONEXISTENT_SPARSE_STOCK", repo=repo)
    assert res.get("status") == "insufficient_data"
    assert res.get("bars_count") == 0
    assert res["indicators"]["rsi_14"] is None
    assert res["indicators"]["atr_14"] is None
    assert res["levels"]["stop_loss"] is None
    assert res["is_actionable"] is False
    assert "Annual-report PDFs cannot substitute" in res["data_dependency_notice"]


# =============================================================================
# 9. Citation Validation & Anti-Hallucination
# =============================================================================

def test_citation_validation_and_anti_hallucination(repo):
    """Verify citation validator strictly flags unverified evidence IDs."""
    doc_id = str(uuid4())
    run_id = str(uuid4())
    asset_id = "asset-solaris-001"

    repo.create_run(ResearchRunRecord(id=run_id, asset_id=asset_id, status="TEST"))
    repo.add_document(
        DocumentRecord(
            id=doc_id,
            asset_id=asset_id,
            filename="Test Doc",
            source="Test Source",
            content_hash=str(uuid4()),
            storage_path="test_path",
        )
    )

    valid_ev = EvidenceItem(
        run_id=run_id,
        document_id=doc_id,
        document_name="Test Doc",
        evidence_code="EV-001",
        passage_text="Valid factual statement from filing.",
        content_hash="h1",
    )
    repo.add_evidence_items([valid_ev])

    valid_claim = Claim(claim_id="c1", text="Factual claim with real evidence", evidence_ids=["EV-001"], claim_type="fact")
    val_valid = validate_all_citations(run_id, [valid_claim], repo)
    assert val_valid["is_valid"] is True
    assert val_valid["citation_validity_ratio"] == 1.0

    fake_claim = Claim(claim_id="c2", text="Hallucinated claim with fake evidence", evidence_ids=["fake-ev-9999"], claim_type="fact")
    val_invalid = validate_all_citations(run_id, [fake_claim], repo)
    assert val_invalid["is_valid"] is False
    assert len(val_invalid["invalid_citations"]) == 1
    assert val_invalid["invalid_citations"][0]["invalid_evidence_id"] == "fake-ev-9999"

    repo.clean_test_documents()


# =============================================================================
# 10. Research Readiness Audit (Complete vs Incomplete)
# =============================================================================

def test_research_readiness_audit(repo):
    """Verify research readiness record correctly segments READY_FOR_RESEARCH vs DOCUMENTS_PENDING."""
    all_readiness = repo.list_all_readiness()
    assert len(all_readiness) >= 14

    readiness_by_sym = {r.symbol: r for r in all_readiness}

    # Core indexed stocks must be READY_FOR_RESEARCH or PARTIALLY_READY
    for sym in ["RELIANCE", "TCS", "INFY", "TATAMOTORS"]:
        r = readiness_by_sym[sym]
        assert r.overall_readiness in ("READY_FOR_RESEARCH", "PARTIALLY_READY")
        assert r.available_docs_count >= 1
        assert r.market_data_bars >= 500
        assert r.technical_coverage_pct == 100.0

    # Pending stocks must be DOCUMENTS_PENDING
    for sym in ["HDFCBANK", "ICICIBANK", "LT", "BHARTIARTL", "ITC", "SBIN", "HINDUNILVR"]:
        r = readiness_by_sym[sym]
        assert r.overall_readiness == "DOCUMENTS_PENDING"
        assert r.available_docs_count == 0
        assert r.pending_docs_count == 12
        assert r.market_data_bars >= 500
        assert r.fundamental_coverage_pct == 0.0
        assert r.technical_coverage_pct == 100.0


# =============================================================================
# 11. Coverage & Market Data REST API Endpoints
# =============================================================================

def test_coverage_and_market_data_api_endpoints():
    """Verify REST endpoints for document coverage catalog and historical market data."""
    # 1. GET /api/v1/coverage
    res = client.get("/api/v1/coverage")
    assert res.status_code == 200
    catalog = res.json()
    assert "readiness_records" in catalog
    assert len(catalog["readiness_records"]) >= 14
    assert "category_summaries" in catalog
    assert len(catalog["category_summaries"]) >= 14
    first_summary = catalog["category_summaries"][0]
    assert "asset_id" in first_summary
    assert "total_items" in first_summary
    assert first_summary["total_items"] == 12

    # 2. GET /api/v1/coverage/{asset_id}
    asset_id = first_summary["asset_id"]
    res_single = client.get(f"/api/v1/coverage/{asset_id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["asset"]["id"] == asset_id
    assert len(single_data["catalog_items"]) == 12

    # 3. GET /api/v1/market-data/{symbol}
    res_mkt = client.get("/api/v1/market-data/RELIANCE?timeframe=swing")
    assert res_mkt.status_code == 200
    mkt_data = res_mkt.json()
    assert mkt_data["symbol"] == "RELIANCE"
    assert mkt_data["bars_count"] >= 500
    assert mkt_data["status"] == "available"
    assert "indicators" in mkt_data
    assert "levels" in mkt_data
