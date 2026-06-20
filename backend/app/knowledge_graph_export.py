from datetime import datetime, timezone
from urllib.parse import quote


CONTEXT = {
    "onco": "https://example.org/oncoreconcile/",
    "schema": "https://schema.org/",
    "prov": "http://www.w3.org/ns/prov#",
    "type": "@type",
    "label": "schema:name",
    "source": "schema:citation",
    "generatedBy": {"@id": "prov:wasGeneratedBy", "@type": "@id"},
    "derivedFrom": {"@id": "prov:wasDerivedFrom", "@type": "@id"},
    "hasEvidence": {"@id": "onco:hasEvidence", "@type": "@id"},
    "hasCanonicalConcept": {"@id": "onco:hasCanonicalConcept", "@type": "@id"},
    "hasAlternative": {"@id": "onco:hasAlternative", "@type": "@id"},
}


def _node_id(kind: str, value: str) -> str:
    return f"onco:{kind}/{quote(value, safe='')}"


def build_knowledge_graph(result: dict) -> dict:
    case_id = result.get("case_id") or "unassigned"
    reconciliation_id = _node_id("reconciliation", str(case_id))
    input_id = _node_id("input", str(case_id))
    graph = [
        {
            "@id": reconciliation_id,
            "@type": "onco:ReconciliationActivity",
            "label": f"Oncology reconciliation {case_id}",
            "onco:reviewStatus": result.get("review_status"),
            "onco:confidence": result.get("confidence"),
            "onco:confidenceScore": result.get("confidence_score"),
            "prov:generatedAtTime": datetime.now(timezone.utc).isoformat(),
            "derivedFrom": input_id,
            "hasCanonicalConcept": [],
            "hasEvidence": [],
            "hasAlternative": [],
        },
        {
            "@id": input_id,
            "@type": "onco:RawOncologyRecord",
            "label": f"Input record {case_id}",
            "onco:payload": result.get("input") or {},
        },
    ]

    canonical = result.get("canonical") or {}
    for entity_type, value in canonical.items():
        if not value:
            continue
        node_id = _node_id(entity_type, str(value))
        graph[0]["hasCanonicalConcept"].append(node_id)
        graph.append({
            "@id": node_id,
            "@type": f"onco:Canonical{entity_type.title().replace('_', '')}",
            "label": value,
            "generatedBy": reconciliation_id,
        })

    for index, item in enumerate(result.get("evidence") or [], start=1):
        evidence_id = _node_id("evidence", f"{case_id}-{index}")
        graph[0]["hasEvidence"].append(evidence_id)
        graph.append({
            "@id": evidence_id,
            "@type": "onco:EvidenceRecord",
            "label": item.get("description") or item.get("type") or f"Evidence {index}",
            "source": item.get("source"),
            "onco:evidenceType": item.get("evidence_type"),
            "onco:retrievalMode": item.get("retrieval_mode"),
            "onco:externalId": item.get("external_id"),
            "schema:url": item.get("url"),
            "prov:generatedAtTime": item.get("timestamp"),
        })

    for index, item in enumerate(result.get("alternatives") or [], start=1):
        if not isinstance(item, dict):
            continue
        alternative_id = _node_id("alternative", f"{case_id}-{index}")
        graph[0]["hasAlternative"].append(alternative_id)
        graph.append({
            "@id": alternative_id,
            "@type": "onco:CandidateConcept",
            "label": item.get("name") or item.get("id") or f"Alternative {index}",
            "onco:reason": item.get("reason"),
            "onco:requiresReview": item.get("requires_review", True),
        })

    return {
        "@context": CONTEXT,
        "@graph": graph,
        "export_status": "JSON-LD knowledge graph prototype",
        "note": (
            "This graph is an OncoReconcile prototype. It is not an official "
            "Biolink, RDF, GA4GH, FHIR, or OMOP representation."
        ),
    }
