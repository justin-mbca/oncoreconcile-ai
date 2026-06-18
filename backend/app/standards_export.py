from .provenance_export import build_prov_o_inspired_record


def build_vrs_ready_stub(result: dict) -> dict:
    canonical = result.get("canonical") or {}
    return {
        "type": "VRS-ready-stub",
        "gene": canonical.get("gene"),
        "variant": canonical.get("variant"),
        "representation_status": "requires_mapping_to_sequence_location",
        "review_status": result.get("review_status"),
        "note": "This is not an official GA4GH VRS object.",
    }


def build_cat_vrs_ready_stub(result: dict) -> dict:
    canonical = result.get("canonical") or {}
    alternatives = result.get("alternatives") or []
    members = [
        item.get("name")
        for item in alternatives
        if isinstance(item, dict) and item.get("name")
    ]
    category = canonical.get("variant")
    for item in alternatives:
        if isinstance(item, dict) and item.get("category"):
            category = item["category"]
            break

    ambiguity_preserved = bool(members) and result.get("review_status") == "REVIEW_REQUIRED"
    return {
        "type": "Cat-VRS-ready-stub",
        "category": category,
        "members": members,
        "ambiguity_preserved": ambiguity_preserved,
        "review_required": result.get("review_status") == "REVIEW_REQUIRED",
        "note": "This is not an official Cat-VRS object.",
    }


def build_va_spec_ready_stub(result: dict) -> dict:
    return {
        "type": "VA-Spec-ready-stub",
        "statement": "Input was reconciled to a candidate canonical concept.",
        "evidence": result.get("evidence") or [],
        "provenance": build_prov_o_inspired_record(result),
        "review_status": result.get("review_status"),
        "note": "This is not an official VA-Spec document.",
    }
