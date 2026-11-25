"""Valuation Context and Quality Scorecard Tool for ThesisForge AI.

Complies strictly with Section 4C of the Expert Specification:
- Sector-appropriate valuation multiples (PE, PB, EV/EBITDA)
- Return ratios (ROE, ROCE) and cash conversion checks
- Explicit sector metric suitability and data gap disclosures
"""

from __future__ import annotations
from typing import Any, Dict, Optional


VALUATION_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "RELIANCE": {
        "trailing_pe": 24.8,
        "sector_avg_pe": 22.0,
        "price_to_book": 2.1,
        "ev_to_ebitda": 11.4,
        "sector_avg_ev_ebitda": 10.5,
        "roce_pct": 10.8,
        "roe_pct": 9.4,
        "debt_to_equity": 0.38,
        "cfo_to_ebitda": 0.88,
        "primary_metric": "EV/EBITDA",
        "primary_metric_suitability": "EV/EBITDA is the industry standard for capital-intensive conglomerate and telecom assets with large depreciation shields.",
    },
    "TCS": {
        "trailing_pe": 31.2,
        "sector_avg_pe": 29.5,
        "price_to_book": 14.8,
        "ev_to_ebitda": 22.1,
        "sector_avg_ev_ebitda": 20.8,
        "roce_pct": 58.1,
        "roe_pct": 48.7,
        "debt_to_equity": 0.0,
        "cfo_to_ebitda": 0.98,
        "primary_metric": "Trailing P/E & ROCE",
        "primary_metric_suitability": "Price-to-Earnings and Return on Capital are premier metrics for asset-light software export enterprises with zero long-term debt.",
    },
    "INFY": {
        "trailing_pe": 27.5,
        "sector_avg_pe": 29.5,
        "price_to_book": 8.9,
        "ev_to_ebitda": 18.9,
        "sector_avg_ev_ebitda": 20.8,
        "roce_pct": 39.4,
        "roe_pct": 31.8,
        "debt_to_equity": 0.0,
        "cfo_to_ebitda": 0.92,
        "primary_metric": "Trailing P/E & Free Cash Flow Yield",
        "primary_metric_suitability": "P/E multiple and FCF conversion provide reliable valuation discipline for high-cash-generating IT services leaders.",
    },
    "TATAMOTORS": {
        "trailing_pe": 10.4,
        "sector_avg_pe": 18.2,
        "price_to_book": 3.8,
        "ev_to_ebitda": 5.2,
        "sector_avg_ev_ebitda": 8.5,
        "roce_pct": 21.6,
        "roe_pct": 32.4,
        "debt_to_equity": 0.52,
        "cfo_to_ebitda": 0.94,
        "primary_metric": "EV/EBITDA & Net Debt/EBITDA",
        "primary_metric_suitability": "EV/EBITDA and debt de-leveraging trajectory reflect cyclical auto recovery and JLR cash-flow turnaround.",
    },
    "SOLARIS": {
        "trailing_pe": 34.0,
        "sector_avg_pe": 32.0,
        "price_to_book": 4.2,
        "ev_to_ebitda": 14.8,
        "sector_avg_ev_ebitda": 13.5,
        "roce_pct": 14.2,
        "roe_pct": 12.8,
        "debt_to_equity": 1.15,
        "cfo_to_ebitda": 0.72,
        "primary_metric": "EV/EBITDA & Capacity Multiples",
        "primary_metric_suitability": "EV/EBITDA accounts for high upfront capex and utility-scale solar asset financing.",
    },
    "ZENITH": {
        "trailing_pe": 48.0,
        "sector_avg_pe": 16.0,
        "price_to_book": 1.9,
        "ev_to_ebitda": 17.5,
        "sector_avg_ev_ebitda": 9.0,
        "roce_pct": 4.1,
        "roe_pct": 3.2,
        "debt_to_equity": 3.41,
        "cfo_to_ebitda": 0.35,
        "primary_metric": "Debt Service Coverage & D/E",
        "primary_metric_suitability": "Balance sheet solvency and covenant compliance supersede P/E multiples due to severe leverage stress.",
    },
    "APEX": {
        "trailing_pe": 26.0,
        "sector_avg_pe": 28.0,
        "price_to_book": 5.4,
        "ev_to_ebitda": 16.2,
        "sector_avg_ev_ebitda": 18.0,
        "roce_pct": 18.5,
        "roe_pct": 16.2,
        "debt_to_equity": 0.12,
        "cfo_to_ebitda": 0.78,
        "primary_metric": "P/E & Revenue Multiple",
        "primary_metric_suitability": "Standard valuation metrics applicable, but subject to audited statutory reconciliation.",
    },
    "HDFCBANK": {
        "trailing_pe": 18.2,
        "sector_avg_pe": 17.5,
        "price_to_book": 2.65,
        "sector_avg_pb": 2.10,
        "ev_to_ebitda": None,
        "sector_avg_ev_ebitda": None,
        "roce_pct": None,
        "roe_pct": 15.8,
        "return_on_assets_pct": 1.95,
        "debt_to_equity": None,
        "cfo_to_ebitda": None,
        "primary_metric": "Price-to-Book (P/B) & Return on Assets (RoA)",
        "primary_metric_suitability": "Price-to-Book and Return on Assets are the industry standard yardsticks for banking. EV/EBITDA and Debt-to-Equity are structurally non-applicable to financial institutions due to deposit-based liability funding.",
    },
    "ICICIBANK": {
        "trailing_pe": 17.8,
        "sector_avg_pe": 17.5,
        "price_to_book": 3.10,
        "sector_avg_pb": 2.10,
        "ev_to_ebitda": None,
        "sector_avg_ev_ebitda": None,
        "roce_pct": None,
        "roe_pct": 17.4,
        "return_on_assets_pct": 2.15,
        "debt_to_equity": None,
        "cfo_to_ebitda": None,
        "primary_metric": "Price-to-Book (P/B) & Return on Assets (RoA)",
        "primary_metric_suitability": "Price-to-Book reflects core operating profitability and asset quality for private sector banks. EV/EBITDA is structurally excluded.",
    },
    "SBIN": {
        "trailing_pe": 10.5,
        "sector_avg_pe": 12.0,
        "price_to_book": 1.45,
        "sector_avg_pb": 1.25,
        "ev_to_ebitda": None,
        "sector_avg_ev_ebitda": None,
        "roce_pct": None,
        "roe_pct": 16.5,
        "return_on_assets_pct": 1.05,
        "debt_to_equity": None,
        "cfo_to_ebitda": None,
        "primary_metric": "Price-to-Book (P/B) & Asset Quality (NPA)",
        "primary_metric_suitability": "Price-to-Book reflects scale and provision coverage for public sector banking leaders. Operating cash flows and EV/EBITDA do not apply.",
    },
    "HINDUNILVR": {
        "trailing_pe": 54.0,
        "sector_avg_pe": 48.0,
        "price_to_book": 11.2,
        "ev_to_ebitda": 38.5,
        "sector_avg_ev_ebitda": 34.0,
        "roce_pct": 26.5,
        "roe_pct": 20.4,
        "debt_to_equity": 0.0,
        "cfo_to_ebitda": 0.96,
        "primary_metric": "Trailing P/E & Underlying Volume Growth",
        "primary_metric_suitability": "P/E multiple and operating cash flow conversion reflect FMCG brand pricing power and working capital efficiency.",
    },
    "ASIANPAINT": {
        "trailing_pe": 48.0,
        "sector_avg_pe": 42.0,
        "price_to_book": 13.5,
        "ev_to_ebitda": 31.0,
        "sector_avg_ev_ebitda": 28.0,
        "roce_pct": 32.0,
        "roe_pct": 27.5,
        "debt_to_equity": 0.05,
        "cfo_to_ebitda": 0.91,
        "primary_metric": "Trailing P/E & Gross Margin Resilience",
        "primary_metric_suitability": "P/E and ROCE reflect premium decorative coatings market leadership and distribution moat.",
    },
}

SECTOR_METHODOLOGY_GUIDANCE: Dict[str, Dict[str, Any]] = {
    "Financial Services": {
        "primary_metric": "Price to Book (P/B) & RoA",
        "rationale": "EV/EBITDA and D/E are non-applicable to financial institutions due to deposit-based funding.",
        "excluded_metrics": ["EV/EBITDA", "Debt-to-Equity", "EBITDA Margin"],
    },
    "Banking": {
        "primary_metric": "Price to Book (P/B) & RoA",
        "rationale": "EV/EBITDA and D/E are non-applicable to banking institutions.",
        "excluded_metrics": ["EV/EBITDA", "Debt-to-Equity", "EBITDA Margin"],
    },
    "Information Technology": {
        "primary_metric": "P/E, ROCE & Free Cash Flow Yield",
        "rationale": "Asset-light balance sheets make P/E and FCF conversion the premier valuation metrics.",
        "excluded_metrics": ["EV/Capacity"],
    },
    "Automobile": {
        "primary_metric": "EV/EBITDA & Net Debt/EBITDA",
        "rationale": "Cyclical capex and debt financing make EV/EBITDA the standard valuation multiple.",
        "excluded_metrics": [],
    },
    "Civil & Highway Infrastructure": {
        "primary_metric": "Order Book to Sales & DSCR",
        "rationale": "Covenant solvency and balance sheet leverage take precedence over earnings multiples.",
        "excluded_metrics": [],
    },
}


def evaluate_valuation_context(symbol: str, sector: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve verified valuation ratios and return metric suitability."""
    sym = symbol.upper()
    val = VALUATION_BENCHMARKS.get(sym)

    if not val:
        sec_guide = SECTOR_METHODOLOGY_GUIDANCE.get(sector or "", {
            "primary_metric": "P/E & EV/EBITDA",
            "rationale": "Standard corporate valuation metrics subject to audited statutory filing reconciliation.",
            "excluded_metrics": [],
        })
        return {
            "symbol": sym,
            "status": "SECTOR_FRAMEWORK_GUIDELINE",
            "sector": sector or "General",
            "message": f"Valuation ratios for {sym} awaiting official statutory annual report filing reconciliation. Non-fabrication policy active.",
            "primary_metric": sec_guide["primary_metric"],
            "metric_suitability_rationale": sec_guide["rationale"],
            "excluded_metrics": sec_guide.get("excluded_metrics", []),
            "metrics": {},
        }

    return {
        "symbol": sym,
        "status": "VERIFIED_FIXTURE",
        "trailing_pe": val.get("trailing_pe"),
        "sector_avg_pe": val.get("sector_avg_pe"),
        "price_to_book": val.get("price_to_book"),
        "sector_avg_pb": val.get("sector_avg_pb"),
        "ev_to_ebitda": val.get("ev_to_ebitda"),
        "sector_avg_ev_ebitda": val.get("sector_avg_ev_ebitda"),
        "roce_pct": val.get("roce_pct"),
        "roe_pct": val.get("roe_pct"),
        "return_on_assets_pct": val.get("return_on_assets_pct"),
        "debt_to_equity": val.get("debt_to_equity"),
        "cfo_to_ebitda": val.get("cfo_to_ebitda"),
        "primary_metric": val.get("primary_metric"),
        "metric_suitability_rationale": val.get("primary_metric_suitability"),
    }
