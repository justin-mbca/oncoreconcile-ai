from datetime import datetime, timezone

import httpx


MYVARIANT_QUERY_URL = "https://myvariant.info/v1/query"
NCBI_EUTILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CIVIC_GRAPHQL_URL = "https://civicdb.org/api/graphql"
CLINGEN_ALLELE_URL = "https://reg.genome.network/allele"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_evidence(source: str, retrieval_mode: str, exc: Exception) -> dict:
    return {
        "source": source,
        "type": "external_lookup_error",
        "description": f"{source} lookup failed: {exc}",
        "evidence_type": "external_lookup_error",
        "confidence_weight": "LOW",
        "retrieval_mode": f"{retrieval_mode}_error",
        "timestamp": _timestamp(),
    }


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
        return [_error_evidence("MyVariant.info", "live_myvariant_api", exc)]

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


def lookup_clinvar(gene: str | None, variant: str | None) -> list[dict]:
    if not gene or not variant:
        return []

    query = f"{gene.strip()} {variant.strip()}".strip()
    try:
        search_response = httpx.get(
            f"{NCBI_EUTILS_URL}/esearch.fcgi",
            params={"db": "clinvar", "term": query, "retmode": "json", "retmax": 5},
            timeout=5,
        )
        search_response.raise_for_status()
        identifiers = search_response.json().get("esearchresult", {}).get("idlist", [])[:5]
        if not identifiers:
            return []

        summary_response = httpx.get(
            f"{NCBI_EUTILS_URL}/esummary.fcgi",
            params={"db": "clinvar", "id": ",".join(identifiers), "retmode": "json"},
            timeout=5,
        )
        summary_response.raise_for_status()
        results = summary_response.json().get("result", {})
    except Exception as exc:
        return [_error_evidence("ClinVar", "live_clinvar_api", exc)]

    evidence = []
    for identifier in identifiers:
        summary = results.get(str(identifier), {})
        title = (
            summary.get("title")
            or summary.get("variation_name")
            or summary.get("accession")
            or f"ClinVar record {identifier}"
        )
        evidence.append({
            "source": "ClinVar",
            "type": "external_variant_lookup",
            "description": (
                f"ClinVar returned {title} for {query}. "
                "This live evidence is advisory and requires human review."
            ),
            "evidence_type": "external_variant_lookup",
            "confidence_weight": "MEDIUM",
            "retrieval_mode": "live_clinvar_api",
            "external_id": str(identifier),
            "url": f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{identifier}/",
            "timestamp": _timestamp(),
        })
    return evidence


def _civic_records(payload: dict) -> list[dict]:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    search_records = data.get("search", [])
    if isinstance(search_records, list):
        return [
            record
            for record in search_records
            if record.get("resultType") in {None, "VARIANT"}
        ]
    records = data.get("variantsTypeahead", [])
    if isinstance(records, list):
        return records
    search_results = data.get("searchVariants", {})
    if isinstance(search_results, dict):
        for key in ("records", "results", "variants", "nodes"):
            if isinstance(search_results.get(key), list):
                return search_results[key]
    return []


def lookup_civic(gene: str | None, variant: str | None) -> list[dict]:
    if not gene or not variant:
        return []

    query = f"{gene.strip()} {variant.strip()}".strip()
    graphql_query = """
        query VariantSearch($query: String!) {
          search(query: $query, types: [VARIANT]) {
            id
            name
            resultType
          }
        }
    """
    try:
        response = httpx.post(
            CIVIC_GRAPHQL_URL,
            json={"query": graphql_query, "variables": {"query": query}},
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError(payload["errors"][0].get("message", "CIViC GraphQL error"))
        records = _civic_records(payload)[:5]
    except Exception as exc:
        return [_error_evidence("CIViC", "live_civic_api", exc)]

    evidence = []
    for record in records:
        external_id = record.get("id") or record.get("variantId")
        name = record.get("name") or record.get("variantName") or query
        evidence.append({
            "source": "CIViC",
            "type": "external_oncology_evidence",
            "description": (
                f"CIViC returned oncology variant candidate {name} for {query}. "
                "This live evidence is advisory and requires human review."
            ),
            "evidence_type": "external_oncology_evidence",
            "confidence_weight": "MEDIUM",
            "retrieval_mode": "live_civic_api",
            "external_id": str(external_id) if external_id is not None else None,
            "url": f"https://civicdb.org/variants/{external_id}" if external_id is not None else None,
            "timestamp": _timestamp(),
        })
    return evidence


def lookup_clingen_allele_registry(gene: str | None, variant: str | None) -> list[dict]:
    if not gene or not variant:
        return []

    query = f"{gene.strip()}:{variant.strip()}"
    try:
        response = httpx.get(
            CLINGEN_ALLELE_URL,
            params={"hgvs": query},
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return [_error_evidence("ClinGen Allele Registry", "live_clingen_allele_registry_api", exc)]

    records = payload if isinstance(payload, list) else [payload]
    evidence = []
    for record in records[:5]:
        if not isinstance(record, dict):
            continue
        registry_id = record.get("@id") or record.get("id") or record.get("alleleId")
        if isinstance(registry_id, str) and "/" in registry_id:
            external_id = registry_id.rstrip("/").rsplit("/", 1)[-1]
            url = registry_id
        else:
            external_id = str(registry_id) if registry_id is not None else None
            url = f"{CLINGEN_ALLELE_URL}/{external_id}" if external_id else None
        if not external_id:
            continue
        title = record.get("communityStandardTitle") or record.get("hgvs") or query
        evidence.append({
            "source": "ClinGen Allele Registry",
            "type": "external_allele_registry_lookup",
            "description": (
                f"ClinGen Allele Registry returned candidate allele {title}. "
                "This experimental lookup is advisory and requires human review."
            ),
            "evidence_type": "external_allele_registry_lookup",
            "confidence_weight": "MEDIUM",
            "retrieval_mode": "live_clingen_allele_registry_api",
            "external_id": external_id,
            "url": url,
            "timestamp": _timestamp(),
        })
    return evidence


def lookup_all_external_sources(gene: str | None, variant: str | None) -> list[dict]:
    evidence = []
    for lookup in (
        lookup_myvariant,
        lookup_clinvar,
        lookup_civic,
        lookup_clingen_allele_registry,
    ):
        evidence.extend(lookup(gene, variant))
    return evidence
