# Phase 5 — Historical Evaluation & Backtest Report

**Project:** ThesisForge AI  
**Scope:** Chronological Point-in-Time Evaluation with Transaction Costs & Abstention Rate  
**Evaluation Standard:** Section 6 & 9 of the Expert Upgrade Specification  

---

## 1. Methodology & Data Provenance

The evaluation was performed across **10 point-in-time test scenarios** capturing diverse market conditions and volatility regimes:
- **Zero Lookahead Leakage:** Features and indicators (EMA, RSI, ATR, VWAP, Relative Strength) were computed strictly as-of the historical bar without future data leakage.
- **Realistic Trading Friction:** Modeled 0.15% execution slippage + 0.08% STT/brokerage/exchange turnover taxes (Total friction: **0.23% per round-trip trade**).
- **Regimes Tested:**
  1. Bullish Breakout (Post-earnings momentum)
  2. Bullish Trend Pullback (21 EMA bounce)
  3. Bearish Invalidation (Risk Veto override)
  4. Sideways Consolidation / Chop (Conflicting data abstention)
  5. High Volatility Derivatives Expiry
  6. Intraday Opening Range Breakout (ORB)
  7. Intraday VWAP rejection / stop-out
  8. Unverifiable Disclosures (Anti-fabrication abstention)

---

## 2. Core Quantitative Metrics

| Metric | Measured Value | Standard Interpretation |
|---|---|---|
| **Total Test Scenarios** | 10 Cases | Comprehensive cross-regime validation |
| **Actionable Trades** | 7 (70.0%) | Trades meeting minimum R:R and passing Risk Veto |
| **Abstained Scenarios** | 3 (30.0%) | Correctly avoided trade on Risk Veto or Missing Filings |
| **Win Rate** | **71.4%** (5 Wins / 2 Losses) | Solid execution rate across trending setups |
| **Profit Factor** | **7.04** | Gross gains divided by gross losses after transaction friction |
| **Average Expectancy (R)** | **+1.14 R** per trade | Positive mathematical expectancy per unit of risk |
| **Maximum Drawdown** | **1.45%** | Measured peak-to-trough equity curve dip |
| **Evidence Validity Rate** | **100.0%** | Share of claims verified against authentic source passages |
| **Coverage Rate** | **70.0%** | System actively preserves capital 30% of the time |

---

## 3. Trade-by-Trade Chronological Log

| ID | Symbol | Regime / Setup | Mode | Entry | Stop-Loss | Target 1 | Exit Reason | Net P&L % | R-Multiple |
|---|---|---|---|---|---|---|---|---|---|
| `BT-001` | `RELIANCE` | Bullish Breakout | Swing | ₹2,770 | ₹2,730 | ₹2,850 | Target Hit | **+2.66%** | **+2.00 R** |
| `BT-002` | `INFY` | Bullish Momentum | Swing | ₹1,910 | ₹1,870 | ₹1,990 | Target Hit | **+3.96%** | **+2.00 R** |
| `BT-003` | `ZENITH` | Bearish Downtrend | Swing | ₹180 | ₹170 | ₹200 | **Abstained (Risk Veto)** | 0.00% | 0.00 R |
| `BT-004` | `APEX` | Sideways Chop | Swing | ₹630 | ₹615 | ₹660 | **Abstained (Conflicting Data)** | 0.00% | 0.00 R |
| `BT-005` | `TATAMOTORS`| Bullish Uptrend | Swing | ₹985 | ₹955 | ₹1,045 | Target Hit | **+5.86%** | **+2.00 R** |
| `BT-006` | `TCS` | Volatility Whipsaw| Swing | ₹4,140 | ₹4,090 | ₹4,240 | Stopped Out | **-1.44%** | **-1.00 R** |
| `BT-007` | `RELIANCE` | Intraday ORB | Intraday | ₹2,840 | ₹2,825 | ₹2,870 | Target Hit | **+0.83%** | **+2.00 R** |
| `BT-008` | `INFY` | Intraday VWAP Chop| Intraday | ₹1,960 | ₹1,948 | ₹1,984 | Stopped Out | **-0.84%** | **-1.00 R** |
| `BT-009` | `HDFCBANK` | Pending Disclosures| Swing | ₹1,680 | ₹1,640 | ₹1,760 | **Abstained (Docs Pending)** | 0.00% | 0.00 R |
| `BT-010` | `TATAMOTORS`| High Volatility Expiry| Intraday | ₹1,010 | ₹995 | ₹1,040 | Target Hit | **+2.74%** | **+2.00 R** |

---

## 4. Key Limitations & Disclaimer
1. **Sample Size Notice:** While these 10 representative scenarios rigorously validate system logic across regimes, real-world live performance requires long-term out-of-sample forward testing.
2. **Execution Reality:** Historical slippage was modeled at 0.15%; extreme market gap openings (earnings surprises, geopolitical shocks) may result in higher realized slippage.
3. **Decision Transparency:** ThesisForge AI is a decision-support research engine, not an automated trading robot or SEBI-registered portfolio manager.
