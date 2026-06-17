"""
File-backed MVP review queue store.
In production, replace with a database backend.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from .models import ReviewQueueItem, ReviewDecision


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
    _store[decision.case_id] = item
    _save_store()
    return item


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
