"""Comprehensive Test Suite for Audit Findings, Intelligence Improvements, and Data Integrity.

Validates:
1. Missing-data semantics decoupling (HDFCBANK market price & technical context preserved; fundamental risk NOT_ASSESSED)
2. Quantitative indicators: ADX, Supertrend, OBV, Donchian Channels, Gap Analysis, Classic Pivots
3. Position sizing constraints and Indian market transaction friction (Gross R:R vs Net R:R)
4. Sector-aware fundamental intelligence (Banking P/B vs non-applicable EV/EBITDA)
5. Dual risk policy modes: Academic Assignment (HOLD) vs Product Policy (AVOID)
6. Tamper-evident audit logging and hash-chain verification
7. Document lifecycle stages and reconciliation API endpoints
"""

import math
import pytest
from datetime import datetime, timezone

from database.models import (
    Asset,
    Claim,
    DocumentCoverageItem,
    JudgeDecision,
    RiskAssessment,
)
from database.repository import Repository
from orchestration.workflow import InvestmentCommitteeOrchestrator
from tools.market_data_tools import (
    calculate_indian_market_transaction_costs,
    calculate_position_size,
    calculate_risk_reward_ratio,
    compute_quantitative_market_structure,
)
from tools.technical_tools import (
    calculate_adx,
    calculate_classic_pivot_points,
    calculate_donchian_channels,
    calculate_obv,
    calculate_price_gaps,
    calculate_supertrend,
)
from tools.validation_tools import enforce_risk_veto
from tools.valuation_tools import evaluate_valuation_context


@pytest.fixture
def repo():
    return Repository()


def test_hdfcbank_missing_data_decoupling(repo):
    """Test that companies awaiting primary filings retain real market prices and technical structure."""
    assets = repo.list_assets(search="HDFCBANK")
    assert len(assets) > 0, "HDFCBANK must exist in the asset universe"
    hdfc = assets[0]

    orchestrator = InvestmentCommitteeOrchestrator(repo=repo)
    report = orchestrator.run(
        asset_id=hdfc.id,
        config={"research_mode": "swing", "risk_budget_rupees": 10000.0},
    )

    # 1. Recommendation must be HOLD in compliance with anti-fabrication
    assert report.recommendation == "HOLD"

    # 2. Reference price must be authentic (> 500), NOT 0.0
    assert report.signal_card is not None
    assert report.signal_card.current_reference_price > 500.0, (
        f"Expected real market price for HDFCBANK, got {report.signal_card.current_reference_price}"
    )

    # 3. Technical context must be populated because HDFCBANK has > 1000 daily OHLCV bars
    assert report.technical_context is not None, "Technical context should be available from market bars"
    assert report.technical_context.get("status") == "available"
    assert "adx_14" in report.technical_context.get("indicators", {})

    # 4. Fundamental risk score must be None (NOT 0.0 which falsely implies zero risk)
    assert report.risk_veto.get("score") is None, "Risk score must be None for unassessed pending asset"
    assert "NOT_ASSESSED" in report.risk_veto.get("reason", "") or "NOT_ASSESSED" in report.risk_veto.get("risk_status", "")


def test_adx_supertrend_obv_donchian_pivots_gaps():
    """Verify deterministic calculations for the expanded indicator suite."""
    # Synthetic trending price series
    closes = [100.0 + i * 2.0 for i in range(35)]
    highs = [c + 3.0 for c in closes]
    lows = [c - 2.0 for c in closes]
    opens = [closes[i - 1] if i > 0 else 100.0 for i in range(35)]
    volumes = [100000.0 + i * 5000.0 for i in range(35)]

    # 1. ADX
    adx_res = calculate_adx(highs, lows, closes, period=14)
    assert "adx" in adx_res
    assert "plus_di" in adx_res
    assert "minus_di" in adx_res
    assert adx_res["adx"] > 0
    assert adx_res["plus_di"] > adx_res["minus_di"], "In strong uptrend, +DI must exceed -DI"

    # 2. Supertrend
    st_res = calculate_supertrend(highs, lows, closes, period=10, multiplier=3.0)
    assert st_res["direction"] == "BULLISH"
    assert st_res["supertrend"] < closes[-1]

    # 3. OBV
    obv_res = calculate_obv(closes, volumes)
    assert obv_res["obv_trend"] == "ACCUMULATION"
    assert obv_res["obv"] > 0

    # 4. Donchian Channels
    donchian = calculate_donchian_channels(highs, lows, period=20)
    assert donchian["upper"] == max(highs[-20:])
    assert donchian["lower"] == min(lows[-20:])
    assert donchian["middle"] == round((donchian["upper"] + donchian["lower"]) / 2.0, 2)
    assert donchian["bandwidth_pct"] > 0

    # 5. Classic Pivots
    pivots = calculate_classic_pivot_points(high=150.0, low=140.0, close=145.0)
    expected_p = (150.0 + 140.0 + 145.0) / 3.0
    assert pivots["pivot"] == round(expected_p, 2)
    assert pivots["r1"] > pivots["pivot"]
    assert pivots["s1"] < pivots["pivot"]

    # 6. Price Gaps
    gap_opens = [100.0, 101.0, 108.0]
    gap_highs = [102.0, 103.0, 110.0]
    gap_lows = [99.0, 100.0, 106.0]
    gap_closes = [101.0, 102.0, 109.0]
    gaps = calculate_price_gaps(gap_opens, gap_highs, gap_lows, gap_closes)
    assert len(gaps) == 1
    assert gaps[0]["type"] == "GAP_UP"
    assert gaps[0]["gap_size"] == round(106.0 - 103.0, 2)


def test_position_sizing_constraints_and_transaction_friction():
    """Verify position sizing under risk, capital, and liquidity constraints alongside transaction costs."""
    # 1. Unconstrained by capital or liquidity
    qty_risk_only = calculate_position_size(
        entry_price=1000.0,
        stop_loss=950.0,
        risk_budget_rupees=10000.0,
    )
    assert qty_risk_only == 200  # 10000 / 50 = 200

    # 2. Constrained by capital (e.g., maximum portfolio capital 50,000)
    qty_cap_limited = calculate_position_size(
        entry_price=1000.0,
        stop_loss=950.0,
        risk_budget_rupees=10000.0,
        portfolio_capital=50000.0,
    )
    assert qty_cap_limited == 50  # 50000 / 1000 = 50

    # 3. Constrained by liquidity (1% of daily volume 2,000 = 20)
    qty_liq_limited = calculate_position_size(
        entry_price=1000.0,
        stop_loss=950.0,
        risk_budget_rupees=10000.0,
        avg_daily_volume=2000.0,
    )
    assert qty_liq_limited == 20  # min(200, 20) = 20

    # 4. Indian market transaction cost model
    friction = calculate_indian_market_transaction_costs(
        entry_price=1000.0,
        exit_price=1100.0,
        quantity=100,
        trade_type="DELIVERY",
    )
    assert friction["total_friction_rupees"] > 0
    assert friction["friction_per_share"] > 0
    # STT on delivery (0.1% on buy 100k + sell 110k = 210)
    assert friction["breakdown"]["stt"] == 210.0


def test_sector_aware_fundamental_intelligence():
    """Verify banking vs corporate fundamental valuation profile separation."""
    # 1. Banking Asset (HDFCBANK)
    hdfc_val = evaluate_valuation_context("HDFCBANK", sector="Banking & Financial Services")
    assert hdfc_val["status"] == "VERIFIED_FIXTURE"
    assert hdfc_val["price_to_book"] is not None
    assert hdfc_val["return_on_assets_pct"] is not None
    # EV/EBITDA and D/E must be structurally None for banks
    assert hdfc_val["ev_to_ebitda"] is None
    assert hdfc_val["debt_to_equity"] is None
    assert "non-applicable" in hdfc_val["metric_suitability_rationale"].lower()

    # 2. Corporate Asset (RELIANCE)
    rel_val = evaluate_valuation_context("RELIANCE", sector="Energy & Conglomerate")
    assert rel_val["status"] == "VERIFIED_FIXTURE"
    assert rel_val["ev_to_ebitda"] is not None
    assert rel_val["debt_to_equity"] is not None


def test_dual_risk_veto_policy_modes():
    """Verify that academic assignment mode forces HOLD, while product policy mode forces AVOID."""
    provisional = JudgeDecision(
        recommendation="BUY",
        strongest_bull_claim_id="C-01",
        strongest_bear_claim_id="C-02",
        deciding_reasons=[Claim(claim_id="C-01", text="Growth", claim_type="fact", evidence_ids=["EV-001"])],
        uncertainties=[],
        evidence_ids=["EV-001"],
    )

    risk_assess = RiskAssessment(
        score=0.85,
        threshold=0.65,
        veto=True,
        reasons=["Debt covenant breach", "Severe insolvency distress"],
        evidence_ids=["EV-002"],
        flags=["COVENANT_BREACH"],
    )

    # 1. Academic Assignment Mode -> HOLD
    academic_decision = enforce_risk_veto(provisional, risk_assess, policy_mode="academic_assignment")
    assert academic_decision.recommendation == "HOLD"
    assert academic_decision.veto_applied is True
    assert "HOLD" in academic_decision.deciding_reasons[0].text

    # 2. Product Policy Mode -> AVOID
    # Reset provisional
    provisional.recommendation = "BUY"
    provisional.deciding_reasons = [Claim(claim_id="C-01", text="Growth", claim_type="fact", evidence_ids=["EV-001"])]
    product_decision = enforce_risk_veto(provisional, risk_assess, policy_mode="product_policy")
    assert product_decision.recommendation == "AVOID"
    assert product_decision.veto_applied is True
    assert "AVOID" in product_decision.deciding_reasons[0].text
    assert "BLOCK" in product_decision.deciding_reasons[0].text


def test_audit_log_hash_chain_verification(repo):
    """Verify cryptographic audit trail integrity check."""
    integrity = repo.verify_all_run_logs_integrity()
    assert integrity["total_runs_checked"] >= 0
    assert integrity["all_valid"] is True


def test_reconciliation_endpoints_and_lifecycle_stages(repo):
    """Verify document coverage catalog lifecycle stages and API endpoints."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 1. Test /api/v1/audit/integrity
    resp_int = client.get("/api/v1/audit/integrity")
    assert resp_int.status_code == 200
    data_int = resp_int.json()
    assert "all_valid" in data_int
    assert data_int["all_valid"] is True

    # 2. Test /api/v1/audit/reconciliation
    resp_rec = client.get("/api/v1/audit/reconciliation")
    assert resp_rec.status_code == 200
    data_rec = resp_rec.json()
    assert data_rec["total_assets"] >= 14
    assert data_rec["monitored_catalog_slots"] == data_rec["total_assets"] * 12
    assert len(data_rec["lifecycle_stage_breakdown"]) > 0

    # 3. Test /api/v1/market-data/{symbol}
    resp_mkt = client.get("/api/v1/market-data/RELIANCE?timeframe=swing")
    assert resp_mkt.status_code == 200
    data_mkt = resp_mkt.json()
    assert data_mkt["status"] == "available"
    assert "adx_14" in data_mkt["indicators"]
    assert "supertrend" in data_mkt["indicators"]
    assert "obv" in data_mkt["indicators"]
    assert "net_reward_to_risk" in data_mkt["levels"]
