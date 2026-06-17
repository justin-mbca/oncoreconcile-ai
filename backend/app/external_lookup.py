from datetime import datetime, timezone

import httpx


MYVARIANT_QUERY_URL = "https://myvariant.info/v1/query"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hit_description(query: str, hit: dict) -> str:
    hit_id = hit.get("_id") or hit.get("dbsnp", {}).get("rsid") or "unknown external record"
    sources = []
    for source in ("clinvar", "civic", "dbsnp", "snpeff", "vcf"):
        if hit.get(source):
            sources.append(source)
    source_text = ", ".join(sources) if sources else "MyVariant.info"
    return (
        f"External evidence candidate found for {query}: {hit_id}. "
        f"Returned fields include {source_text}. This evidence is advisory and requires human review."
    )


def lookup_myvariant(gene: str | None, variant: str | None) -> list[dict]:
    if not gene or not variant:
        return []

    query = f"{gene.strip()} {variant.strip()}".strip()
    if not query:
        return []

    try:
        response = httpx.get(
            MYVARIANT_QUERY_URL,
            params={
                "q": query,
                "fields": "clinvar,civic,dbsnp,snpeff,vcf",
                "size": 5,
            },
            timeout=5,
        )
        response.raise_for_status()
        hits = response.json().get("hits", [])
    except Exception as exc:
        return [{
            "source": "MyVariant.info",
            "type": "external_lookup_error",
            "description": f"External lookup failed: {exc}",
            "evidence_type": "external_lookup_error",
            "confidence_weight": "LOW",
            "retrieval_mode": "live_myvariant_api_error",
            "timestamp": _timestamp(),
        }]

    evidence = []
    for hit in hits:
        external_id = hit.get("_id") or hit.get("dbsnp", {}).get("rsid")
        evidence.append({
            "source": "MyVariant.info",
            "type": "external_variant_lookup",
            "description": _hit_description(query, hit),
            "evidence_type": "external_lookup",
            "confidence_weight": "LOW",
            "retrieval_mode": "live_myvariant_api",
            "external_id": external_id,
            "url": f"https://myvariant.info/v1/variant/{external_id}" if external_id else None,
            "timestamp": _timestamp(),
        })

    return evidence
