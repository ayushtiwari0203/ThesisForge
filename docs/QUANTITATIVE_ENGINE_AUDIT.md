# THESISFORGE AI — QUANTITATIVE TRADING ENGINE AUDIT

## 1. Executive Summary

The **ThesisForge AI Quantitative Engine** executes transparent, mathematically verified technical and position-sizing analysis. Under the project specifications, the system strictly separates historical price bars from textual filings, eliminates mock data, enforces multi-factor position sizing, and accounts for Indian market transaction friction.

---

## 2. Structured OHLCV Data Architecture

- **Data Sourcing**: 3–5 years of daily bars with corporate-action adjustments (splits, dividends) stored in `historical_market_data` table.
- **Strict Data Dependency Rule**: Price history cannot be substituted with annual-report PDFs. When bars are $< 14$, technical analysis gracefully returns `status = "insufficient_data"` with transparent notices.
- **Daily vs Intraday Boundary**:
  - Daily bars provide multi-day swing and positional analysis.
  - Intraday VWAP requires minute/tick data. The system explicitly labels its daily volume-weighted metric as `rolling_anchored_vwap_20d` and reports `intraday_vwap: None` with notice:
    > *"UNAVAILABLE — Requires 1-min/5-min intraday market depth feed. Daily bars cannot represent intraday VWAP."*

---

## 3. Mathematical Formula Specifications

### 3.1 Wilder's Smoothed ADX (Average Directional Index)
$$TR_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$$
$$+DM_t = \begin{cases} H_t - H_{t-1} & \text{if } (H_t - H_{t-1}) > (L_{t-1} - L_t) \text{ and } (H_t - H_{t-1}) > 0 \\ 0 & \text{otherwise} \end{cases}$$
$$-DM_t = \begin{cases} L_{t-1} - L_t & \text{if } (L_{t-1} - L_t) > (H_t - H_{t-1}) \text{ and } (L_{t-1} - L_t) > 0 \\ 0 & \text{otherwise} \end{cases}$$
$$\text{Smoothed } X_t = \text{Smoothed } X_{t-1} - \frac{\text{Smoothed } X_{t-1}}{14} + X_t$$
$$+DI = 100 \times \frac{\text{Smoothed } +DM}{\text{Smoothed } TR}, \quad -DI = 100 \times \frac{\text{Smoothed } -DM}{\text{Smoothed } TR}$$
$$DX = 100 \times \frac{|+DI - -DI|}{+DI + -DI}$$
$$ADX = \text{Wilder's Smooth of } DX \text{ over 14 periods}$$

### 3.2 Iterative Supertrend (10, 3.0)
$$\text{Basic Upper} = \frac{H_t + L_t}{2} + 3.0 \times ATR_{10}$$
$$\text{Basic Lower} = \frac{H_t + L_t}{2} - 3.0 \times ATR_{10}$$
$$\text{Final Upper}_t = \begin{cases} \text{Basic Upper}_t & \text{if Basic Upper}_t < \text{Final Upper}_{t-1} \text{ or } C_{t-1} > \text{Final Upper}_{t-1} \\ \text{Final Upper}_{t-1} & \text{otherwise} \end{cases}$$
$$\text{Final Lower}_t = \begin{cases} \text{Basic Lower}_t & \text{if Basic Lower}_t > \text{Final Lower}_{t-1} \text{ or } C_{t-1} < \text{Final Lower}_{t-1} \\ \text{Final Lower}_{t-1} & \text{otherwise} \end{cases}$$
$$\text{Supertrend Direction} = \begin{cases} \text{BULLISH (Lower Band)} & \text{if } C_t > \text{Final Upper}_{t-1} \\ \text{BEARISH (Upper Band)} & \text{if } C_t < \text{Final Lower}_{t-1} \end{cases}$$

### 3.3 On-Balance Volume (OBV)
$$OBV_t = \begin{cases} OBV_{t-1} + V_t & \text{if } C_t > C_{t-1} \\ OBV_{t-1} - V_t & \text{if } C_t < C_{t-1} \\ OBV_{t-1} & \text{if } C_t = C_{t-1} \end{cases}$$
Trend is classified as `ACCUMULATION` when $OBV_t > \text{SMA}(OBV, 20)$, and `DISTRIBUTION` when below.

### 3.4 Donchian Channels (20-Day)
$$\text{Upper} = \max(H_{t-19 \dots t}), \quad \text{Lower} = \min(L_{t-19 \dots t}), \quad \text{Middle} = \frac{\text{Upper} + \text{Lower}}{2}$$
$$\text{Bandwidth \%} = \frac{\text{Upper} - \text{Lower}}{\text{Middle}} \times 100$$

### 3.5 Classic Pivot Points
$$P = \frac{H + L + C}{3}$$
$$R_1 = 2P - L, \quad S_1 = 2P - H$$
$$R_2 = P + (H - L), \quad S_2 = P - (H - L)$$
$$R_3 = H + 2(P - L), \quad S_3 = L - 2(H - P)$$

### 3.6 Annualized Historical Volatility
$$\sigma_{\text{ann}} = \text{std}(\ln(C_t / C_{t-1})) \times \sqrt{252} \times 100\%$$

---

## 4. Multi-Constraint Position Sizing

Position size is deterministically calculated as:
$$\text{Quantity} = \max\left(0, \min(Q_{\text{risk}}, Q_{\text{capital}}, Q_{\text{liquidity}})\right)$$

Where:
1. **Risk-Limited Quantity**:
   $$Q_{\text{risk}} = \left\lfloor \frac{\text{Risk Budget (₹)}}{\text{Entry Price} - \text{Stop Loss}} \right\rfloor$$
2. **Capital-Limited Quantity**:
   $$Q_{\text{capital}} = \left\lfloor \frac{\text{Allocated Portfolio Capital}}{\text{Entry Price}} \right\rfloor$$
3. **Liquidity Participation Cap**:
   $$Q_{\text{liquidity}} = \max\left(1, \left\lfloor \text{Average Daily Volume}_{20\text{d}} \times 0.01 \right\rfloor\right)$$
   *(Restricts order size to $\le 1\%$ of daily turnover to avoid market impact and slippage)*

---

## 5. Indian Market Transaction Cost & Net R:R Model

All trade setups compute both **Gross Reward-to-Risk** and **Net Reward-to-Risk** by deducting Indian statutory and operational friction:

| Component | Delivery Rate | Intraday Rate | Applicable Leg |
|---|---|---|---|
| **Securities Transaction Tax (STT)** | 0.100% | 0.025% | Buy + Sell (Delivery) / Sell only (Intraday) |
| **Brokerage** | $\min(₹20, 0.05\%)$ | $\min(₹20, 0.05\%)$ | Both Legs |
| **Exchange Transaction Charges** | 0.00345% | 0.00345% | Both Legs |
| **SEBI Turnover Fee** | 0.00010% | 0.00010% | Both Legs |
| **Stamp Duty** | 0.01500% | 0.00300% | Buy Leg Only |
| **GST** | 18% | 18% | On (Brokerage + Exchange + SEBI) |
| **Slippage Assumption** | 0.150% | 0.150% | Both Legs |

### Net Reward-to-Risk Calculation
$$\text{Gross R:R} = \frac{|\text{Target}_1 - \text{Entry}|}{|\text{Entry} - \text{Stop Loss}|}$$
$$\text{Net R:R} = \frac{\max(0, \text{Gross Reward} - \text{Friction Per Share})}{\text{Gross Risk} + \text{Friction Per Share}}$$
