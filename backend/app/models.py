from typing import List, Optional
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
    url: Optional[str] = None


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
    confidence: str
    review_status: str
    notes: List[str] = Field(default_factory=list)
    audit_trail: List[str] = Field(default_factory=list)


class BatchRequest(BaseModel):
    records: List[ReconcileRequest]


class BatchResponse(BaseModel):
    results: List[ReconcileResponse]
    summary: dict
