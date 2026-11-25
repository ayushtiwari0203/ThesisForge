# Phase 1 — Ten Expert Persona Audit Findings

**Project:** ThesisForge AI  
**Scope:** Evaluation of Prototype against 10 Simulated Analytical Research Lenses  
**Governance Note:** These findings represent simulated review lenses inspired by publicly documented methodologies. They are strictly quality-control evaluations and DO NOT represent personal endorsements or participation by the named market professionals.

---

## 1. Overview of the Ten Review Lenses

The current ThesisForge prototype was evaluated against frozen test runs (Solaris Power Tech `SOLARIS`, Zenith Infra `ZENITH`, Apex Tech `APEX`, and Reliance Industries `RELIANCE`). Each persona evaluated the prototype outputs for analytical gaps, ungrounded assumptions, and missing execution controls.

---

## 2. Detailed Findings by Review Lens

### Lens 1: Vijay Kedia — Growth, Business Quality & Scalable Opportunity
- **Observed Gap:** While the Research Agent extracts numerical revenue and profit metrics into evidence text, it does not structure them into a multi-period growth trajectory (3-year CAGR or sequential margin expansion).
- **Current Evidence:** Solaris and Reliance runs extract isolated quarterly and annual figures, but capital efficiency (ROCE/ROE) and cash conversion are not systematically audited.
- **Proposed Enhancement:** Add a Growth-Quality Checklist for swing candidates: sales/profit growth trend, ROCE/ROE trajectory, working capital cash-flow conversion, promoter pledging, and customer/supplier concentration.
- **Priority:** **P1** | **Effort:** Medium | **Value:** High | **Regression Risk:** Low.

### Lens 2: Raamdeo Agrawal — Quality, Valuation & Disciplined Fundamentals (QGLP)
- **Observed Gap:** The Judge Agent weighs evidence to decide BUY/HOLD/AVOID, but lacks a disciplined valuation sanity check to determine whether growth is already fully priced into market multiples.
- **Current Evidence:** No PE, PB, or EV/EBITDA ratios are systematically presented or contextualized against industry historical bands.
- **Proposed Enhancement:** Add a Valuation Context Panel: Trailing PE, PB, and EV/EBITDA ratios with sector-specific applicability, earnings growth consistency, and debt-to-cashflow sanity checks.
- **Priority:** **P1** | **Effort:** Medium | **Value:** High | **Regression Risk:** Low.

### Lens 3: Porinju Veliyath — Contrarian & Under-Followed Opportunity
- **Observed Gap:** The Bear Agent identifies company risks, but the system does not explicitly identify what the market's *consensus skepticism* is versus what turnaround catalyst exists.
- **Current Evidence:** In Zenith Infrastructure, the risk is severe debt, but the contrarian turnaround catalyst (asset monetization or debt restructuring) is not formally structured.
- **Proposed Enhancement:** Add a Contrarian Thesis Field to Bear/Bull debate: Market's current primary concern, verifiable evidence supporting an alternative turnaround thesis, upcoming operational catalyst, and governance downside trigger.
- **Priority:** **P1** | **Effort:** Low | **Value:** Medium | **Regression Risk:** Low.

### Lens 4: Basant Maheshwari — Earnings Acceleration & Growth-Momentum
- **Observed Gap:** Earnings growth is treated as a static fact rather than a dynamic rate of change. Sequential acceleration (QoQ growth accelerating over YoY growth) and relative price strength against Nifty 50 are missing.
- **Current Evidence:** Infosys and TCS filings show steady 5% YoY growth, but whether growth is accelerating or decelerating is not quantified.
- **Proposed Enhancement:** Add Earnings Acceleration & Relative Strength Trend features: Compare recent quarterly revenue/PAT growth with prior 4 quarters and compare stock returns against Nifty 50 benchmark.
- **Priority:** **P1** | **Effort:** Medium | **Value:** High | **Regression Risk:** Low.

### Lens 5: Sudarshan Sukhani — Pure Technical Structure & Risk-Defined Setup
- **Observed Gap:** The current output is an investment judgement (`BUY`, `HOLD`, `AVOID`) without actionable technical price structure: no multi-timeframe trend, no EMA/SMA alignment, no breakout trigger price, and no exact invalidation stop-loss.
- **Current Evidence:** A user receiving a BUY recommendation has no price level at which the thesis is invalidated.
- **Proposed Enhancement:** Create a deterministic Technical Setup Card: Multi-timeframe trend (Daily/Weekly), EMA 20/50/200, RSI, ATR, VWAP, breakout trigger level, entry zone, hard stop-loss, target 1 & 2, and setup expiry.
- **Priority:** **P0** | **Effort:** High | **Value:** High | **Regression Risk:** Low.

### Lens 6: Kunal Bothra — Actionable Trading Plan & Execution Discipline
- **Observed Gap:** The analytical thesis cannot be executed by a trader without a standardized trade card specifying risk per share, position sizing, and holding horizon.
- **Current Evidence:** The report provides deciding reasons, but no formula for calculating position quantity based on allowed capital risk.
- **Proposed Enhancement:** Standardize the Mandatory Signal Card: Research mode (Intraday/Swing), Setup type, Entry Trigger vs Entry Zone, Initial Stop-Loss, Targets (T1/T2), Trailing Stop rule, Risk-Reward ratio, and Position Size formula `floor(Risk / (Entry - Stop))`.
- **Priority:** **P0** | **Effort:** High | **Value:** High | **Regression Risk:** Low.

### Lens 7: Sunil Singhania — Portfolio Construction, Sector Allocation & Diversification
- **Observed Gap:** Individual stock reports evaluate securities in isolation, creating a risk that users construct concentrated portfolios in correlated sectors without warning.
- **Current Evidence:** Assets are tagged with `sector`, but multi-asset watchlists do not display industry concentration or turnover liquidity metrics.
- **Proposed Enhancement:** Add Sector/Industry Exposure and Correlation Context: Track watchlist sector weightings, flag clustered ideas in correlated industries, and report average daily turnover.
- **Priority:** **P2** | **Effort:** Low | **Value:** Medium | **Regression Risk:** Low.

### Lens 8: Ashish Kacholia — Emerging Small/Mid-Cap Business Discovery
- **Observed Gap:** Small and mid-cap companies carry unique liquidity impact costs, promoter pledging risks, and cash flow conversion friction that are not systematically checked.
- **Current Evidence:** Small-cap assets like Zenith or Apex have debt checks, but promoter pledging percentages and cash-flow-to-EBITDA ratios are not highlighted.
- **Proposed Enhancement:** Add Small/Mid-Cap Diligence Checklist: Market cap category, bid-ask spread/impact cost estimate, promoter pledging %, related-party transaction flags, and CFO-to-EBITDA ratio.
- **Priority:** **P2** | **Effort:** Medium | **Value:** Medium | **Regression Risk:** Low.

### Lens 9: Ramesh Damani — Market Cycles, Patience & Long-Horizon Context
- **Observed Gap:** The time horizon of the research is unspecified. A recommendation could be valid for 6 months but invalid for 2 weeks, leading to mismatched expectations.
- **Current Evidence:** The report has an `as_of` date but no explicit holding horizon or scheduled thesis review date.
- **Proposed Enhancement:** Add Market-Cycle and Catalyst Context: Classify sector cycle phase (Early / Mid / Late / Recessionary), state expected catalyst timeline, and provide explicit thesis review date.
- **Priority:** **P2** | **Effort:** Low | **Value:** Medium | **Regression Risk:** Low.

### Lens 10: Asim Jain — Data-Driven Equity + Derivatives Defined-Risk Trade Plan
- **Observed Gap:** For NSE securities in the F&O segment (e.g. Reliance, TCS, Infosys, Tata Motors), derivatives market positioning (Futures Open Interest changes, Put-Call Ratio, and Option-chain walls) is completely absent.
- **Current Evidence:** The prototype only inspects text filings and lacks derivatives price/OI buildup classification (Long Buildup, Short Buildup, Short Covering, Long Unwinding).
- **Proposed Enhancement:** Add Derivatives & Futures OI Analysis Engine: Capture futures OI change vs price change, Put-Call Ratio (PCR), and Max Pain/Call Wall resistance.
- **Priority:** **P1** | **Effort:** High | **Value:** High | **Regression Risk:** Low.

---

## 3. Summary of Consolidated Audit Gaps
1. **Core Execution Contract Missing:** Lack of actionable entry trigger, stop-loss, targets, and position sizing (Identified by Sukhani & Bothra).
2. **Horizon Conditioning Missing:** No separation between Intraday, Swing, and Positional research profiles (Identified by Damani, Sukhani, Bothra).
3. **Derivatives Positioning Missing:** No Futures OI buildup or options context for F&O securities (Identified by Jain).
4. **Technical Indicator Engine Missing:** No deterministic calculations for EMA, RSI, ATR, VWAP, or volume confirmation (Identified by Sukhani, Maheshwari).
5. **Fundamental Quality Depth:** Valuation context and sequential earnings acceleration are uncomputed (Identified by Agrawal, Kedia, Maheshwari).
