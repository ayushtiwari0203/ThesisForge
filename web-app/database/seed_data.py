"""Data seeding script to initialize company universe (11 real NSE stocks + 3 academic benchmarks)."""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Optional

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import Asset
from database.repository import Repository
from tools.document_tools import ingest_document_file


def seed_database(repo: Optional[Repository] = None) -> None:
    repo = repo or Repository()

    # Look in MTM606/assets/sample_documents first, then web-app/data/sample_documents
    mtm606_assets = Path(__file__).resolve().parent.parent.parent / "assets" / "sample_documents"
    fallback_assets = Path(__file__).resolve().parent.parent / "data" / "sample_documents"
    base_data_dir = mtm606_assets if mtm606_assets.exists() else fallback_assets

    # =========================================================================
    # PART 1: ACADEMIC DEMONSTRATION BENCHMARKS (3 Synthetic Companies)
    # Strictly marked as dataset_type="synthetic_demo" for Q18 scenario verification
    # =========================================================================

    # 1. Solaris Power Tech (Scenario A: Balanced normal debate)
    asset_solaris = Asset(
        id="asset-solaris-001",
        name="Solaris Power Tech Limited",
        symbol="SOLARIS",
        exchange="NSE",
        isin=None,  # Academic benchmark: strictly None to prevent misleading realistic ISIN representation
        asset_type="equity",
        sector="Renewable Energy & Infrastructure",
        description="India-based utility-scale solar and rooftop clean energy infrastructure developer (Academic benchmark asset).",
        dataset_type="synthetic_demo",
        document_status="indexed",
        market_cap_category="Mid Cap",
    )
    repo.add_asset(asset_solaris)

    solaris_ar = base_data_dir / "solaris_annual_report_fy25.txt"
    if solaris_ar.exists():
        ingest_document_file(
            asset_id=asset_solaris.id,
            file_path=str(solaris_ar),
            repo=repo,
            source="Annual Report FY2024-25",
            source_date="2025-05-15",
            doc_type="annual_report",
        )

    solaris_q2 = base_data_dir / "solaris_quarterly_update_q2.txt"
    if solaris_q2.exists():
        ingest_document_file(
            asset_id=asset_solaris.id,
            file_path=str(solaris_q2),
            repo=repo,
            source="Q2 FY2025-26 Financial Results",
            source_date="2025-10-20",
            doc_type="quarterly_report",
        )

    # 2. Zenith Infrastructure (Scenario B: Risk Veto trigger)
    asset_zenith = Asset(
        id="asset-zenith-002",
        name="Zenith Infrastructure Limited",
        symbol="ZENITH",
        exchange="NSE",
        isin=None,  # Academic benchmark: strictly None to prevent misleading realistic ISIN representation
        asset_type="equity",
        sector="Civil & Highway Infrastructure",
        description="Highways and EPC concessions provider under balance-sheet leverage stress (Academic benchmark asset).",
        dataset_type="synthetic_demo",
        document_status="indexed",
        market_cap_category="Small Cap",
    )
    repo.add_asset(asset_zenith)

    zenith_doc = base_data_dir / "zenith_infra_annual_report_fy25.txt"
    if zenith_doc.exists():
        ingest_document_file(
            asset_id=asset_zenith.id,
            file_path=str(zenith_doc),
            repo=repo,
            source="Annual Report FY2024-25",
            source_date="2025-06-10",
            doc_type="annual_report",
        )

    # 3. Apex Technologies (Scenario C: Conflicting evidence)
    asset_apex = Asset(
        id="asset-apex-003",
        name="Apex Technologies Limited",
        symbol="APEX",
        exchange="NSE",
        isin=None,  # Academic benchmark: strictly None to prevent misleading realistic ISIN representation
        asset_type="equity",
        sector="Information Technology",
        description="Cloud and AI software solutions provider with conflicting disclosures (Academic benchmark asset).",
        dataset_type="synthetic_demo",
        document_status="indexed",
        market_cap_category="Mid Cap",
    )
    repo.add_asset(asset_apex)

    apex_pr = base_data_dir / "apex_technologies_pr_q3.txt"
    if apex_pr.exists():
        ingest_document_file(
            asset_id=asset_apex.id,
            file_path=str(apex_pr),
            repo=repo,
            source="Q3 Management Press Release",
            source_date="2026-01-18",
            doc_type="press_release",
        )

    apex_aud = base_data_dir / "apex_technologies_audited_q3.txt"
    if apex_aud.exists():
        ingest_document_file(
            asset_id=asset_apex.id,
            file_path=str(apex_aud),
            repo=repo,
            source="Q3 Statutory Audited Filing",
            source_date="2026-02-12",
            doc_type="audited_filing",
        )

    # =========================================================================
    # PART 2: REAL LISTED INDIAN EQUITIES (11 Real NSE Companies)
    # Strictly marked as dataset_type="real_listed"
    # Never fabricated: companies with documents use authentic exchange filings;
    # companies without documents are honestly labeled "documents_pending" (0 docs).
    # =========================================================================

    real_companies = [
        # 1. Reliance Industries (Authentic filing available)
        {
            "id": "asset-reliance-001",
            "name": "Reliance Industries Limited",
            "symbol": "RELIANCE",
            "isin": "INE002A01018",
            "sector": "Energy & Conglomerate",
            "description": "India's largest private enterprise spanning oil-to-chemicals, telecom (Jio), retail, and new energy.",
            "filing_file": "reliance_q2_fy25_financial_results.txt",
            "filing_source": "NSE/BSE Regulatory Filing Q2 FY25",
            "filing_date": "2024-10-14",
            "doc_type": "quarterly_filing",
        },
        # 2. Tata Consultancy Services (Authentic filing available)
        {
            "id": "asset-tcs-002",
            "name": "Tata Consultancy Services Limited",
            "symbol": "TCS",
            "isin": "INE467B01029",
            "sector": "Information Technology",
            "description": "Global leader in IT services, consulting, business solutions, and cloud transformation.",
            "filing_file": "tcs_q2_fy25_financial_results.txt",
            "filing_source": "NSE/BSE Regulatory Filing Q2 FY25",
            "filing_date": "2024-10-10",
            "doc_type": "quarterly_filing",
        },
        # 3. HDFC Bank (Documents Pending)
        {
            "id": "asset-hdfcbank-003",
            "name": "HDFC Bank Limited",
            "symbol": "HDFCBANK",
            "isin": "INE040A01034",
            "sector": "Banking & Financial Services",
            "description": "India's largest private sector bank by assets following the landmark merger with HDFC Limited.",
            "filing_file": None,
        },
        # 4. Infosys (Authentic filing available)
        {
            "id": "asset-infosys-004",
            "name": "Infosys Limited",
            "symbol": "INFY",
            "isin": "INE009A01021",
            "sector": "Information Technology",
            "description": "Next-generation digital services and consulting leader in AI, cloud infrastructure, and enterprise agility.",
            "filing_file": "infosys_q2_fy25_financial_results.txt",
            "filing_source": "NSE/BSE Regulatory Filing Q2 FY25",
            "filing_date": "2024-10-17",
            "doc_type": "quarterly_filing",
        },
        # 5. ICICI Bank (Documents Pending)
        {
            "id": "asset-icicibank-005",
            "name": "ICICI Bank Limited",
            "symbol": "ICICIBANK",
            "isin": "INE090A01021",
            "sector": "Banking & Financial Services",
            "description": "Leading Indian multinational banking and financial services conglomerate offering retail and corporate banking.",
            "filing_file": None,
        },
        # 6. Larsen & Toubro (Documents Pending)
        {
            "id": "asset-lt-006",
            "name": "Larsen & Toubro Limited",
            "symbol": "LT",
            "isin": "INE018A01030",
            "sector": "Infrastructure & Engineering",
            "description": "Technology, engineering, construction, manufacturing, and financial services conglomerate.",
            "filing_file": None,
        },
        # 7. Bharti Airtel (Documents Pending)
        {
            "id": "asset-bhartiartl-007",
            "name": "Bharti Airtel Limited",
            "symbol": "BHARTIARTL",
            "isin": "INE397D01024",
            "sector": "Telecommunications",
            "description": "Global communications solutions provider operating across India, South Asia, and 14 African nations.",
            "filing_file": None,
        },
        # 8. ITC (Documents Pending)
        {
            "id": "asset-itc-008",
            "name": "ITC Limited",
            "symbol": "ITC",
            "isin": "INE154A01025",
            "sector": "Consumer Goods & Conglomerate",
            "description": "Diversified conglomerate with presence in FMCG, hotels, paperboards, packaging, and agri-business.",
            "filing_file": None,
        },
        # 9. State Bank of India (Documents Pending)
        {
            "id": "asset-sbin-009",
            "name": "State Bank of India",
            "symbol": "SBIN",
            "isin": "INE062A01020",
            "sector": "Banking & Financial Services",
            "description": "Fortune 500 public sector bank and financial services statutory body with widespread nationwide presence.",
            "filing_file": None,
        },
        # 10. Tata Motors (Authentic filing available)
        {
            "id": "asset-tatamotors-010",
            "name": "Tata Motors Limited",
            "symbol": "TATAMOTORS",
            "isin": "INE155A01022",
            "sector": "Automobile",
            "description": "Leading global automobile manufacturer. Demerger Note: Approved corporate demerger separating Commercial Vehicles (TMCV) and Passenger Vehicles (TMPV / JLR / EV). Market data maps to TMPV.NS.",
            "filing_file": "tatamotors_q2_fy25_financial_results.txt",
            "filing_source": "NSE/BSE Regulatory Filing Q2 FY25",
            "filing_date": "2024-11-08",
            "doc_type": "quarterly_filing",
        },
        # 11. Hindustan Unilever (Documents Pending)
        {
            "id": "asset-hindunilvr-011",
            "name": "Hindustan Unilever Limited",
            "symbol": "HINDUNILVR",
            "isin": "INE030A01027",
            "sector": "Consumer Goods & FMCG",
            "description": "India's largest consumer goods company touching 9 out of 10 Indian households across food, home, and personal care.",
            "filing_file": None,
        },
    ]

    for c in real_companies:
        has_file = c.get("filing_file") is not None
        asset_obj = Asset(
            id=c["id"],
            name=c["name"],
            symbol=c["symbol"],
            exchange="NSE",
            isin=c["isin"],
            asset_type="equity",
            sector=c["sector"],
            description=c["description"],
            dataset_type="real_listed",
            document_status="indexed" if has_file else "documents_pending",
            document_count=0,
            market_cap_category="Large Cap",
        )
        repo.add_asset(asset_obj)

        if has_file and c.get("filing_file"):
            doc_path = base_data_dir / c["filing_file"]
            if doc_path.exists():
                ingest_document_file(
                    asset_id=asset_obj.id,
                    file_path=str(doc_path),
                    repo=repo,
                    source=c.get("filing_source", "Exchange Regulatory Filing"),
                    source_date=c.get("filing_date", "2024-10-15"),
                    doc_type=c.get("doc_type", "quarterly_filing"),
                )

    print(f"Seed data loaded successfully: 14 total companies (11 real listed + 3 synthetic benchmarks).")

    # Initialize 12-category document coverage catalog and market data readiness
    try:
        from tools.document_coverage_engine import build_and_ingest_all_stock_coverage
        build_and_ingest_all_stock_coverage(repo=repo, ingest_pending=False)
        print("Document coverage catalog (12 categories) and market data initialized.")
    except Exception as e:
        print(f"Notice: Document coverage sync in seed skipped: {e}")


if __name__ == "__main__":
    seed_database()
