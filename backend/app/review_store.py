"""
In-memory review queue store.
In production, replace with a database backend.
"""
from typing import Dict, Optional
from .models import ReviewQueueItem, ReviewDecision


_store: Dict[str, ReviewQueueItem] = {}


def add_to_queue(item: ReviewQueueItem) -> None:
    _store[item.case_id] = item


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
        _store[decision.case_id] = item
        return item

    item.decision = decision.decision
    item.curator_id = decision.curator_id
    item.curator_notes = decision.notes
    item.decision_timestamp = decision.timestamp
    item.audit_trail.append(
        f"Human review decision: {decision.decision} by {decision.curator_id or 'unknown'} at {decision.timestamp}"
    )
    if decision.override_canonical:
        item.canonical = decision.override_canonical
        item.audit_trail.append("Canonical concept edited by reviewer")
    _store[decision.case_id] = item
    return item


def clear_queue() -> None:
    _store.clear()
