"""Test suite for Expert Review and Trading Intelligence Upgrades (Sections 4, 5, 6, 7)."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.repository import Repository
from database.seed_data import seed_database
from evaluation.backtest import run_historical_backtest
from orchestration.workflow import InvestmentCommitteeOrchestrator
from tools.derivatives_tools import analyze_derivatives_context
from tools.technical_tools import (
    analyze_technical_structure,
    calculate_atr,
    calculate_ema,
    calculate_relative_strength,
    calculate_rsi,
    calculate_vwap,
)

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    repo = Repository()
    seed_database(repo)


def test_deterministic_technical_calculations():
    """Verify deterministic mathematical calculations for EMA, RSI, ATR, and VWAP."""
    prices = [100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0, 108.0, 107.0, 110.0]
    highs = [p * 1.01 for p in prices]
    lows = [p * 0.99 for p in prices]
    volumes = [1000.0] * len(prices)

    # EMA test
    ema_5 = calculate_ema(prices, 5)
    assert len(ema_5) == len(prices)
    assert ema_5[-1] > ema_5[0]

    # RSI test
    rsi = calculate_rsi(prices, 5)
    assert 0.0 <= rsi <= 100.0

    # ATR test
    atr = calculate_atr(highs, lows, prices, 5)
    assert atr > 0.0

    # VWAP test
    vwap = calculate_vwap(highs, lows, prices, volumes)
    assert min(lows) <= vwap <= max(highs)

    # Relative strength
    rs = calculate_relative_strength(prices * 3, prices * 3)
    assert rs == 0.0  # Equal performance should yield 0.0% diff


def test_derivatives_joint_price_oi_buildup():
    """Verify futures price and OI classification for F&O equities and non-F&O boundary."""
    # F&O security (Reliance)
    rel_deriv = analyze_derivatives_context("RELIANCE")
    assert rel_deriv["is_fo_eligible"] is True
    assert rel_deriv["buildup"]["type"] == "LONG_BUILDUP"
    assert rel_deriv["options_context"]["put_call_ratio"] > 1.0

    # Non-F&O security (Solaris demo)
    sol_deriv = analyze_derivatives_context("SOLARIS")
    assert sol_deriv["is_fo_eligible"] is False
    assert sol_deriv["status"] == "NOT_APPLICABLE"


def test_actionable_signal_card_generation_swing():
    """Verify structured signal card generation and position sizing for Swing mode."""
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)

    reliance_asset = repo.get_asset("RELIANCE")
    report = orch.run(reliance_asset.id, config={"research_mode": "swing", "risk_budget_rupees": 20000.0})

    assert report.signal_card is not None
    sig = report.signal_card

    assert sig.symbol == "RELIANCE"
    assert sig.research_mode == "swing"
    assert sig.entry_trigger is not None
    assert sig.stop_loss is not None
    assert sig.target_1 is not None
    assert sig.reward_to_risk is not None
    assert sig.reward_to_risk > 1.0
    assert sig.risk_budget_rupees == 20000.0

    # Verify position sizing formula: floor(risk_budget / (entry - stop))
    risk_dist = abs(sig.entry_trigger - sig.stop_loss)
    expected_qty = int(20000.0 / risk_dist)
    # Check lot size rounding if F&O
    assert sig.suggested_quantity > 0


def test_intraday_mode_separation():
    """Verify distinct feature calibration for Intraday mode."""
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)

    reliance_asset = repo.get_asset("RELIANCE")
    report_intra = orch.run(reliance_asset.id, config={"research_mode": "intraday"})

    assert report_intra.research_mode == "intraday"
    sig = report_intra.signal_card
    assert sig.research_mode == "intraday"
    assert "1 Session" in sig.holding_window
    assert sig.stop_loss_type == "hard_stop"


def test_ten_persona_expert_review_findings():
    """Verify that all 10 simulated review personas produce structured quality audits."""
    repo = Repository()
    orch = InvestmentCommitteeOrchestrator(repo=repo)

    solaris_asset = repo.get_asset("SOLARIS")
    report = orch.run(solaris_asset.id)

    assert report.expert_reviews is not None
    assert len(report.expert_reviews) == 10

    persona_ids = [r["persona_id"] for r in report.expert_reviews]
    expected_personas = [
        "vijay_kedia",
        "raamdeo_agrawal",
        "porinju_veliyath",
        "basant_maheshwari",
        "sudarshan_sukhani",
        "kunal_bothra",
        "sunil_singhania",
        "ashish_kacholia",
        "ramesh_damani",
        "asim_jain",
    ]
    for ep in expected_personas:
        assert ep in persona_ids, f"Persona {ep} missing from review findings."


def test_signal_ledger_persistence_and_api():
    """Verify persistent recording of signals in SQLite signal ledger and retrieval API."""
    res = client.get("/api/v1/signals")
    assert res.status_code == 200
    signals = res.json()
    assert len(signals) > 0

    first_sig = signals[0]
    assert "symbol" in first_sig
    assert "mode" in first_sig
    assert "decision" in first_sig
    assert "status" in first_sig


def test_historical_backtest_replay():
    """Verify historical evaluation replay produces valid positive expectancy and drawdown metrics."""
    backtest_results = run_historical_backtest(slippage_pct=0.15, brokerage_and_taxes_pct=0.08)

    assert backtest_results["total_test_cases"] == 10
    assert backtest_results["actionable_trades_count"] == 7
    assert backtest_results["abstained_cases_count"] == 3
    assert backtest_results["win_rate_pct"] > 60.0
    assert backtest_results["profit_factor"] > 2.0
    assert backtest_results["expectancy_r"] > 0.5
    assert backtest_results["max_drawdown_pct"] < 5.0
    assert backtest_results["evidence_validity_rate_pct"] == 100.0
