import json
from pathlib import Path
from .models import ReconcileRequest, ReconcileResponse, CanonicalConcept, EvidenceItem
from .explain import build_explanation

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

def load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

CANCER_ALIASES = load_json("cancer_aliases.json")
GENE_ALIASES = load_json("gene_aliases.json")
VARIANT_ALIASES = load_json("variant_aliases.json")


def normalize_cancer_type(value: str | None):
    if not value:
        return None, None
    canonical = CANCER_ALIASES.get(value) or CANCER_ALIASES.get(value.strip())
    return canonical, "Cancer type alias match" if canonical else None


def normalize_gene(value: str):
    canonical = GENE_ALIASES.get(value) or GENE_ALIASES.get(value.strip())
    return canonical, "Gene alias match" if canonical else None


def normalize_variant(value: str, canonical_gene: str | None):
    raw = value.strip()
    mapped = VARIANT_ALIASES.get(raw)
    if not mapped:
        return None, None

    if "{gene}" in mapped:
        if canonical_gene:
            mapped = mapped.replace("{gene}", canonical_gene)
        else:
            return None, None

    return mapped, "Variant synonym match"


def get_confidence(cancer_ok: bool, gene_ok: bool, variant_ok: bool):
    if gene_ok and variant_ok:
        return "HIGH"
    if gene_ok or variant_ok or cancer_ok:
        return "MEDIUM"
    return "LOW"


def get_review_status(confidence: str, canonical_gene: str | None, canonical_variant: str | None):
    if confidence == "HIGH":
        return "AUTO_RECONCILE"
    if canonical_gene or canonical_variant:
        return "REVIEW_REQUIRED"
    return "CANNOT_RECONCILE"


def reconcile_record(req: ReconcileRequest) -> ReconcileResponse:
    audit_trail = ["Input received"]

    audit_trail.append("Cancer alias lookup attempted")
    canonical_cancer, cancer_reason = normalize_cancer_type(req.cancer_type)
    audit_trail.append("Gene alias lookup attempted")
    canonical_gene, gene_reason = normalize_gene(req.gene)
    audit_trail.append("Variant synonym lookup attempted")
    canonical_variant, variant_reason = normalize_variant(req.variant, canonical_gene)

    evidence = []
    if cancer_reason:
        audit_trail.append("Cancer type alias match found")
        evidence.append(EvidenceItem(
            source="Seed Knowledge Base",
            type="cancer_type_alias",
            description=f"{req.cancer_type} was mapped to {canonical_cancer}.",
            evidence_type="alias_dictionary_match",
            confidence_weight="MEDIUM",
            retrieval_mode="local_seed_alias"
        ))
    if gene_reason:
        audit_trail.append("Gene alias match found")
        evidence.append(EvidenceItem(
            source="Seed Knowledge Base / HGNC-inspired",
            type="gene_alias",
            description=f"{req.gene} was mapped to {canonical_gene}.",
            evidence_type="alias_dictionary_match",
            confidence_weight="HIGH",
            retrieval_mode="local_seed_alias"
        ))
    if variant_reason:
        audit_trail.append("Variant synonym match found")
        evidence.append(EvidenceItem(
            source="Seed Knowledge Base",
            type="variant_synonym",
            description=f"{req.variant} was mapped to {canonical_variant}.",
            evidence_type="alias_dictionary_match",
            confidence_weight="HIGH",
            retrieval_mode="local_seed_alias"
        ))
    if not evidence:
        audit_trail.append("No alias/synonym evidence found")

    confidence = get_confidence(bool(canonical_cancer), bool(canonical_gene), bool(canonical_variant))
    review_status = get_review_status(confidence, canonical_gene, canonical_variant)
    audit_trail.append(f"Confidence computed: {confidence}")
    audit_trail.append(f"Review status decided: {review_status}")

    evidence_dicts = [e.model_dump() for e in evidence]
    explanation = build_explanation(evidence_dicts, confidence, review_status)
    audit_trail.append("Explanation generated")

    notes = []
    if not canonical_gene:
        notes.append("Gene could not be reconciled.")
        audit_trail.append("Gene unresolved")
    if not canonical_variant:
        notes.append("Variant could not be reconciled.")
        audit_trail.append("Variant unresolved")

    return ReconcileResponse(
        case_id=req.case_id,
        input=req.model_dump(),
        canonical=CanonicalConcept(
            cancer_type=canonical_cancer,
            gene=canonical_gene,
            variant=canonical_variant,
        ),
        evidence=evidence,
        explanation=explanation,
        confidence=confidence,
        review_status=review_status,
        notes=notes,
        audit_trail=audit_trail,
    )
