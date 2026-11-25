"""API route definitions for ThesisForge AI (SRS Section 9.1 & Expert Upgrade Specification)."""

from __future__ import annotations
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

from database.models import Asset, DocumentRecord, FinalReport, ResearchRunRecord, SignalCard, SignalRecord
from database.repository import Repository
from orchestration.workflow import InvestmentCommitteeOrchestrator
from tools.document_tools import ingest_document_file

router = APIRouter(prefix="/api/v1")
repo = Repository()
orchestrator = InvestmentCommitteeOrchestrator(repo=repo)


class CreateRunRequest(BaseModel):
    asset_id: str
    document_ids: Optional[List[str]] = None
    research_mode: str = "swing"  # "intraday", "swing", "positional"
    risk_budget_rupees: Optional[float] = 10000.0
    include_risk_agent: bool = True
    risk_veto_threshold: Optional[float] = 0.65


class CreateRunResponse(BaseModel):
    run_id: str
    status: str
    asset_id: str


@router.get("/assets", response_model=List[Asset])
def list_assets(
    search: Optional[str] = Query(None, description="Search query matching company name or symbol"),
    sector: Optional[str] = Query(None, description="Filter by sector name"),
    dataset_type: Optional[str] = Query(None, description="Filter by dataset_type: 'real_listed' or 'synthetic_demo'"),
    document_status: Optional[str] = Query(None, description="Filter by document_status: 'indexed' or 'documents_pending'"),
):
    """Retrieve companies with optional multi-field filtering."""
    return repo.list_assets(
        search=search,
        sector=sector,
        dataset_type=dataset_type,
        document_status=document_status,
    )


@router.get("/sectors", response_model=List[str])
def list_sectors():
    """Retrieve all distinct sectors represented in the asset universe."""
    return repo.list_sectors()


@router.post("/assets", response_model=Asset, status_code=201)
def add_new_asset(asset: Asset):
    """Register a new listed equity dynamically without requiring code changes."""
    return repo.add_asset(asset)


@router.get("/assets/{asset_id}")
def get_asset(asset_id: str):
    asset = repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return asset


@router.get("/assets/{asset_id}/documents", response_model=List[DocumentRecord])
def list_asset_documents(asset_id: str):
    asset = repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return repo.list_documents_for_asset(asset.id)


@router.post("/documents/ingest")
async def ingest_document(
    asset_id: str = Form(...),
    source: str = Form("Manual Upload"),
    source_date: Optional[str] = Form(None),
    doc_type: str = Form("annual_report"),
    file: UploadFile = File(...),
):
    asset = repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    storage_dir = Path(__file__).resolve().parent.parent / "storage" / "documents"
    storage_dir.mkdir(parents=True, exist_ok=True)

    dest_filename = f"{uuid4().hex[:8]}_{file.filename}"
    dest_path = storage_dir / dest_filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc = ingest_document_file(
            asset_id=asset.id,
            file_path=str(dest_path),
            repo=repo,
            source=source,
            source_date=source_date,
            doc_type=doc_type,
        )
        return {"status": "success", "document": doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(e)}")


def _run_orchestrator_job(run_id: str, asset_id: str, config: Dict[str, Any]):
    try:
        orchestrator.run(asset_id=asset_id, run_id=run_id, config=config)
    except Exception as e:
        print(f"[Error in research run {run_id}]: {e}")


@router.post("/research-runs", response_model=CreateRunResponse, status_code=202)
def create_research_run(req: CreateRunRequest, background_tasks: BackgroundTasks):
    asset = repo.get_asset(req.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {req.asset_id} not found")

    run_id = str(uuid4())
    config = {
        "research_mode": req.research_mode,
        "risk_budget_rupees": req.risk_budget_rupees or 10000.0,
        "include_risk_agent": req.include_risk_agent,
        "risk_veto_threshold": req.risk_veto_threshold or 0.65,
    }

    background_tasks.add_task(_run_orchestrator_job, run_id, asset.id, config)
    return CreateRunResponse(run_id=run_id, status="queued", asset_id=asset.id)


@router.get("/research-runs/{run_id}")
def get_research_run_status(run_id: str):
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Research run {run_id} not found")
    return run


@router.get("/research-runs/{run_id}/trace")
def get_research_run_trace(run_id: str):
    events = repo.get_run_events(run_id)
    integrity = repo.verify_run_log_integrity(run_id)
    return {
        "run_id": run_id,
        "event_count": len(events),
        "hash_chain_valid": integrity,
        "trace": [e.model_dump() for e in events],
    }


@router.get("/research-runs/{run_id}/evidence")
def get_research_run_evidence(run_id: str):
    items = repo.get_evidence_for_run(run_id)
    return {
        "run_id": run_id,
        "count": len(items),
        "evidence": [it.model_dump() for it in items],
    }


@router.get("/research-runs/{run_id}/report", response_model=FinalReport)
def get_research_run_report(run_id: str):
    report = repo.get_final_report(run_id)
    if not report:
        run = repo.get_run(run_id)
        if run and run.status not in ("COMPLETED", "FAILED", "INSUFFICIENT_EVIDENCE"):
            raise HTTPException(status_code=202, detail=f"Research run is still in progress: status '{run.status}'")
        raise HTTPException(status_code=404, detail=f"Report not found for run {run_id}")
    return report


@router.get("/research-runs/{run_id}/signal-card")
def get_run_signal_card(run_id: str):
    """Retrieve the mandatory structured signal card for a research run."""
    report = repo.get_final_report(run_id)
    if not report or not report.signal_card:
        raise HTTPException(status_code=404, detail=f"Signal card not found for run {run_id}")
    return report.signal_card


@router.get("/research-runs/{run_id}/expert-reviews")
def get_run_expert_reviews(run_id: str):
    """Retrieve the 10 simulated methodology-inspired persona reviews."""
    reviews = repo.get_expert_reviews(run_id)
    return {
        "run_id": run_id,
        "persona_count": len(reviews),
        "reviews": [r["finding"] for r in reviews],
    }


@router.get("/signals", response_model=List[SignalRecord])
def list_signals(
    asset_id: Optional[str] = Query(None, description="Filter signals by asset ID"),
    symbol: Optional[str] = Query(None, description="Filter signals by ticker symbol"),
    limit: int = Query(50, description="Max signals to return"),
):
    """Retrieve historical signals from the persistent signal ledger."""
    return repo.get_signal_records(asset_id=asset_id, symbol=symbol, limit=limit)


@router.post("/research-runs/{run_id}/retry")
def retry_research_run(run_id: str, background_tasks: BackgroundTasks):
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    background_tasks.add_task(_run_orchestrator_job, run.id, run.asset_id, run.config)
    return {"run_id": run.id, "status": "retrying"}


# ---------------------------------------------------------------------------
# Section 6 & 7: Document Coverage & Research Readiness Dashboard Endpoints
# ---------------------------------------------------------------------------

@router.get("/coverage")
def get_all_stock_coverage_summary():
    """Retrieve comprehensive coverage and research-readiness audit for all stocks."""
    readiness_list = repo.list_all_readiness()
    summary_stats = repo.get_coverage_summary()
    return {
        "total_assets": len(readiness_list),
        "readiness_records": [r.model_dump() for r in readiness_list],
        "category_summaries": summary_stats,
    }


@router.get("/coverage/{asset_id}")
def get_asset_coverage_detail(asset_id: str):
    """Retrieve the standard 12-category document package status for a specific stock."""
    asset = repo.get_asset(asset_id)
    if not asset:
        # Check by symbol
        assets = repo.list_assets(search=asset_id)
        if assets:
            asset = assets[0]
        else:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    items = repo.list_coverage_for_asset(asset.id)
    readiness = repo.get_asset_readiness(asset.id)
    market_summary = repo.get_market_data_summary(asset.symbol)

    return {
        "asset": asset.model_dump(),
        "readiness": readiness.model_dump() if readiness else None,
        "market_summary": market_summary,
        "total_categories": len(items),
        "catalog_items": [it.model_dump() for it in items],
    }


@router.get("/market-data/{symbol}")
def get_asset_market_data(
    symbol: str,
    timeframe: str = Query("swing", description="intraday | swing | positional"),
):
    """Retrieve quantitative market structure, technical indicators, and OHLCV summary."""
    from tools.market_data_tools import compute_quantitative_market_structure
    res = compute_quantitative_market_structure(symbol.upper(), repo, research_mode=timeframe)
    return res


@router.post("/coverage/refresh")
def refresh_coverage_audit(background_tasks: BackgroundTasks):
    """Trigger background refresh of document coverage and market data ingestion."""
    from tools.document_coverage_engine import build_and_ingest_all_stock_coverage

    def _job():
        build_and_ingest_all_stock_coverage(repo)

    background_tasks.add_task(_job)
    return {"status": "refresh_initiated", "message": "Coverage audit and market data refresh in progress."}


# ---------------------------------------------------------------------------
# Section 8: Audit Trail Hash-Chain Integrity & Reconciliation Endpoints
# ---------------------------------------------------------------------------

@router.get("/audit/integrity")
def get_audit_trail_integrity():
    """Verify cryptographic hash-chain integrity across all research runs in the audit ledger."""
    return repo.verify_all_run_logs_integrity()


@router.get("/audit/reconciliation")
def get_audit_reconciliation_summary():
    """Retrieve reconciled document counts, monitored categories, and lifecycle distribution."""
    with repo._get_connection() as conn:
        cur = conn.cursor()
        total_assets = cur.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        total_docs = cur.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        total_chunks = cur.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]
        total_catalog = cur.execute("SELECT COUNT(*) FROM document_coverage_catalog").fetchone()[0]
        
        stages = [
            {"lifecycle_stage": r[0], "count": r[1]}
            for r in cur.execute(
                "SELECT lifecycle_stage, COUNT(*) as cnt FROM document_coverage_catalog GROUP BY lifecycle_stage ORDER BY cnt DESC"
            ).fetchall()
        ]
        readiness_dist = [
            {"status": r[0], "count": r[1]}
            for r in cur.execute(
                "SELECT overall_readiness, COUNT(*) as cnt FROM asset_research_readiness GROUP BY overall_readiness ORDER BY cnt DESC"
            ).fetchall()
        ]

    return {
        "status": "reconciled",
        "total_assets": total_assets,
        "physical_documents_indexed": total_docs,
        "document_chunks_indexed": total_chunks,
        "monitored_catalog_slots": total_catalog,
        "catalog_slots_per_asset": 12,
        "lifecycle_stage_breakdown": stages,
        "research_readiness_distribution": readiness_dist,
        "anti_fabrication_policy": "Zero synthetic financial data. Inaccessible filings preserved as DOCUMENT_PENDING with official IR/NSE links.",
    }


