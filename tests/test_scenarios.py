"""Mandatory Three Scenarios Test Suite for ThesisForge AI (SRS Section 11.1).

Covers:
  - Scenario A: Normal balanced debate
  - Scenario B: Risk Agent safety veto override to HOLD
  - Scenario C: Conflicting / insufficient evidence handling
"""

import pytest
from database.repository import Repository
from database.seed_data import seed_database
from orchestration.workflow import InvestmentCommitteeOrchestrator


@pytest.fixture(scope="module")
def setup_environment():
    repo = Repository()
    seed_database(repo)
    orchestrator = InvestmentCommitteeOrchestrator(repo=repo)
    return {"repo": repo, "orchestrator": orchestrator}


def test_scenario_a_normal_debate(setup_environment):
    orch: InvestmentCommitteeOrchestrator = setup_environment["orchestrator"]
    repo: Repository = setup_environment["repo"]

    report = orch.run(asset_id="asset-solaris-001")

    assert report.run_id is not None
    assert report.asset["symbol"] == "SOLARIS"
    assert report.recommendation in ["BUY", "HOLD", "AVOID"]

    assert report.strongest_bull_argument["claim"]
    assert len(report.strongest_bull_argument["evidence_ids"]) > 0

    assert report.strongest_bear_argument["claim"]
    assert len(report.strongest_bear_argument["evidence_ids"]) > 0

    assert report.bull_rebuttal["text"]
    assert len(report.bull_rebuttal["evidence_ids"]) > 0
    assert report.bear_rebuttal["text"]
    assert len(report.bear_rebuttal["evidence_ids"]) > 0

    assert len(report.deciding_reasons) >= 1
    for reason in report.deciding_reasons:
        assert reason["reason"]
        assert len(reason["evidence_ids"]) > 0

    evidence_items = repo.get_evidence_for_run(report.run_id)
    assert len(evidence_items) > 0
    for ev in evidence_items:
        assert ev.evidence_code.startswith("EV-")
        assert ev.passage_text
        assert ev.document_name

    events = repo.get_run_events(report.run_id)
    assert len(events) >= 20
    assert repo.verify_run_log_integrity(report.run_id) is True


def test_scenario_b_risk_veto(setup_environment):
    orch: InvestmentCommitteeOrchestrator = setup_environment["orchestrator"]
    repo: Repository = setup_environment["repo"]

    report = orch.run(asset_id="asset-zenith-002", config={"risk_veto_threshold": 0.65})

    assert report.risk_veto["triggered"] is True
    assert "REGULATORY_INVESTIGATION" in report.risk_veto["reason"] or "exceeds" in report.risk_veto["reason"]
    assert report.recommendation == "HOLD"

    deciding_texts = [r["reason"] for r in report.deciding_reasons]
    assert any("Risk Veto Enforced" in dt for dt in deciding_texts)

    events = repo.get_run_events(report.run_id)
    risk_tool_events = [e for e in events if "RiskAgent" in e.agent_or_tool]
    assert len(risk_tool_events) >= 3


def test_scenario_c_insufficient_or_conflicting_evidence(setup_environment):
    orch: InvestmentCommitteeOrchestrator = setup_environment["orchestrator"]
    repo: Repository = setup_environment["repo"]

    report = orch.run(asset_id="asset-apex-003")

    assert "inconsistency" in report.strongest_bear_argument["claim"].lower() or "conflict" in report.strongest_bear_argument["claim"].lower()
    assert report.recommendation == "HOLD"

    ledger_codes = {ev.evidence_code for ev in repo.get_evidence_for_run(report.run_id)}
    for r in report.deciding_reasons:
        for eid in r["evidence_ids"]:
            assert eid in ledger_codes, f"Evidence ID {eid} not found in run ledger!"
