"""Test suite for Stock Universe expansion, filtering, anti-fabrication, and evidence isolation."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.models import Asset
from database.repository import Repository
from database.seed_data import seed_database
from orchestration.workflow import InvestmentCommitteeOrchestrator

client = TestClient(app)

TARGET_REAL_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "LT",
    "BHARTIARTL",
    "ITC",
    "SBIN",
    "TATAMOTORS",
    "HINDUNILVR",
]

BENCHMARK_DEMO_SYMBOLS = [
    "SOLARIS",
    "ZENITH",
    "APEX",
]


@pytest.fixture(scope="module", autouse=True)
def ensure_seed_data():
    repo = Repository()
    seed_database(repo)


def test_universe_contains_minimum_11_real_stocks_plus_benchmarks():
    """Verify that all 11 requested real NSE stocks and 3 synthetic demo stocks exist."""
    res = client.get("/api/v1/assets")
    assert res.status_code == 200
    assets = res.json()
    assert len(assets) >= 14

    symbol_map = {a["symbol"]: a for a in assets}

    # Verify all 11 real companies exist
    for sym in TARGET_REAL_SYMBOLS:
        assert sym in symbol_map, f"Target real stock {sym} missing from asset universe."
        assert symbol_map[sym]["dataset_type"] == "real_listed"
        assert symbol_map[sym]["exchange"] == "NSE"

    # Verify 3 academic demo fixtures exist and are distinctly marked
    for sym in BENCHMARK_DEMO_SYMBOLS:
        assert sym in symbol_map, f"Benchmark stock {sym} missing from asset universe."
        assert symbol_map[sym]["dataset_type"] == "synthetic_demo"


def test_unique_ticker_symbols():
    """Verify that every ticker symbol in the repository is unique."""
    res = client.get("/api/v1/assets")
    assert res.status_code == 200
    assets = res.json()
    symbols = [a["symbol"] for a in assets]
    assert len(symbols) == len(set(symbols)), "Duplicate ticker symbols detected in asset universe!"


def test_asset_search_and_filtering_api():
    """Test multi-field search and filtering on the /api/v1/assets endpoint."""
    # 1. Search by symbol
    res_rel = client.get("/api/v1/assets?search=RELIANCE")
    assert res_rel.status_code == 200
    rel_assets = res_rel.json()
    assert len(rel_assets) == 1
    assert rel_assets[0]["symbol"] == "RELIANCE"

    # 2. Search by company name keyword
    res_tata = client.get("/api/v1/assets?search=Tata")
    assert res_tata.status_code == 200
    tata_symbols = [a["symbol"] for a in res_tata.json()]
    assert "TCS" in tata_symbols
    assert "TATAMOTORS" in tata_symbols

    # 3. Filter by dataset_type
    res_real = client.get("/api/v1/assets?dataset_type=real_listed")
    assert res_real.status_code == 200
    assert len(res_real.json()) >= 11
    assert all(a["dataset_type"] == "real_listed" for a in res_real.json())

    res_demo = client.get("/api/v1/assets?dataset_type=synthetic_demo")
    assert res_demo.status_code == 200
    assert len(res_demo.json()) == 3
    assert all(a["dataset_type"] == "synthetic_demo" for a in res_demo.json())

    # 4. Filter by sector
    res_it = client.get("/api/v1/assets?sector=Information Technology")
    assert res_it.status_code == 200
    it_symbols = [a["symbol"] for a in res_it.json()]
    assert "TCS" in it_symbols
    assert "INFY" in it_symbols
    assert "APEX" in it_symbols


def test_document_status_and_anti_fabrication_labeling():
    """Verify companies without authentic disclosures are strictly labeled pending."""
    res = client.get("/api/v1/assets")
    assets = res.json()
    symbol_map = {a["symbol"]: a for a in assets}

    # Companies with authentic filings uploaded
    for sym in ["RELIANCE", "TCS", "INFY", "TATAMOTORS"]:
        asset = symbol_map[sym]
        assert asset["document_count"] >= 1, f"{sym} should have authentic documents ingested."
        assert asset["document_status"] == "indexed"

    # Companies awaiting primary filings: must NOT have fabricated documents
    pending_symbols = ["HDFCBANK", "ICICIBANK", "LT", "BHARTIARTL", "ITC", "SBIN", "HINDUNILVR"]
    for sym in pending_symbols:
        asset = symbol_map[sym]
        assert asset["document_count"] == 0, f"{sym} must not have fabricated documents."
        assert asset["document_status"] == "documents_pending"


def test_graceful_handling_of_pending_document_company():
    """Verify research run on a pending-document stock safely defaults to HOLD without crashing."""
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)

    hdfc_asset = repo.get_asset("HDFCBANK")
    assert hdfc_asset is not None

    # Run orchestrator on asset with 0 documents
    report = orch.run(hdfc_asset.id)
    assert report is not None
    assert report.recommendation == "HOLD"
    assert report.asset["symbol"] == "HDFCBANK"
    assert "No authentic filings available" in report.deciding_reasons[0]["reason"]
    assert report.strongest_bull_argument["evidence_ids"] == []

    # Check run record in repository
    run_record = repo.get_run(report.run_id)
    assert run_record.status == "INSUFFICIENT_EVIDENCE"


def test_strict_evidence_isolation_across_companies():
    """Verify that evidence items generated for Company A never leak into Company B's ledger."""
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)

    reliance_asset = repo.get_asset("RELIANCE")
    infy_asset = repo.get_asset("INFY")

    report_rel = orch.run(reliance_asset.id)
    report_infy = orch.run(infy_asset.id)

    rel_ev = repo.get_evidence_for_run(report_rel.run_id)
    infy_ev = repo.get_evidence_for_run(report_infy.run_id)

    assert len(rel_ev) > 0, "Reliance run should extract evidence from Reliance filing."
    assert len(infy_ev) > 0, "Infosys run should extract evidence from Infosys filing."

    # Verify that all documents in Reliance evidence belong strictly to Reliance
    for ev in rel_ev:
        assert "reliance" in ev.document_name.lower() or "rli" in ev.document_name.lower()
        assert "infosys" not in ev.document_name.lower()
        assert "tata" not in ev.document_name.lower()

    # Verify that all documents in Infosys evidence belong strictly to Infosys
    for ev in infy_ev:
        assert "infosys" in ev.document_name.lower() or "infy" in ev.document_name.lower()
        assert "reliance" not in ev.document_name.lower()


def test_dynamic_asset_registration_api():
    """Verify adding a new company dynamically via POST /api/v1/assets without modifying code."""
    new_asset_data = {
        "name": "Asian Paints Limited",
        "symbol": "ASIANPAINT",
        "exchange": "NSE",
        "isin": "INE021A01026",
        "sector": "Consumer Goods & Paints",
        "description": "Leading Indian decorative and industrial coatings company.",
        "dataset_type": "real_listed",
        "document_status": "documents_pending",
    }
    res = client.post("/api/v1/assets", json=new_asset_data)
    assert res.status_code == 201
    created = res.json()
    assert created["symbol"] == "ASIANPAINT"
    assert created["document_status"] == "documents_pending"

    # Verify it can be retrieved
    res_get = client.get("/api/v1/assets/ASIANPAINT")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Asian Paints Limited"
