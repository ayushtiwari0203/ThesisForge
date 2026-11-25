"""Unit tests for evidence, chunking, citation validation, and audit log integrity (SRS Section 11.2)."""

import pytest
from uuid import uuid4
from database.models import Claim, EvidenceItem, JudgeDecision, RiskAssessment, DocumentRecord, ResearchRunRecord
from database.repository import Repository
from tools.document_tools import chunk_document, extract_text_from_file
from tools.retrieval_tools import search_documents
from tools.risk_tools import calculate_risk_score, check_risk_thresholds
from tools.validation_tools import enforce_risk_veto, rank_arguments, validate_all_citations


@pytest.fixture
def repo():
    return Repository()


def test_text_extraction_and_chunking():
    pages = [
        (1, "First page text outlining financial highlights and sales growth of 20%."),
        (2, "Second page detailing risk disclosures, operating liabilities, and debt covenants."),
    ]
    doc_id = str(uuid4())
    asset_id = str(uuid4())

    chunks = chunk_document(document_id=doc_id, asset_id=asset_id, pages=pages, chunk_size=50)

    assert len(chunks) >= 2
    for ch in chunks:
        assert ch.document_id == doc_id
        assert ch.asset_id == asset_id
        assert ch.page_number in [1, 2]
        assert "word_count" in ch.metadata


def test_retrieval_filters_by_selected_asset(repo):
    chunks_solaris = search_documents(asset_id="asset-solaris-001", query="revenue margin", repo=repo)
    for ch in chunks_solaris:
        assert ch.asset_id == "asset-solaris-001"

    chunks_zenith = search_documents(asset_id="asset-zenith-002", query="debt covenant", repo=repo)
    for ch in chunks_zenith:
        assert ch.asset_id == "asset-zenith-002"


def test_citation_validator_rejects_unknown_ids(repo):
    run_id = str(uuid4())
    doc_id = str(uuid4())

    repo.create_run(ResearchRunRecord(id=run_id, asset_id="asset-solaris-001", status="TEST"))
    repo.add_document(
        DocumentRecord(
            id=doc_id,
            asset_id="asset-solaris-001",
            filename="Test Doc",
            source="Test Source",
            content_hash=str(uuid4()),
            storage_path="test_path",
        )
    )

    real_items = [
        EvidenceItem(
            run_id=run_id,
            document_id=doc_id,
            document_name="Test Doc",
            evidence_code="EV-001",
            passage_text="Revenue grew by 25% to ₹500 crore.",
            content_hash="h1",
        ),
        EvidenceItem(
            run_id=run_id,
            document_id=doc_id,
            document_name="Test Doc",
            evidence_code="EV-002",
            passage_text="Operating margin expanded to 21%.",
            content_hash="h2",
        ),
    ]
    repo.add_evidence_items(real_items)

    valid_claim = Claim(
        claim_id="CLM-01",
        text="Revenue and margin grew solidly.",
        claim_type="fact",
        evidence_ids=["EV-001", "EV-002"],
    )
    val_valid = validate_all_citations(run_id, [valid_claim], repo)
    assert val_valid["is_valid"] is True
    assert val_valid["citation_validity_ratio"] == 1.0

    fake_claim = Claim(
        claim_id="CLM-02",
        text="Fabricated fact not in documents.",
        claim_type="fact",
        evidence_ids=["EV-999"],
    )
    val_invalid = validate_all_citations(run_id, [fake_claim], repo)
    assert val_invalid["is_valid"] is False
    assert len(val_invalid["invalid_citations"]) == 1
    assert val_invalid["invalid_citations"][0]["invalid_evidence_id"] == "EV-999"


def test_rebuttal_rank_arguments():
    claims = [
        Claim(claim_id="C1", text="Minor operational detail.", claim_type="interpretation", evidence_ids=["EV-001"]),
        Claim(claim_id="C2", text="Major revenue growth of 24.5% to ₹1200 crore.", claim_type="fact", evidence_ids=["EV-002", "EV-003"]),
    ]
    ranked = rank_arguments(claims)
    assert ranked[0].claim_id == "C2"


def test_risk_threshold_boundary_and_veto_override():
    low_eval = check_risk_thresholds(risk_score=0.40, flags=[], policy_threshold=0.65)
    assert low_eval["veto"] is False

    high_eval = check_risk_thresholds(risk_score=0.68, flags=[], policy_threshold=0.65)
    assert high_eval["veto"] is True

    crit_eval = check_risk_thresholds(risk_score=0.50, flags=["REGULATORY_INVESTIGATION"], policy_threshold=0.65)
    assert crit_eval["veto"] is True

    initial_decision = JudgeDecision(
        recommendation="BUY",
        strongest_bull_claim_id="BULL-01",
        strongest_bear_claim_id="BEAR-01",
        deciding_reasons=[Claim(claim_id="J1", text="Strong growth", claim_type="interpretation", evidence_ids=["EV-001"])],
        uncertainties=[],
        evidence_ids=["EV-001"],
    )
    risk_assessment = RiskAssessment(
        score=0.85,
        threshold=0.65,
        veto=True,
        reasons=["Excessive leverage breaches debt covenant."],
        evidence_ids=["EV-002"],
        flags=["LEVERAGE_COVENANT_BREACH"],
    )

    overridden = enforce_risk_veto(initial_decision, risk_assessment)
    assert overridden.recommendation == "HOLD"
    assert overridden.provisional_recommendation == "BUY"
    assert overridden.veto_applied is True


def test_append_only_log_hash_chaining(repo):
    run_id = str(uuid4())
    repo.create_run(ResearchRunRecord(id=run_id, asset_id="asset-solaris-001", status="TEST"))

    ev1 = repo.append_event(run_id, "EVENT_1", "Agent1", {"step": 1})
    ev2 = repo.append_event(run_id, "EVENT_2", "Agent2", {"step": 2})
    ev3 = repo.append_event(run_id, "EVENT_3", "Agent3", {"step": 3})

    assert ev1.previous_hash == "GENESIS_00000000000000000000000000000000"
    assert ev2.previous_hash == ev1.event_hash
    assert ev3.previous_hash == ev2.event_hash

    assert repo.verify_run_log_integrity(run_id) is True

    with repo._get_connection() as conn:
        conn.execute("UPDATE run_events SET payload = '{\"tampered\": true}' WHERE id = ?", (ev2.id,))
        conn.commit()

    assert repo.verify_run_log_integrity(run_id) is False
