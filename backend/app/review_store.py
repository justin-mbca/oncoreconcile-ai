"""
File-backed MVP review queue store.
In production, replace with a database backend.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from .models import ReviewQueueItem, ReviewDecision, ReviewDecisionRecord


ROOT = Path(__file__).resolve().parents[2]
REVIEW_QUEUE_PATH = ROOT / "data" / "review_queue.json"
_store: Dict[str, ReviewQueueItem] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_store() -> None:
    if not REVIEW_QUEUE_PATH.exists():
        return
    try:
        payload = json.loads(REVIEW_QUEUE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    items = payload.get("items", payload if isinstance(payload, list) else [])
    for raw_item in items:
        try:
            item = ReviewQueueItem.model_validate(raw_item)
        except Exception:
            continue
        _store[item.case_id] = item


def _save_store() -> None:
    REVIEW_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "items": [
            item.model_dump(mode="json")
            for item in sorted(_store.values(), key=lambda i: i.case_id)
        ]
    }
    REVIEW_QUEUE_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def add_to_queue(item: ReviewQueueItem) -> None:
    existing = _store.get(item.case_id)
    if existing:
        item.created_at = existing.created_at
        item.decision = existing.decision
        item.curator_id = existing.curator_id
        item.curator_notes = existing.curator_notes
        item.decision_timestamp = existing.decision_timestamp
        item.review_history = existing.review_history
        item.adjudication_status = existing.adjudication_status
        item.adjudicated_by = existing.adjudicated_by
        item.adjudication_timestamp = existing.adjudication_timestamp
        if existing.decision in {"edit", "override", "approve"}:
            item.canonical = existing.canonical
    item.updated_at = _now()
    _store[item.case_id] = item
    _save_store()


def get_queue(status: Optional[str] = None) -> list[ReviewQueueItem]:
    items = list(_store.values())
    if status == "pending":
        items = [i for i in items if i.decision is None]
    elif status == "reviewed":
        items = [i for i in items if i.decision is not None]
    return items


def get_item(case_id: str) -> Optional[ReviewQueueItem]:
    return _store.get(case_id)


def apply_decision(decision: ReviewDecision) -> Optional[ReviewQueueItem]:
    item = _store.get(decision.case_id)
    if not item:
        return None

    if decision.decision == "reopen":
        item.audit_trail.append(
            f"Human review reopened by {decision.curator_id or 'unknown'} at {decision.timestamp}"
        )
        item.decision = None
        item.curator_id = decision.curator_id
        item.curator_notes = decision.notes
        item.decision_timestamp = decision.timestamp
        item.updated_at = _now()
        _store[decision.case_id] = item
        _save_store()
        return item

    decision_record = ReviewDecisionRecord(
        decision=decision.decision,
        curator_id=decision.curator_id,
        canonical=decision.override_canonical or item.canonical,
        notes=decision.notes,
        timestamp=decision.timestamp,
    )
    item.review_history.append(decision_record)
    item.decision = decision.decision
    item.curator_id = decision.curator_id
    item.curator_notes = decision.notes
    item.decision_timestamp = decision.timestamp
    item.updated_at = _now()
    item.audit_trail.append(
        f"Human review decision: {decision.decision} by {decision.curator_id or 'unknown'} at {decision.timestamp}"
    )
    if decision.override_canonical:
        item.canonical = decision.override_canonical
        item.audit_trail.append("Canonical concept edited by reviewer")
    _update_adjudication_status(item)
    _store[decision.case_id] = item
    _save_store()
    return item


def _decision_signature(record: ReviewDecisionRecord) -> tuple:
    canonical = record.canonical
    canonical_signature = (
        canonical.cancer_type if canonical else None,
        canonical.gene if canonical else None,
        canonical.variant if canonical else None,
    )
    decision = "edit" if record.decision in {"edit", "override"} else record.decision
    return decision, canonical_signature


def _latest_reviewer_records(item: ReviewQueueItem) -> list[ReviewDecisionRecord]:
    latest = {}
    for record in item.review_history:
        if record.role != "reviewer" or not record.curator_id:
            continue
        latest[record.curator_id] = record
    return list(latest.values())


def _update_adjudication_status(item: ReviewQueueItem) -> None:
    records = _latest_reviewer_records(item)
    if len(records) < 2:
        item.adjudication_status = "NOT_REQUIRED"
        return
    signatures = {_decision_signature(record) for record in records}
    item.adjudication_status = "REQUIRED" if len(signatures) > 1 else "NOT_REQUIRED"


def apply_adjudication(decision: ReviewDecision) -> Optional[ReviewQueueItem]:
    item = _store.get(decision.case_id)
    if not item:
        return None
    if item.adjudication_status != "REQUIRED":
        return item

    item.review_history.append(ReviewDecisionRecord(
        decision=decision.decision,
        curator_id=decision.curator_id,
        role="adjudicator",
        canonical=decision.override_canonical or item.canonical,
        notes=decision.notes,
        timestamp=decision.timestamp,
    ))
    item.decision = decision.decision
    item.curator_id = decision.curator_id
    item.curator_notes = decision.notes
    item.decision_timestamp = decision.timestamp
    if decision.override_canonical:
        item.canonical = decision.override_canonical
    item.adjudication_status = "RESOLVED"
    item.adjudicated_by = decision.curator_id
    item.adjudication_timestamp = decision.timestamp
    item.updated_at = _now()
    item.audit_trail.append(
        f"Adjudication decision: {decision.decision} by {decision.curator_id or 'unknown'} at {decision.timestamp}"
    )
    _store[decision.case_id] = item
    _save_store()
    return item


def agreement_metrics() -> dict:
    comparable = []
    reviewer_decisions = {}
    for item in _store.values():
        records = _latest_reviewer_records(item)
        if len(records) < 2:
            continue
        records.sort(key=lambda record: record.curator_id or "")
        first, second = records[:2]
        first_label = _decision_signature(first)[0]
        second_label = _decision_signature(second)[0]
        comparable.append((first_label, second_label))
        reviewer_decisions.setdefault(first.curator_id, 0)
        reviewer_decisions.setdefault(second.curator_id, 0)
        reviewer_decisions[first.curator_id] += 1
        reviewer_decisions[second.curator_id] += 1

    total = len(comparable)
    agreements = sum(first == second for first, second in comparable)
    observed = agreements / total if total else None
    labels = {label for pair in comparable for label in pair}
    expected = 0.0
    if total:
        for label in labels:
            first_rate = sum(first == label for first, _ in comparable) / total
            second_rate = sum(second == label for _, second in comparable) / total
            expected += first_rate * second_rate
    kappa = (
        (observed - expected) / (1 - expected)
        if observed is not None and expected < 1
        else None
    )
    return {
        "cases_with_multiple_reviewers": total,
        "agreements": agreements,
        "disagreements": total - agreements,
        "percent_agreement": round(observed, 4) if observed is not None else None,
        "cohens_kappa": round(kappa, 4) if kappa is not None else None,
        "adjudication_required": sum(
            item.adjudication_status == "REQUIRED" for item in _store.values()
        ),
        "adjudication_resolved": sum(
            item.adjudication_status == "RESOLVED" for item in _store.values()
        ),
        "reviewer_case_counts": reviewer_decisions,
        "note": "Agreement metrics require at least two distinct curator decisions per case.",
    }


def clear_queue() -> None:
    _store.clear()
    _save_store()


def promote_candidate_to_catalog(review_id: str) -> dict:
    """Roadmap stub: catalog promotion must remain an explicit governed action."""
    return {
        "status": "not_implemented",
        "review_id": review_id,
        "message": (
            "Promote to Catalog is disabled in the MVP. "
            "Approved reviews do not modify gene_variant_catalog.csv."
        ),
    }


_load_store()
