"""
Explainability module — deterministic explanation builder.

Owner: Michael
Branch: michael/explain-layer  (branch off vanguard_justin)
Due: June 6, 2026

Reference contract:
  build_explanation(evidence, confidence, review_status) -> str

Rules:
  - HIGH + AUTO_RECONCILE  → clear success sentence with source
  - MEDIUM + REVIEW_REQUIRED → partial match sentence with recommendation
  - LOW + CANNOT_RECONCILE → failure sentence with audit trail note
  - Never returns empty string
  - Never calls external APIs or LLMs
  - Must not raise exceptions under any input

Integration point (Nikola wires this in reconcile.py):
  from .explain import build_explanation
  explanation = build_explanation(evidence, confidence, review_status)
"""

from typing import List


def build_explanation(
    evidence: List[dict],
    confidence: str,
    review_status: str,
) -> str:
    """
    Return a deterministic human-readable explanation for a reconciliation outcome.

    Args:
        evidence:      List of EvidenceItem dicts (keys: source, type, description)
        confidence:    "HIGH" | "MEDIUM" | "LOW"
        review_status: "AUTO_RECONCILE" | "REVIEW_REQUIRED" | "CANNOT_RECONCILE"

    Returns:
        Non-empty explanation string.

    TODO (Michael):
        Replace placeholder logic below with real rules per confidence/review state.
        Keep logic deterministic — no randomness, no external calls.
    """

    # --- HIGH / AUTO_RECONCILE ---
    if confidence == "HIGH" and review_status == "AUTO_RECONCILE":
        sources = [e.get("source", "knowledge base") for e in evidence if e]
        source_note = f" (sources: {', '.join(set(sources))})" if sources else ""
        return (
            "All entities were confidently reconciled to canonical oncology concepts"
            f"{source_note}. No human review is required."
        )

    # --- CANNOT_RECONCILE ---
    if review_status == "CANNOT_RECONCILE":
        return (
            "The gene cannot be identified using the current knowledge base, "
            "so the system safely returns CANNOT_RECONCILE."
        )

    # --- MEDIUM / REVIEW_REQUIRED ---
    if confidence == "MEDIUM" or review_status == "REVIEW_REQUIRED":
        review_required = [
            e.get("description", "")
            for e in evidence
            if e and e.get("evidence_type") == "requires_human_review" and e.get("description")
        ]
        if review_required:
            return " ".join(review_required)

        matched = [e.get("description", "") for e in evidence if e]
        match_note = f" Partial matches found: {'; '.join(matched)}." if matched else ""
        return (
            "One or more entities could not be fully reconciled with high confidence."
            f"{match_note} Human review is recommended before use."
        )

    # --- LOW fallback ---
    if confidence == "LOW":
        return (
            "No reliable canonical match was found for one or more entities. "
            "This record has been flagged for manual review. "
            "Original input values are preserved in the audit trail."
        )

    # --- Fallback (should not be reached in normal operation) ---
    return (
        "Reconciliation completed. Review the confidence score and "
        "evidence before use in downstream workflows."
    )
