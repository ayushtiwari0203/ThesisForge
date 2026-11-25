"""Research Agent module for ThesisForge AI (SRS Section 6)."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.llm_adapter import LLMServiceAdapter
from database.models import AgentResult, Claim, EvidenceItem
from database.repository import Repository
from tools.document_tools import get_document_metadata
from tools.evidence_tools import create_evidence_pack
from tools.retrieval_tools import retrieve_chunks, search_documents


class ResearchAgent:
    """Research Agent assembles facts from the provided asset document set.

    Strict rule: Makes no recommendation or stance.
    Invokes real tools: search_documents, retrieve_chunks, get_document_metadata, create_evidence_pack.
    """

    def __init__(self, repo: Repository, adapter: LLMServiceAdapter):
        self.repo = repo
        self.adapter = adapter
        self.agent_name = "ResearchAgent"

    def execute(self, run_id: str, asset_id: str) -> AgentResult:
        tool_calls: List[str] = []

        documents = self.repo.list_documents_for_asset(asset_id)
        doc_metas = []
        for d in documents:
            meta = get_document_metadata(d.id, self.repo)
            doc_metas.append(meta)
        tool_calls.append("get_document_metadata")

        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.get_document_metadata",
            payload={"documents_inspected": len(doc_metas), "document_ids": [d.id for d in documents]},
        )

        if not documents:
            self.repo.append_event(
                run_id=run_id,
                event_type="AGENT_FAILED",
                agent_or_tool=self.agent_name,
                payload={"error": "No documents found for asset"},
            )
            return AgentResult(
                agent_name=self.agent_name,
                run_id=UUID(run_id),
                status="insufficient_evidence",
                summary="No documents available in document pack for this asset.",
                claims=[],
                evidence_ids=[],
                uncertainties=["Document store is empty for requested asset."],
                warnings=["Ingest documents before initiating research run."],
                tool_calls=tool_calls,
            )

        research_queries = [
            "revenue turnover sales growth",
            "ebitda operating profit margin performance",
            "debt borrowing liabilities leverage liquidity",
            "risk factors challenges litigation headwinds",
            "management outlook guidance market opportunity",
        ]

        retrieved_chunks = []
        seen_chunk_ids = set()

        for q in research_queries:
            chunks = search_documents(asset_id=asset_id, query=q, repo=self.repo, top_k=6)
            for ch in chunks:
                if ch.id not in seen_chunk_ids:
                    seen_chunk_ids.add(ch.id)
                    retrieved_chunks.append(ch)

        tool_calls.append("search_documents")
        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.search_documents",
            payload={"queries_executed": len(research_queries), "unique_chunks_retrieved": len(retrieved_chunks)},
        )

        if documents:
            primary_doc_id = documents[0].id
            primary_chunks = retrieve_chunks(
                document_id=primary_doc_id,
                query="annual quarterly audited financial results balance sheet",
                repo=self.repo,
                top_k=4,
            )
            for ch in primary_chunks:
                if ch.id not in seen_chunk_ids:
                    seen_chunk_ids.add(ch.id)
                    retrieved_chunks.append(ch)
            tool_calls.append("retrieve_chunks")
            self.repo.append_event(
                run_id=run_id,
                event_type="TOOL_CALLED",
                agent_or_tool=f"{self.agent_name}.retrieve_chunks",
                payload={"primary_doc_id": primary_doc_id, "primary_chunks_retrieved": len(primary_chunks)},
            )

        evidence_items: List[EvidenceItem] = create_evidence_pack(
            run_id=run_id,
            asset_id=asset_id,
            chunks=retrieved_chunks,
            repo=self.repo,
        )
        tool_calls.append("create_evidence_pack")

        self.repo.append_event(
            run_id=run_id,
            event_type="TOOL_CALLED",
            agent_or_tool=f"{self.agent_name}.create_evidence_pack",
            payload={"evidence_items_created": len(evidence_items), "evidence_codes": [e.evidence_code for e in evidence_items]},
        )

        claims: List[Claim] = []
        for idx, ev in enumerate(evidence_items[:8]):
            claims.append(
                Claim(
                    claim_id=f"RES-{idx+1:02d}",
                    text=ev.passage_text,
                    claim_type="fact",
                    evidence_ids=[ev.evidence_code],
                )
            )

        evidence_ids = [e.evidence_code for e in evidence_items]
        summary = (
            f"Research Agent synthesized {len(evidence_items)} verified evidence items across "
            f"{len(documents)} official filing documents without adopting an investment stance."
        )

        result = AgentResult(
            agent_name=self.agent_name,
            run_id=UUID(run_id),
            status="completed",
            summary=summary,
            claims=claims,
            evidence_ids=evidence_ids,
            uncertainties=[],
            warnings=[],
            tool_calls=tool_calls,
        )

        self.repo.save_agent_output(run_id, self.agent_name, "completed", result.model_dump(mode="json"))
        self.repo.append_event(
            run_id=run_id,
            event_type="AGENT_COMPLETED",
            agent_or_tool=self.agent_name,
            payload={"status": "completed", "claims_count": len(claims), "evidence_count": len(evidence_ids)},
        )

        return result
