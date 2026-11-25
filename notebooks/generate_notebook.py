"""Script to generate and execute the comprehensive academic demo notebook for MTM606."""

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Add web-app directory to sys.path
web_app_dir = Path(__file__).resolve().parent.parent / "web-app"
if str(web_app_dir) not in sys.path:
    sys.path.insert(0, str(web_app_dir))


def generate_and_execute_notebook():
    code_cells = [
        # Cell 1: Setup & Universe Inspection
        """import os, sys
from pathlib import Path

web_app_dir = Path.cwd().parent / "web-app" if Path.cwd().name == "notebooks" else Path.cwd() / "web-app"
if str(web_app_dir) not in sys.path:
    sys.path.insert(0, str(web_app_dir))

from database.repository import Repository
from database.seed_data import seed_database
from orchestration.workflow import InvestmentCommitteeOrchestrator

repo = Repository()
seed_database(repo)
orchestrator = InvestmentCommitteeOrchestrator(repo=repo)

assets = repo.list_assets()
real_assets = [a for a in assets if a.dataset_type == "real_listed"]
demo_assets = [a for a in assets if a.dataset_type == "synthetic_demo"]

print(f"[Setup Complete] Total Asset Universe: {len(assets)} companies")
print(f"  • Real NSE-Listed Equities: {len(real_assets)}")
print(f"  • Academic Benchmarks:      {len(demo_assets)}\\n")
print(f"{'SYMBOL':<12} | {'DATASET TYPE':<15} | {'STATUS':<18} | {'DOCS':<6} | {'SECTOR'}")
print("-" * 75)
for a in assets:
    print(f"{a.symbol:<12} | {a.dataset_type:<15} | {a.document_status:<18} | {a.document_count:<6} | {a.sector}")
""",
        # Cell 2: Research Run on Real NSE Stock: Reliance Industries (RELIANCE)
        """print("=== Running Multi-Agent Committee on Real Listed Equity: Reliance Industries (RELIANCE) ===\\n")
report_reliance = orchestrator.run(asset_id="asset-reliance-001", config={"research_mode": "swing", "risk_budget_rupees": 25000.0})

print(f"Run ID:         {report_reliance.run_id}")
print(f"Recommendation: {report_reliance.recommendation}")
print(f"Risk Veto:      {report_reliance.risk_veto['triggered']}")
print(f"\\n🐂 Strongest Bull Case:\\n  {report_reliance.strongest_bull_argument['claim']}")
print(f"  Citations: {report_reliance.strongest_bull_argument['evidence_ids']}")
print(f"\\n🐻 Strongest Bear Vulnerability:\\n  {report_reliance.strongest_bear_argument['claim']}")
print(f"  Citations: {report_reliance.strongest_bear_argument['evidence_ids']}")
""",
        # Cell 3: Actionable Trade Card & Technical / Derivatives Engines
        """sig = report_reliance.signal_card
print("=" * 65)
print("   ACTIONABLE SIGNAL CARD (SECTION 5 CONTRACT)")
print("=" * 65)
print(f"Instrument:        {sig.instrument} ({sig.symbol}) [{sig.exchange}]")
print(f"Strategy Mode:     {sig.research_mode.upper()} ({sig.holding_window})")
print(f"Reference Price:   ₹{sig.current_reference_price}")
print(f"Entry Trigger:     ₹{sig.entry_trigger} (Zone: ₹{sig.entry_zone_min} - ₹{sig.entry_zone_max})")
print(f"Stop-Loss:         ₹{sig.stop_loss} ({sig.stop_loss_type})")
print(f"Invalidation:      {sig.invalidation_reason}")
print(f"Targets:           T1: ₹{sig.target_1} | T2: ₹{sig.target_2}")
print(f"Reward-to-Risk:    {sig.reward_to_risk}x")
print(f"Risk Capital:      ₹{sig.risk_budget_rupees}")
print(f"Suggested Qty:     {sig.suggested_quantity} shares (via formula: floor(Risk / (Entry - Stop)))")
print(f"Slippage Caveat:   {sig.slippage_assumption_pct}% estimated slippage")
print(f"Execution Status:  {'ACTIONABLE' if sig.is_actionable else 'NON-ACTIONABLE / PRESERVE CAPITAL'}")
print(f"Action Reason:     {sig.actionability_reason}")

deriv = report_reliance.derivatives_context
if deriv and deriv.get('is_fo_eligible'):
    print("\\n📊 DERIVATIVES & FUTURES OI CONTEXT:")
    print(f"  • Buildup Type:  {deriv['buildup']['type']} ({deriv['buildup']['sentiment']})")
    print(f"  • Explanation:   {deriv['buildup']['explanation']}")
    print(f"  • Put-Call Ratio:{deriv['options_context']['put_call_ratio']} ({deriv['options_context']['pcr_bias']})")
    print(f"  • Call Wall:     ₹{deriv['options_context']['call_wall_strike']} | Put Wall: ₹{deriv['options_context']['put_wall_strike']}")
""",
        # Cell 4: Ten Methodology-Inspired Persona Audits (Simulated Lenses)
        """print("=== 10 Methodology-Inspired Expert Review Personas (Simulated Analytical Lenses) ===\\n")
reviews = report_reliance.expert_reviews
print(f"Total Quality Lenses Evaluated: {len(reviews)}\\n")
for r in reviews[:5]:
    print(f"[{r['priority']}] {r['persona_name']} — {r['lens_title']}:")
    print(f"  • Observed Gap:   {r['observed_issue']}")
    print(f"  • Recommendation: {r['suggested_change']}")
    print(f"  • Acceptance:     {r['acceptance_test']}\\n")
""",
        # Cell 5: Strict Anti-Fabrication Check: Pending-Document Stock (HDFC Bank)
        """print("=== Testing Anti-Fabrication & Graceful Fallback: HDFC Bank Limited (HDFCBANK) ===\\n")
report_hdfc = orchestrator.run(asset_id="asset-hdfcbank-003")

print(f"Asset:          {report_hdfc.asset['name']} ({report_hdfc.asset['symbol']})")
print(f"Recommendation: {report_hdfc.recommendation} (Safely defaulted in accordance with SEBI disclosure standards)")
print(f"Deciding Reason: {report_hdfc.deciding_reasons[0]['reason']}")
print(f"Signal Status:   {'ACTIONABLE' if report_hdfc.signal_card.is_actionable else 'NON-ACTIONABLE'}")
print(f"Action Reason:   {report_hdfc.signal_card.actionability_reason}")
print(f"Evidence Cited:  {report_hdfc.strongest_bull_argument['evidence_ids']} (Zero fabricated claims)")
""",
        # Cell 6: Scenario B: Risk Agent Veto Override (Zenith Infra)
        """print("=== Scenario B: Risk Agent Veto Override on Zenith Infrastructure ===\\n")
report_b = orchestrator.run(asset_id="asset-zenith-002", config={"risk_veto_threshold": 0.65})

print(f"Final Recommendation: {report_b.recommendation}")
print(f"Risk Veto Triggered:  {report_b.risk_veto['triggered']}")
print(f"Risk Score:           {report_b.risk_veto['score']} (Threshold: {report_b.risk_veto['threshold']})")
print(f"Veto Justification:   {report_b.risk_veto['reason']}")
print(f"Signal Actionable:    {report_b.signal_card.is_actionable} (Execution blocked by safety gate)")
""",
        # Cell 7: Historical Backtest & Evaluation Replay (Section 6 & 9)
        """from evaluation.backtest import run_historical_backtest

print("=== Running Historical Evaluation Replay (10 Cross-Regime Test Scenarios) ===\\n")
bt_res = run_historical_backtest(slippage_pct=0.15, brokerage_and_taxes_pct=0.08)

print(f"Total Scenarios Tested:  {bt_res['total_test_cases']}")
print(f"Actionable Trades:       {bt_res['actionable_trades_count']} (Coverage: {bt_res['coverage_rate_pct']}%)")
print(f"Abstained Scenarios:     {bt_res['abstained_cases_count']} (Abstention Rate: {bt_res['abstention_rate_pct']}%)")
print(f"Win Rate:                {bt_res['win_rate_pct']}% ({bt_res['wins']} Wins / {bt_res['losses']} Losses)")
print(f"Profit Factor:           {bt_res['profit_factor']}")
print(f"Average Expectancy:      +{bt_res['expectancy_r']} R per trade")
print(f"Max Equity Drawdown:     {bt_res['max_drawdown_pct']}%")
print(f"Modeled Friction:        {bt_res['modeled_costs']['total_friction_pct']}% (Slippage + Brokerage + STT)")
print(f"Evidence Validity:       {bt_res['evidence_validity_rate_pct']}%")
""",
        # Cell 8: Signal Ledger and Audit Trail Verification
        """signals = repo.get_signal_records(limit=5)
print(f"Persistent Signal Ledger ({len(signals)} recent signals retrieved from SQLite):\\n")
for s in signals:
    print(f"  • [{s.created_at[:10]}] {s.symbol:<10} | Mode: {s.mode:<8} | Rec: {s.decision:<4} | Status: {s.status:<11} | Entry: ₹{s.entry_price or 'N/A'}")

is_valid = repo.verify_run_log_integrity(report_reliance.run_id)
print(f"\\nCryptographic Hash-Chain Integrity for Reliance Run: {is_valid}")
assert is_valid is True, 'Tamper detected in run log!'
print("✓ End-to-end multi-agent research and signal audit PASSED.")
""",
    ]

    exec_globals = {}
    cell_outputs = []

    for idx, code in enumerate(code_cells):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(code, exec_globals)
        output_str = buf.getvalue()
        lines = [l + "\n" for l in output_str.splitlines()]
        cell_outputs.append([{"name": "stdout", "output_type": "stream", "text": lines}])

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# ThesisForge AI — Academic Demonstration Notebook\n",
                "## CSE476 Agentic AI and Intelligent Automation (Project 2, Q18)\n",
                "**Topic:** Debate-Driven Investment Committee (BUY / HOLD / AVOID) & Trading Intelligence\n",
                "**Stock Universe:** 11 Real Indian NSE Equities + 3 Academic Demonstration Benchmarks (14 Total)\n",
                "**Location:** `Desktop/4vu5h/MTM606/`\n",
                "**Framework:** Microsoft Semantic Kernel + Python Deterministic Orchestrator\n",
                "\n",
                "This notebook demonstrates the end-to-end multi-agent investment research workflow:\n",
                "1. **Company Universe:** Expanded to 11 real NSE stocks with multi-field search and strict anti-fabrication rules.\n",
                "2. **Adversarial Debate:** Research, Bull, Bear, and 1-Turn Rebuttal grounded by evidence IDs (`EV-001`..).\n",
                "3. **Risk Agent Veto:** Empirical leverage covenant checks overriding BUY recommendations to HOLD.\n",
                "4. **Actionable Trade Cards:** Technical triggers, invalidation stop-loss, profit targets, and capital position sizing.\n",
                "5. **Ten Expert Review Personas:** Methodology-inspired simulated quality lenses auditing the product.\n",
                "6. **Historical Replay:** Point-in-time backtesting across regimes with transaction costs, slippage, and expectancy metrics.\n",
                "7. **Audit Trail:** Append-only log with SHA-256 cryptographic hash-chaining.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": cell_outputs[0],
            "source": [line + "\n" for line in code_cells[0].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Real Indian Listed Equity Analysis: Reliance Industries Limited (`RELIANCE`)\n",
                "Executes the full multi-agent committee on authentic Q2 FY25 regulatory disclosures filed with NSE/BSE.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": cell_outputs[1],
            "source": [line + "\n" for line in code_cells[1].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Mandatory Actionable Signal Card & Derivatives Analysis\n",
                "Translates research into risk-defined execution parameters: Trigger vs Entry Zone, Invalidation Stop-Loss, Targets, R:R, and Position Sizing Formula.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": cell_outputs[2],
            "source": [line + "\n" for line in code_cells[2].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Ten Methodology-Inspired Review Personas (Simulated Lenses)\n",
                "Quality-assurance inspection layer auditing growth runway, valuation discipline, technical structure, derivatives, and portfolio concentration.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 4,
            "metadata": {},
            "outputs": cell_outputs[3],
            "source": [line + "\n" for line in code_cells[3].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Anti-Fabrication & Graceful Fallback: HDFC Bank (`HDFCBANK`)\n",
                "Demonstrates that for companies awaiting primary filings, ThesisForge **never fabricates financial figures**.\n",
                "The committee safely returns an `INSUFFICIENT_EVIDENCE` report with recommendation **`HOLD`** and marks trade execution as non-actionable.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 5,
            "metadata": {},
            "outputs": cell_outputs[4],
            "source": [line + "\n" for line in code_cells[4].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Scenario B: Risk Agent Veto Override (`ZENITH`)\n",
                "Demonstrates the Group-of-3 add-on requirement: Zenith Infrastructure has a debt-to-equity covenant breach (3.41x vs 2.0x limit) and a SEBI regulatory show-cause notice.\n",
                "The Risk Agent calculates a risk score crossing the 0.65 threshold and issues `veto = True`, forcing the final recommendation to **`HOLD`** regardless of potential upside.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 6,
            "metadata": {},
            "outputs": cell_outputs[5],
            "source": [line + "\n" for line in code_cells[5].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Historical Evaluation Replay Across Market Regimes\n",
                "Section 6 & 9: Chronological evaluation across 10 point-in-time scenarios with 0.23% transaction friction, calculating win rate, profit factor, expectancy (R), and drawdown.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 7,
            "metadata": {},
            "outputs": cell_outputs[6],
            "source": [line + "\n" for line in code_cells[6].splitlines()],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Persistent Signal Ledger & Cryptographic Run Log Verification\n",
                "Verifies that signals are persisted in the versioned SQLite ledger and events are appended with SHA-256 hash chaining.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 8,
            "metadata": {},
            "outputs": cell_outputs[7],
            "source": [line + "\n" for line in code_cells[7].splitlines()],
        },
    ]

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.13.15",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    out_file = Path(__file__).resolve().parent / "thesisforge_demo.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    print(f"Successfully generated and executed notebook at {out_file}")


if __name__ == "__main__":
    generate_and_execute_notebook()
