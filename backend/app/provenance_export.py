from datetime import datetime, timezone


def build_prov_o_inspired_record(result: dict) -> dict:
    evidence = result.get("evidence") or []
    evidence_sources = []
    seen = set()
    for item in evidence:
        source = item.get("source")
        if not source or source in seen:
            continue
        seen.add(source)
        evidence_sources.append({
            "source": source,
            "evidence_type": item.get("evidence_type"),
            "retrieval_mode": item.get("retrieval_mode"),
            "external_id": item.get("external_id"),
            "timestamp": item.get("timestamp"),
        })

    return {
        "type": "PROV-O-inspired",
        "entity": {
            "input": result.get("input") or {},
            "canonical": result.get("canonical") or {},
        },
        "activity": {
            "name": "oncology_entity_reconciliation",
            "steps": [
                "text_normalization",
                "disease_reconciliation",
                "gene_reconciliation",
                "variant_reconciliation",
                "evidence_discovery",
                "human_review_routing",
            ],
        },
        "agents": [{
            "type": "software",
            "name": "OncoReconcile AI",
            "role": "reconciliation_engine",
        }],
        "evidence_sources": evidence_sources,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_status": result.get("review_status"),
        "note": "This is a PROV-O-inspired prototype record, not an official PROV-O document.",
    }
