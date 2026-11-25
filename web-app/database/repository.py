"""Database persistence and append-only audit repository for ThesisForge AI."""

from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from database.models import (
    Asset,
    DocumentRecord,
    DocumentChunk,
    EvidenceItem,
    ResearchRunRecord,
    RunEvent,
    FinalReport,
    SignalCard,
    SignalRecord,
    DocumentCoverageItem,
    HistoricalBar,
    AssetReadinessRecord,
)


class Repository:
    """Thread-safe, SQLite-backed repository implementing the SRS Section 8 schema

    and the Section 12 append-only run log requirement.
    """

    def __init__(self, db_path: Optional[str] = None, log_file: Optional[str] = None):
        if db_path is None:
            storage_dir = Path(__file__).resolve().parent.parent / "storage"
            storage_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(storage_dir / "thesisforge.db")
        self.db_path = db_path

        if log_file is None:
            # Place logs in MTM606/logs/run_log.jsonl
            mtm606_dir = Path(__file__).resolve().parent.parent.parent
            logs_dir = mtm606_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_file = str(logs_dir / "run_log.jsonl")
        self.log_file = log_file

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL UNIQUE,
                exchange TEXT NOT NULL DEFAULT 'NSE',
                isin TEXT,
                asset_type TEXT NOT NULL DEFAULT 'equity',
                sector TEXT,
                description TEXT,
                dataset_type TEXT NOT NULL DEFAULT 'real_listed',
                document_status TEXT NOT NULL DEFAULT 'documents_pending'
            );
            """)

            # Automatic non-destructive migration for existing assets table
            try:
                cursor.execute("ALTER TABLE assets ADD COLUMN dataset_type TEXT DEFAULT 'real_listed'")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE assets ADD COLUMN document_status TEXT DEFAULT 'documents_pending'")
            except sqlite3.OperationalError:
                pass

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL REFERENCES assets(id),
                filename TEXT NOT NULL,
                source TEXT NOT NULL,
                source_date TEXT,
                content_hash TEXT NOT NULL UNIQUE,
                storage_path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'indexed',
                page_count INTEGER NOT NULL DEFAULT 1,
                doc_type TEXT NOT NULL DEFAULT 'annual_report'
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id),
                asset_id TEXT NOT NULL REFERENCES assets(id),
                page_number INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_runs (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL REFERENCES assets(id),
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                config TEXT NOT NULL DEFAULT '{}'
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_items (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES research_runs(id),
                document_id TEXT NOT NULL REFERENCES documents(id),
                document_name TEXT NOT NULL,
                evidence_code TEXT NOT NULL,
                page_number INTEGER,
                passage_text TEXT NOT NULL,
                evidence_type TEXT,
                reporting_period TEXT,
                published_at TEXT,
                content_hash TEXT NOT NULL,
                relevance_score REAL NOT NULL DEFAULT 1.0,
                UNIQUE(run_id, evidence_code)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_outputs (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES research_runs(id),
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                output_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL UNIQUE REFERENCES research_runs(id),
                recommendation TEXT NOT NULL,
                report_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL REFERENCES research_runs(id),
                sequence_no INTEGER NOT NULL,
                occurred_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                agent_or_tool TEXT NOT NULL,
                payload TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                UNIQUE(run_id, sequence_no)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_records (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES research_runs(id),
                asset_id TEXT NOT NULL REFERENCES assets(id),
                symbol TEXT NOT NULL,
                mode TEXT NOT NULL,
                decision TEXT NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                target_1 REAL,
                target_2 REAL,
                risk_reward REAL,
                status TEXT NOT NULL DEFAULT 'active',
                outcome_r_multiple REAL,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                notes TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_reviews (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES research_runs(id),
                persona_id TEXT NOT NULL,
                persona_name TEXT NOT NULL,
                lens_title TEXT NOT NULL,
                finding_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_coverage_catalog (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL REFERENCES assets(id),
                symbol TEXT NOT NULL,
                category_key TEXT NOT NULL,
                category_name TEXT NOT NULL,
                period TEXT NOT NULL,
                document_id TEXT REFERENCES documents(id),
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                lifecycle_stage TEXT NOT NULL DEFAULT 'DOCUMENT_PENDING',
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL DEFAULT '',
                publication_date TEXT,
                page_count INTEGER NOT NULL DEFAULT 0,
                extraction_status TEXT NOT NULL DEFAULT 'pending',
                notes TEXT,
                last_checked TEXT NOT NULL
            );
            """)

            try:
                cursor.execute("ALTER TABLE document_coverage_catalog ADD COLUMN lifecycle_stage TEXT DEFAULT 'DOCUMENT_PENDING'")
            except sqlite3.OperationalError:
                pass

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_market_data (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                adjusted_close REAL NOT NULL,
                corporate_action_notes TEXT,
                UNIQUE(symbol, trade_date)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_research_readiness (
                asset_id TEXT PRIMARY KEY REFERENCES assets(id),
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                total_required_categories INTEGER NOT NULL DEFAULT 12,
                available_docs_count INTEGER NOT NULL DEFAULT 0,
                missing_docs_count INTEGER NOT NULL DEFAULT 0,
                outdated_docs_count INTEGER NOT NULL DEFAULT 0,
                pending_docs_count INTEGER NOT NULL DEFAULT 0,
                failed_docs_count INTEGER NOT NULL DEFAULT 0,
                market_data_bars INTEGER NOT NULL DEFAULT 0,
                market_data_start_date TEXT,
                market_data_end_date TEXT,
                historical_market_coverage_pct REAL NOT NULL DEFAULT 0.0,
                fundamental_coverage_pct REAL NOT NULL DEFAULT 0.0,
                technical_coverage_pct REAL NOT NULL DEFAULT 0.0,
                technical_readiness TEXT NOT NULL DEFAULT 'TECHNICAL_READY',
                fundamental_readiness TEXT NOT NULL DEFAULT 'DOCUMENTS_PENDING',
                event_readiness TEXT NOT NULL DEFAULT 'EVENT_TRACKING_PENDING',
                overall_readiness TEXT NOT NULL DEFAULT 'DOCUMENTS_PENDING',
                readiness_explanation TEXT,
                last_updated TEXT NOT NULL
            );
            """)

            try:
                cursor.execute("ALTER TABLE asset_research_readiness ADD COLUMN technical_readiness TEXT DEFAULT 'TECHNICAL_READY'")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE asset_research_readiness ADD COLUMN fundamental_readiness TEXT DEFAULT 'DOCUMENTS_PENDING'")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE asset_research_readiness ADD COLUMN event_readiness TEXT DEFAULT 'EVENT_TRACKING_PENDING'")
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def add_asset(self, asset: Asset) -> Asset:
        with self._get_connection() as conn:
            existing = conn.execute("SELECT id FROM assets WHERE id = ? OR symbol = ?", (asset.id, asset.symbol.upper())).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE assets SET
                        name = ?, symbol = ?, exchange = ?, isin = ?, asset_type = ?,
                        sector = ?, description = ?, dataset_type = ?, document_status = ?
                    WHERE id = ?
                    """,
                    (
                        asset.name,
                        asset.symbol.upper(),
                        asset.exchange,
                        asset.isin,
                        asset.asset_type,
                        asset.sector,
                        asset.description,
                        asset.dataset_type,
                        asset.document_status,
                        existing["id"],
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO assets (id, name, symbol, exchange, isin, asset_type, sector, description, dataset_type, document_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        asset.id,
                        asset.name,
                        asset.symbol.upper(),
                        asset.exchange,
                        asset.isin,
                        asset.asset_type,
                        asset.sector,
                        asset.description,
                        asset.dataset_type,
                        asset.document_status,
                    ),
                )
            conn.commit()
        return asset

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM assets WHERE id = ? OR symbol = ?", (asset_id, asset_id.upper())).fetchone()
            if not row:
                return None
            data = dict(row)
            stats = conn.execute(
                "SELECT COUNT(*) as doc_cnt, MAX(source_date) as last_date FROM documents WHERE asset_id = ?",
                (data["id"],),
            ).fetchone()
            doc_cnt = stats["doc_cnt"] if stats else 0
            last_date = stats["last_date"] if stats else None

            data["document_count"] = doc_cnt
            data["last_document_update"] = last_date
            data["document_status"] = "indexed" if doc_cnt > 0 else "documents_pending"
            return Asset(**data)

    def list_assets(
        self,
        search: Optional[str] = None,
        sector: Optional[str] = None,
        dataset_type: Optional[str] = None,
        document_status: Optional[str] = None,
    ) -> List[Asset]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM assets ORDER BY name ASC").fetchall()
            doc_stats = conn.execute(
                "SELECT asset_id, COUNT(*) as doc_cnt, MAX(source_date) as last_date FROM documents GROUP BY asset_id"
            ).fetchall()
            stats_map = {r["asset_id"]: (r["doc_cnt"], r["last_date"]) for r in doc_stats}

            assets: List[Asset] = []
            for r in rows:
                d = dict(r)
                doc_cnt, last_date = stats_map.get(d["id"], (0, None))
                d["document_count"] = doc_cnt
                d["last_document_update"] = last_date
                d["document_status"] = "indexed" if doc_cnt > 0 else "documents_pending"
                asset = Asset(**d)

                if search:
                    s_lower = search.strip().lower()
                    if s_lower not in asset.name.lower() and s_lower not in asset.symbol.lower():
                        continue

                if sector and sector.strip().lower() != "all":
                    if (asset.sector or "").strip().lower() != sector.strip().lower():
                        continue

                if dataset_type and dataset_type.strip().lower() != "all":
                    if asset.dataset_type.strip().lower() != dataset_type.strip().lower():
                        continue

                if document_status and document_status.strip().lower() != "all":
                    if asset.document_status.strip().lower() != document_status.strip().lower():
                        continue

                assets.append(asset)
            return assets

    def list_sectors(self) -> List[str]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT sector FROM assets WHERE sector IS NOT NULL AND sector != '' ORDER BY sector ASC"
            ).fetchall()
            return [r["sector"] for r in rows]

    def add_document(self, doc: DocumentRecord) -> DocumentRecord:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO documents (id, asset_id, filename, source, source_date, content_hash, storage_path, status, page_count, doc_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (doc.id, doc.asset_id, doc.filename, doc.source, doc.source_date, doc.content_hash, doc.storage_path, doc.status, doc.page_count, doc.doc_type),
            )
            conn.commit()
        return doc

    def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if not row:
                return None
            return DocumentRecord(**dict(row))

    def list_documents_for_asset(self, asset_id: str) -> List[DocumentRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents WHERE asset_id = ? ORDER BY filename ASC", (asset_id,)).fetchall()
            return [DocumentRecord(**dict(r)) for r in rows]

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for ch in chunks:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO document_chunks (id, document_id, asset_id, page_number, chunk_index, content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (ch.id, ch.document_id, ch.asset_id, ch.page_number, ch.chunk_index, ch.content, json.dumps(ch.metadata)),
                )
            conn.commit()

    def get_chunks_for_asset(self, asset_id: str) -> List[DocumentChunk]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM document_chunks WHERE asset_id = ? ORDER BY page_number, chunk_index",
                (asset_id,),
            ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["metadata"] = json.loads(d.get("metadata", "{}") or "{}")
                result.append(DocumentChunk(**d))
            return result

    def create_run(self, run: ResearchRunRecord) -> ResearchRunRecord:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO research_runs (id, asset_id, status, created_at, completed_at, config)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run.id, run.asset_id, run.status, run.created_at, run.completed_at, json.dumps(run.config, default=str)),
            )
            conn.commit()
        return run

    def update_run_status(self, run_id: str, status: str, completed_at: Optional[str] = None) -> None:
        with self._get_connection() as conn:
            if completed_at:
                conn.execute(
                    "UPDATE research_runs SET status = ?, completed_at = ? WHERE id = ?",
                    (status, completed_at, run_id),
                )
            else:
                conn.execute("UPDATE research_runs SET status = ? WHERE id = ?", (status, run_id))
            conn.commit()

    def get_run(self, run_id: str) -> Optional[ResearchRunRecord]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM research_runs WHERE id = ?", (run_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["config"] = json.loads(d.get("config", "{}") or "{}")
            return ResearchRunRecord(**d)

    def add_evidence_items(self, items: List[EvidenceItem]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for it in items:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO evidence_items 
                    (id, run_id, document_id, document_name, evidence_code, page_number, passage_text, evidence_type, reporting_period, published_at, content_hash, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        it.id,
                        it.run_id,
                        it.document_id,
                        it.document_name,
                        it.evidence_code,
                        it.page_number,
                        it.passage_text,
                        it.evidence_type,
                        it.reporting_period,
                        it.published_at,
                        it.content_hash,
                        it.relevance_score,
                    ),
                )
            conn.commit()

    def get_evidence_for_run(self, run_id: str) -> List[EvidenceItem]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM evidence_items WHERE run_id = ? ORDER BY evidence_code ASC",
                (run_id,),
            ).fetchall()
            return [EvidenceItem(**dict(r)) for r in rows]

    def get_evidence_by_code(self, run_id: str, evidence_code: str) -> Optional[EvidenceItem]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM evidence_items WHERE run_id = ? AND evidence_code = ?",
                (run_id, evidence_code),
            ).fetchone()
            if not row:
                return None
            return EvidenceItem(**dict(row))

    def save_agent_output(self, run_id: str, agent_name: str, status: str, output: Dict[str, Any]) -> None:
        with self._get_connection() as conn:
            out_id = str(uuid4())
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                INSERT INTO agent_outputs (id, run_id, agent_name, status, output_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (out_id, run_id, agent_name, status, json.dumps(output, default=str), now_iso),
            )
            conn.commit()

    def get_agent_outputs_for_run(self, run_id: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT agent_name, output_json FROM agent_outputs WHERE run_id = ? ORDER BY created_at ASC",
                (run_id,),
            ).fetchall()
            results = {}
            for r in rows:
                results[r["agent_name"]] = json.loads(r["output_json"])
            return results

    def save_final_report(self, run_id: str, report: FinalReport) -> None:
        with self._get_connection() as conn:
            rep_id = str(uuid4())
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                INSERT OR REPLACE INTO reports (id, run_id, recommendation, report_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (rep_id, run_id, report.recommendation, json.dumps(report.model_dump(mode="json"), default=str), now_iso),
            )
            conn.commit()

    def get_final_report(self, run_id: str) -> Optional[FinalReport]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT report_json FROM reports WHERE run_id = ?", (run_id,)).fetchone()
            if not row:
                return None
            return FinalReport(**json.loads(row["report_json"]))

    def append_event(
        self,
        run_id: str,
        event_type: str,
        agent_or_tool: str,
        payload: Dict[str, Any],
    ) -> RunEvent:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            last_event = cursor.execute(
                "SELECT sequence_no, event_hash FROM run_events WHERE run_id = ? ORDER BY sequence_no DESC LIMIT 1",
                (run_id,),
            ).fetchone()

            if last_event:
                sequence_no = last_event["sequence_no"] + 1
                previous_hash = last_event["event_hash"]
            else:
                sequence_no = 1
                previous_hash = "GENESIS_00000000000000000000000000000000"

            occurred_at = datetime.now(timezone.utc).isoformat()
            payload_str = json.dumps(payload, sort_keys=True, default=str)

            hash_content = f"{run_id}:{sequence_no}:{occurred_at}:{event_type}:{agent_or_tool}:{payload_str}:{previous_hash}"
            event_hash = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()

            cursor.execute(
                """
                INSERT INTO run_events (run_id, sequence_no, occurred_at, event_type, agent_or_tool, payload, previous_hash, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    sequence_no,
                    occurred_at,
                    event_type,
                    agent_or_tool,
                    payload_str,
                    previous_hash,
                    event_hash,
                ),
            )
            event_id = cursor.lastrowid
            conn.commit()

        run_event = RunEvent(
            id=event_id,
            run_id=run_id,
            sequence_no=sequence_no,
            occurred_at=occurred_at,
            event_type=event_type,
            agent_or_tool=agent_or_tool,
            payload=payload,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(run_event.model_dump_json() + "\n")
        except Exception as e:
            print(f"[Warning] Failed to append to JSONL log file: {e}")

        return run_event

    def get_run_events(self, run_id: str) -> List[RunEvent]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM run_events WHERE run_id = ? ORDER BY sequence_no ASC",
                (run_id,),
            ).fetchall()
            events = []
            for r in rows:
                d = dict(r)
                d["payload"] = json.loads(d.get("payload", "{}") or "{}")
                events.append(RunEvent(**d))
            return events

    def verify_run_log_integrity(self, run_id: str) -> bool:
        events = self.get_run_events(run_id)
        if not events:
            return True

        expected_prev = "GENESIS_00000000000000000000000000000000"
        for ev in events:
            if ev.previous_hash != expected_prev:
                return False
            payload_str = json.dumps(ev.payload, sort_keys=True, default=str)
            hash_content = f"{ev.run_id}:{ev.sequence_no}:{ev.occurred_at}:{ev.event_type}:{ev.agent_or_tool}:{payload_str}:{ev.previous_hash}"
            calc_hash = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()
            if calc_hash != ev.event_hash:
                return False
            expected_prev = ev.event_hash
        return True

    def verify_all_run_logs_integrity(self, exclude_test_runs: bool = True) -> Dict[str, Any]:
        """Verify the cryptographic hash-chain integrity of all research runs in the audit ledger.
        
        If exclude_test_runs is True, synthetic test runs (status='TEST') where tampering was
        deliberately injected by unit tests are excluded from the production audit score.
        """
        with self._get_connection() as conn:
            if exclude_test_runs:
                rows = conn.execute(
                    """
                    SELECT DISTINCT r.id FROM research_runs r
                    JOIN run_events e ON r.id = e.run_id
                    WHERE r.status != 'TEST'
                    ORDER BY r.created_at ASC
                    """
                ).fetchall()
            else:
                rows = conn.execute("SELECT DISTINCT run_id FROM run_events ORDER BY id ASC").fetchall()
            run_ids = [r[0] for r in rows]

        details = []
        valid_count = 0
        invalid_count = 0

        for r_id in run_ids:
            is_valid = self.verify_run_log_integrity(r_id)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
            details.append({"run_id": r_id, "is_valid": is_valid})

        return {
            "total_runs_checked": len(run_ids),
            "valid_runs": valid_count,
            "invalid_runs": invalid_count,
            "all_valid": (invalid_count == 0),
            "excluded_test_runs": exclude_test_runs,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }

    # -----------------------------------------------------------------------
    # Signal Ledger Methods (Section 5 & 7 of Expert Specification)
    # -----------------------------------------------------------------------

    def save_signal_record(self, signal: SignalRecord) -> SignalRecord:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO signal_records (
                    id, run_id, asset_id, symbol, mode, decision,
                    entry_price, stop_loss, target_1, target_2, risk_reward,
                    status, outcome_r_multiple, created_at, resolved_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.id,
                    signal.run_id,
                    signal.asset_id,
                    signal.symbol,
                    signal.mode,
                    signal.decision,
                    signal.entry_price,
                    signal.stop_loss,
                    signal.target_1,
                    signal.target_2,
                    signal.risk_reward,
                    signal.status,
                    signal.outcome_r_multiple,
                    signal.created_at,
                    signal.resolved_at,
                    signal.notes,
                ),
            )
            conn.commit()
        return signal

    def get_signal_records(
        self,
        asset_id: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 50,
    ) -> List[SignalRecord]:
        with self._get_connection() as conn:
            query = "SELECT * FROM signal_records"
            params: List[Any] = []
            conditions: List[str] = []

            if asset_id:
                conditions.append("asset_id = ?")
                params.append(asset_id)
            if symbol:
                conditions.append("symbol = ?")
                params.append(symbol.upper())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, tuple(params)).fetchall()
            return [SignalRecord(**dict(r)) for r in rows]

    def update_signal_status(
        self,
        signal_id: str,
        status: str,
        outcome_r_multiple: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE signal_records
                SET status = ?, outcome_r_multiple = ?, notes = ?, resolved_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    outcome_r_multiple,
                    notes,
                    datetime.now(timezone.utc).isoformat(),
                    signal_id,
                ),
            )
            conn.commit()

    # -----------------------------------------------------------------------
    # Expert Review Findings Persistence (Section 3 of Expert Specification)
    # -----------------------------------------------------------------------

    def save_expert_reviews(self, run_id: str, findings: List[Any]) -> None:
        with self._get_connection() as conn:
            now_iso = datetime.now(timezone.utc).isoformat()
            for f in findings:
                finding_dict = f.model_dump() if hasattr(f, "model_dump") else dict(f)
                f_id = f"{run_id}_{finding_dict.get('persona_id', 'unknown')}"
                conn.execute(
                    """
                    INSERT OR REPLACE INTO expert_reviews (
                        id, run_id, persona_id, persona_name, lens_title, finding_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f_id,
                        run_id,
                        finding_dict.get("persona_id", ""),
                        finding_dict.get("persona_name", ""),
                        finding_dict.get("lens_title", ""),
                        json.dumps(finding_dict, default=str),
                        now_iso,
                    ),
                )
            conn.commit()

    def get_expert_reviews(self, run_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM expert_reviews WHERE run_id = ? ORDER BY persona_id ASC",
                (run_id,),
            ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["finding"] = json.loads(d["finding_json"])
                results.append(d)
            return results

    # -----------------------------------------------------------------------
    # Document Coverage & Standard Package Catalog Methods (Section 3 & 6)
    # -----------------------------------------------------------------------

    def upsert_coverage_item(self, item: DocumentCoverageItem) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO document_coverage_catalog (
                    id, asset_id, symbol, category_key, category_name, period,
                    document_id, title, status, lifecycle_stage, source_name, source_url,
                    publication_date, page_count, extraction_status, notes, last_checked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.asset_id,
                    item.symbol,
                    item.category_key,
                    item.category_name,
                    item.period,
                    item.document_id,
                    item.title,
                    item.status,
                    getattr(item, "lifecycle_stage", "DOCUMENT_PENDING"),
                    item.source_name,
                    item.source_url,
                    item.publication_date,
                    item.page_count,
                    item.extraction_status,
                    item.notes,
                    item.last_checked,
                ),
            )
            conn.commit()

    def list_coverage_for_asset(self, asset_id_or_symbol: str) -> List[DocumentCoverageItem]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM document_coverage_catalog
                WHERE asset_id = ? OR symbol = ?
                ORDER BY category_key ASC, period DESC
                """,
                (asset_id_or_symbol, asset_id_or_symbol.upper()),
            ).fetchall()
            return [DocumentCoverageItem(**dict(r)) for r in rows]

    def get_coverage_summary(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    a.id as asset_id,
                    a.symbol,
                    a.name,
                    a.dataset_type,
                    a.document_status,
                    COUNT(c.id) as total_items,
                    SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) as available_count,
                    SUM(CASE WHEN c.status = 'missing' THEN 1 ELSE 0 END) as missing_count,
                    SUM(CASE WHEN c.status = 'outdated' THEN 1 ELSE 0 END) as outdated_count,
                    SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN c.status = 'failed' THEN 1 ELSE 0 END) as failed_count
                FROM assets a
                LEFT JOIN document_coverage_catalog c ON a.id = c.asset_id
                GROUP BY a.id, a.symbol, a.name, a.dataset_type, a.document_status
                ORDER BY a.dataset_type DESC, a.symbol ASC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    # -----------------------------------------------------------------------
    # Historical Market Data (OHLCV) Methods (Section 4)
    # -----------------------------------------------------------------------

    def upsert_historical_bars(self, bars: List[HistoricalBar]) -> int:
        if not bars:
            return 0
        with self._get_connection() as conn:
            inserted = 0
            for b in bars:
                bar_id = f"{b.symbol}_{b.trade_date}"
                conn.execute(
                    """
                    INSERT OR REPLACE INTO historical_market_data (
                        id, symbol, trade_date, open, high, low, close, volume,
                        adjusted_close, corporate_action_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bar_id,
                        b.symbol.upper(),
                        b.trade_date,
                        b.open,
                        b.high,
                        b.low,
                        b.close,
                        b.volume,
                        b.adjusted_close,
                        b.corporate_action_notes,
                    ),
                )
                inserted += 1
            conn.commit()
            return inserted

    def get_historical_bars(self, symbol: str, limit: int = 1260) -> List[HistoricalBar]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT symbol, trade_date, open, high, low, close, volume,
                       adjusted_close, corporate_action_notes
                FROM historical_market_data
                WHERE symbol = ?
                ORDER BY trade_date ASC
                LIMIT ?
                """,
                (symbol.upper(), limit),
            ).fetchall()
            return [HistoricalBar(**dict(r)) for r in rows]

    def get_market_data_summary(self, symbol: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    symbol,
                    COUNT(id) as total_bars,
                    MIN(trade_date) as start_date,
                    MAX(trade_date) as end_date,
                    MIN(low) as lowest_price,
                    MAX(high) as highest_price,
                    AVG(volume) as avg_volume
                FROM historical_market_data
                WHERE symbol = ?
                GROUP BY symbol
                """,
                (symbol.upper(),),
            ).fetchone()
            if row:
                d = dict(row)
                d["has_data"] = d["total_bars"] > 0
                return d
            return {
                "symbol": symbol.upper(),
                "total_bars": 0,
                "start_date": None,
                "end_date": None,
                "lowest_price": None,
                "highest_price": None,
                "avg_volume": None,
                "has_data": False,
            }

    # -----------------------------------------------------------------------
    # Asset Research Readiness Methods (Section 6)
    # -----------------------------------------------------------------------

    def upsert_asset_readiness(self, record: AssetReadinessRecord) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO asset_research_readiness (
                    asset_id, symbol, name, total_required_categories,
                    available_docs_count, missing_docs_count, outdated_docs_count,
                    pending_docs_count, failed_docs_count, market_data_bars,
                    market_data_start_date, market_data_end_date,
                    historical_market_coverage_pct, fundamental_coverage_pct,
                    technical_coverage_pct, technical_readiness,
                    fundamental_readiness, event_readiness,
                    overall_readiness, readiness_explanation, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.asset_id,
                    record.symbol.upper(),
                    record.name,
                    record.total_required_categories,
                    record.available_docs_count,
                    record.missing_docs_count,
                    record.outdated_docs_count,
                    record.pending_docs_count,
                    record.failed_docs_count,
                    record.market_data_bars,
                    record.market_data_start_date,
                    record.market_data_end_date,
                    record.historical_market_coverage_pct,
                    record.fundamental_coverage_pct,
                    record.technical_coverage_pct,
                    getattr(record, "technical_readiness", "TECHNICAL_READY"),
                    getattr(record, "fundamental_readiness", "DOCUMENTS_PENDING"),
                    getattr(record, "event_readiness", "EVENT_TRACKING_PENDING"),
                    record.overall_readiness,
                    record.readiness_explanation,
                    record.last_updated,
                ),
            )
            conn.commit()

    def get_asset_readiness(self, asset_id_or_symbol: str) -> Optional[AssetReadinessRecord]:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM asset_research_readiness
                WHERE asset_id = ? OR symbol = ?
                """,
                (asset_id_or_symbol, asset_id_or_symbol.upper()),
            ).fetchone()
            if row:
                return AssetReadinessRecord(**dict(row))
            return None

    def list_all_readiness(self) -> List[AssetReadinessRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM asset_research_readiness
                ORDER BY overall_readiness ASC, symbol ASC
                """
            ).fetchall()
            return [AssetReadinessRecord(**dict(r)) for r in rows]

    def clean_test_documents(self) -> int:
        """Purge temporary 'Test Doc' entries created during test runs."""
        with self._get_connection() as conn:
            # First find matching doc IDs
            rows = conn.execute(
                "SELECT id FROM documents WHERE filename = 'Test Doc' OR storage_path = 'test_path'"
            ).fetchall()
            doc_ids = [r[0] for r in rows]
            if not doc_ids:
                return 0
            placeholders = ",".join("?" for _ in doc_ids)
            conn.execute(f"UPDATE document_coverage_catalog SET document_id = NULL WHERE document_id IN ({placeholders})", doc_ids)
            conn.execute(f"DELETE FROM evidence_items WHERE document_id IN ({placeholders})", doc_ids)
            conn.execute(f"DELETE FROM document_chunks WHERE document_id IN ({placeholders})", doc_ids)
            cursor = conn.execute(
                f"DELETE FROM documents WHERE id IN ({placeholders})", doc_ids
            )
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def purge_documents_for_asset(self, asset_id: str) -> int:
        """Safely purge all documents, chunks, and evidence items for a given asset."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id FROM documents WHERE asset_id = ?", (asset_id,)).fetchall()
            doc_ids = [r[0] for r in rows]
            if not doc_ids:
                conn.execute(
                    "UPDATE assets SET document_status = 'documents_pending' WHERE id = ?",
                    (asset_id,),
                )
                conn.commit()
                return 0
            placeholders = ",".join("?" for _ in doc_ids)
            conn.execute(f"UPDATE document_coverage_catalog SET document_id = NULL WHERE document_id IN ({placeholders})", doc_ids)
            conn.execute(f"DELETE FROM evidence_items WHERE document_id IN ({placeholders})", doc_ids)
            conn.execute(f"DELETE FROM document_chunks WHERE document_id IN ({placeholders})", doc_ids)
            cursor = conn.execute(f"DELETE FROM documents WHERE id IN ({placeholders})", doc_ids)
            deleted = cursor.rowcount
            conn.execute(
                "UPDATE assets SET document_status = 'documents_pending' WHERE id = ?",
                (asset_id,),
            )
            conn.commit()
            return deleted
