"""Integration tests for FastAPI endpoints (SRS Section 9.1)."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.repository import Repository
from database.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def init_db():
    repo = Repository()
    seed_database(repo)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ThesisForge AI"


def test_list_assets_endpoint():
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 3
    symbols = [a["symbol"] for a in assets]
    assert "SOLARIS" in symbols
    assert "ZENITH" in symbols
    assert "APEX" in symbols


def test_list_asset_documents_endpoint():
    response = client.get("/api/v1/assets/asset-solaris-001/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 2
    filenames = [d["filename"] for d in docs]
    assert any("solaris_annual_report" in fn for fn in filenames)


def test_create_and_fetch_research_run_endpoints():
    from orchestration.workflow import InvestmentCommitteeOrchestrator
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)
    report = orch.run("asset-solaris-001")

    res_status = client.get(f"/api/v1/research-runs/{report.run_id}")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "COMPLETED"

    res_report = client.get(f"/api/v1/research-runs/{report.run_id}/report")
    assert res_report.status_code == 200
    rep_data = res_report.json()
    assert rep_data["recommendation"] in ["BUY", "HOLD", "AVOID"]
    assert rep_data["strongest_bull_argument"]["claim"]

    res_trace = client.get(f"/api/v1/research-runs/{report.run_id}/trace")
    assert res_trace.status_code == 200
    trace_data = res_trace.json()
    assert trace_data["event_count"] >= 20
    assert trace_data["hash_chain_valid"] is True

    res_ev = client.get(f"/api/v1/research-runs/{report.run_id}/evidence")
    assert res_ev.status_code == 200
    ev_data = res_ev.json()
    assert ev_data["count"] > 0
    assert ev_data["evidence"][0]["evidence_code"].startswith("EV-")
