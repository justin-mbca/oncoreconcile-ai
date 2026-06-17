from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class ReconcileRequest(BaseModel):
    case_id: Optional[str] = None
    cancer_type: Optional[str] = None
    gene: str
    variant: str


class EvidenceItem(BaseModel):
    source: str
    type: str
    description: str
    evidence_type: Optional[str] = None
    confidence_weight: Optional[str] = None
    retrieval_mode: Optional[str] = None
    external_id: Optional[str] = None
    url: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    governance_standard: Optional[str] = "VA-Spec-inspired"


class CanonicalConcept(BaseModel):
    cancer_type: Optional[str] = None
    gene: Optional[str] = None
    variant: Optional[str] = None


class ReconcileResponse(BaseModel):
    case_id: Optional[str] = None
    input: dict
    canonical: CanonicalConcept
    evidence: List[EvidenceItem]
    explanation: str
    confidence: str                              # HIGH | MEDIUM | LOW
    confidence_score: float = 0.0               # 0.0–1.0 numeric score
    score_breakdown: dict = Field(default_factory=dict)  # per-signal weights
    review_status: str
    alternatives: List[Any] = Field(default_factory=list)  # other candidates considered
    notes: List[str] = Field(default_factory=list)
    audit_trail: List[str] = Field(default_factory=list)


class BatchRequest(BaseModel):
    records: List[ReconcileRequest]


class BatchResponse(BaseModel):
    results: List[ReconcileResponse]
    summary: dict


# ── Review queue models ───────────────────────────────────────────────────────

class ReviewDecision(BaseModel):
    case_id: str
    decision: str           # "approve" | "reject" | "edit" | "override" | "reopen"
    curator_id: Optional[str] = None
    override_canonical: Optional[CanonicalConcept] = None
    notes: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ReviewQueueItem(BaseModel):
    case_id: str
    input: dict
    canonical: CanonicalConcept
    confidence: str
    confidence_score: float
    score_breakdown: dict
    review_status: str
    explanation: str
    evidence: List[EvidenceItem]
    alternatives: List[Any] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    audit_trail: List[str] = Field(default_factory=list)
    decision: Optional[str] = None        # null until reviewed
    curator_id: Optional[str] = None
    curator_notes: Optional[str] = None
    decision_timestamp: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ReviewQueueResponse(BaseModel):
    items: List[ReviewQueueItem]
    total: int
    pending: int
    reviewed: int
