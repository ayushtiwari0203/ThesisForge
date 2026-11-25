"""State machine definitions for ThesisForge AI (SRS Section 5.3)."""

from __future__ import annotations
from enum import Enum
from typing import Set


class WorkflowState(str, Enum):
    CREATED = "CREATED"
    DOCUMENTS_READY = "DOCUMENTS_READY"
    EVIDENCE_READY = "EVIDENCE_READY"
    RESEARCH_COMPLETE = "RESEARCH_COMPLETE"
    BULL_BEAR_COMPLETE = "BULL_BEAR_COMPLETE"
    REBUTTAL_COMPLETE = "REBUTTAL_COMPLETE"
    RISK_REVIEW_COMPLETE = "RISK_REVIEW_COMPLETE"
    JUDGE_COMPLETE = "JUDGE_COMPLETE"
    VALIDATION_COMPLETE = "VALIDATION_COMPLETE"
    COMPLETED = "COMPLETED"

    # Failure states from SRS Section 5.3
    INGESTION_FAILED = "INGESTION_FAILED"
    RETRIEVAL_FAILED = "RETRIEVAL_FAILED"
    AGENT_FAILED = "AGENT_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CANCELLED = "CANCELLED"


VALID_TRANSITIONS = {
    WorkflowState.CREATED: {WorkflowState.DOCUMENTS_READY, WorkflowState.INGESTION_FAILED, WorkflowState.CANCELLED},
    WorkflowState.DOCUMENTS_READY: {WorkflowState.EVIDENCE_READY, WorkflowState.RETRIEVAL_FAILED, WorkflowState.INSUFFICIENT_EVIDENCE},
    WorkflowState.EVIDENCE_READY: {WorkflowState.RESEARCH_COMPLETE, WorkflowState.AGENT_FAILED},
    WorkflowState.RESEARCH_COMPLETE: {WorkflowState.BULL_BEAR_COMPLETE, WorkflowState.AGENT_FAILED, WorkflowState.INSUFFICIENT_EVIDENCE},
    WorkflowState.BULL_BEAR_COMPLETE: {WorkflowState.REBUTTAL_COMPLETE, WorkflowState.AGENT_FAILED},
    WorkflowState.REBUTTAL_COMPLETE: {WorkflowState.RISK_REVIEW_COMPLETE, WorkflowState.AGENT_FAILED},
    WorkflowState.RISK_REVIEW_COMPLETE: {WorkflowState.JUDGE_COMPLETE, WorkflowState.AGENT_FAILED},
    WorkflowState.JUDGE_COMPLETE: {WorkflowState.VALIDATION_COMPLETE, WorkflowState.VALIDATION_FAILED},
    WorkflowState.VALIDATION_COMPLETE: {WorkflowState.COMPLETED},
}


def can_transition(current: WorkflowState, target: WorkflowState) -> bool:
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed
