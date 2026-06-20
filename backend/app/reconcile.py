import json
import csv
import re
import requests
from difflib import SequenceMatcher
from pathlib import Path
from .models import ReconcileRequest, ReconcileResponse, CanonicalConcept, EvidenceItem

try:
    from rapidfuzz import fuzz, process as rfprocess
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

from .explain import build_explanation
from .external_lookup import lookup_all_external_sources
from . import llm

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_disease_aliases() -> dict:
    aliases = load_json("cancer_aliases.json")
    aliases.update(load_json("disease_aliases.json"))
    return aliases


def load_variant_catalog() -> list[dict]:
    path = DATA_DIR / "gene_variant_catalog.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("gene") and row.get("variant")]


def load_csv_rows(relative_path: str) -> list[dict]:
    path = ROOT / relative_path
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def index_variant_catalog(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    index = {}
    for row in rows:
        aliases = [row["variant"]]
        aliases.extend(
            alias.strip()
            for alias in row.get("variant_aliases", "").split(";")
            if alias.strip()
        )
        for alias in aliases:
            key = (row["gene"].strip(), alias.strip())
            index.setdefault(key, []).append(row)
            index.setdefault((key[0], key[1].lower()), []).append(row)
    return index


def evidence_key(gene: str | None, variant: str | None) -> tuple[str, str]:
    return ((gene or "").strip().lower(), (variant or "").strip().lower())


def index_external_evidence(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    index = {}
    for row in rows:
        key = evidence_key(row.get("gene"), row.get("variant"))
        if key != ("", ""):
            index.setdefault(key, []).append(row)
    return index


def index_disease_gene_catalog(rows: list[dict]) -> set[tuple[str, str]]:
    pairs = set()
    for row in rows:
        disease = (row.get("disease") or "").strip()
        gene = (row.get("gene") or "").strip()
        if disease and gene:
            pairs.add((disease.lower(), gene.upper()))
    return pairs


_EXTERNAL_GENE_CACHE: dict[str, dict | None] = {}
_EXTERNAL_VARIANT_CACHE: dict[tuple[str, str], list[dict]] = {}


def _norm_token(value: str | None) -> str:
    return (value or "").strip()


def looks_like_protein_variant(value: str | None) -> bool:
    raw = _norm_token(value).upper()
    return bool(re.fullmatch(r"[A-Z][0-9]{1,5}[A-Z]", raw))


def local_gene_catalog_candidate_lookup(
    value: str | None,
    canonical_cancer: str | None,
) -> dict | None:
    raw = _norm_token(value).upper()
    if not raw:
        return None

    catalog_rows = [
        row
        for row in VARIANT_CATALOG
        if row.get("gene", "").strip().upper() == raw
        and row.get("gene") not in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}
    ]
    if not catalog_rows:
        return None

    in_disease_catalog = (
        bool(canonical_cancer)
        and (canonical_cancer.lower(), raw) in DISEASE_GENE_CATALOG
    )
    in_variant_catalog_scope = any(
        row.get("disease_scope") == canonical_cancer for row in catalog_rows
    )
    locally_supported = in_disease_catalog or in_variant_catalog_scope
    reason = (
        f"{raw} is listed for {canonical_cancer} in the local oncology catalog."
        if locally_supported
        else (
            f"{raw} is known in the local gene/variant catalog, but this disease "
            "context is not established in the local disease-gene catalog."
        )
    )
    return {
        "id": f"local:gene-catalog:{raw}",
        "symbol": raw,
        "name": raw,
        "source": "Local Disease/Gene + Variant Catalog",
        "reason": reason,
        "requires_review": not locally_supported,
        "match_method": "catalog" if locally_supported else "external_candidate",
        "similarity": 1.0 if locally_supported else 0.85,
        "url": None,
    }


def external_gene_candidate_lookup(value: str | None) -> dict | None:
    raw = _norm_token(value)
    if not raw:
        return None

    cache_key = raw.upper()
    if cache_key in _EXTERNAL_GENE_CACHE:
        return _EXTERNAL_GENE_CACHE[cache_key]
    try:
        response = requests.get(
            "https://mygene.info/v3/query",
            params={
                "q": f"symbol:{raw} OR alias:{raw}",
                "species": "human",
                "fields": "symbol,name,entrezgene,HGNC,alias",
                "size": 5,
            },
            timeout=5,
        )
        response.raise_for_status()
        for hit in response.json().get("hits", []):
            symbol = hit.get("symbol")
            aliases = hit.get("alias") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            if symbol and (
                symbol.upper() == raw.upper()
                or raw.upper() in {str(alias).upper() for alias in aliases}
            ):
                candidate = {
                    "id": f"external:mygene:{symbol}",
                    "symbol": symbol,
                    "name": hit.get("name") or symbol,
                    "source": "MyGene.info API",
                    "reason": f"MyGene.info returned human gene symbol {symbol} for input {raw}.",
                    "requires_review": True,
                    "match_method": "external_candidate",
                    "similarity": 0.85,
                    "url": (
                        f"https://mygene.info/v3/gene/{hit.get('entrezgene')}"
                        if hit.get("entrezgene")
                        else None
                    ),
                }
                _EXTERNAL_GENE_CACHE[cache_key] = candidate
                return candidate
    except Exception:
        pass

    _EXTERNAL_GENE_CACHE[cache_key] = None
    return None


def _extract_civic_records(payload) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    for key in ("records", "results", "variants"):
        if isinstance(payload.get(key), list):
            return payload[key]
    if isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def external_variant_candidate_lookup(
    gene: str | None,
    variant: str | None,
) -> list[dict]:
    gene = _norm_token(gene).upper()
    variant = _norm_token(variant)
    if not gene or not variant:
        return []

    cache_key = (gene, variant.upper())
    if cache_key in _EXTERNAL_VARIANT_CACHE:
        return _EXTERNAL_VARIANT_CACHE[cache_key]

    candidates = []
    query = f"{gene} {variant}"
    for row in CIVIC_CANDIDATES:
        if row.get("query_gene", "").strip().upper() != gene:
            continue
        terms = " ".join([
            row.get("molecular_profile", ""),
            row.get("variant_name", ""),
            row.get("variant_aliases", ""),
        ]).upper()
        if variant.upper() not in terms:
            continue
        variant_link = row.get("variant_link") or ""
        candidates.append({
            "id": f"external:civic-local:{row.get('variant_id') or row.get('evidence_item_id') or variant}",
            "name": f"{gene} {variant.upper()}",
            "source": "Local CIViC candidate CSV",
            "reason": f"Local CIViC candidate row contains {query}.",
            "requires_review": True,
            "url": (
                f"https://civicdb.org{variant_link}"
                if variant_link.startswith("/")
                else None
            ),
        })
        if len(candidates) >= 3:
            break

    if not candidates:
        try:
            response = requests.get(
                "https://civicdb.org/api/variants",
                params={"query": query},
                timeout=5,
            )
            if response.ok:
                for item in _extract_civic_records(response.json())[:3]:
                    name = item.get("name") or item.get("variant_name") or query
                    candidates.append({
                        "id": f"external:civic-api:{item.get('id') or name}",
                        "name": f"{gene} {variant.upper()}",
                        "source": "CIViC API candidate",
                        "reason": f"CIViC API returned a possible record for {query}: {name}.",
                        "requires_review": True,
                        "url": (
                            f"https://civicdb.org/variants/{item.get('id')}"
                            if item.get("id")
                            else None
                        ),
                    })
        except Exception:
            pass

    if not candidates and looks_like_protein_variant(variant):
        candidates.append({
            "id": f"external:syntax-candidate:{gene}:{variant.upper()}",
            "name": f"{gene} {variant.upper()}",
            "source": "External fallback candidate",
            "reason": (
                f"{variant.upper()} matches common protein hotspot notation and {gene} "
                "is a recognized gene symbol. This candidate requires curator review."
            ),
            "requires_review": True,
            "url": None,
        })

    _EXTERNAL_VARIANT_CACHE[cache_key] = candidates
    return candidates

CANCER_ALIASES = load_disease_aliases()
GENE_ALIASES = load_json("gene_aliases.json")
GENE_REVIEW_REQUIRED = load_json("gene_review_required.json")
VARIANT_ALIASES = load_json("variant_aliases.json")
VARIANT_CATALOG = load_variant_catalog()
VARIANT_CATALOG_INDEX = index_variant_catalog(VARIANT_CATALOG)
EXTERNAL_EVIDENCE = index_external_evidence(load_csv_rows("data/external_evidence_map.csv"))
CIVIC_CANDIDATES = load_csv_rows("data/raw/civic_variant_candidates.csv")
DISEASE_GENE_CATALOG = index_disease_gene_catalog(load_csv_rows("data/disease_gene_catalog.csv"))
REVIEW_REQUIRED_GENE_TERMS = {
    term for term, canonical in GENE_ALIASES.items() if canonical == "REVIEW_REQUIRED"
}
REVIEW_REQUIRED_GENE_TERMS.update({"TRK", "trk", "NTRK", "ntrk", "REVIEW_REQUIRED"})
CANNOT_RECONCILE_GENE_TERMS = {
    term for term, canonical in GENE_ALIASES.items() if canonical == "CANNOT_RECONCILE"
}
CANNOT_RECONCILE_GENE_TERMS.add("CANNOT_RECONCILE")
CATEGORICAL_NTRK_FUSION = "Categorical NTRK Fusion (NTRK1/NTRK2/NTRK3)"

# Pre-build fuzzy search pools
_DISEASE_KEYS = list(CANCER_ALIASES.keys())
_GENE_KEYS = [k for k, v in GENE_ALIASES.items() if v not in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}]

FUZZY_THRESHOLD = 80   # minimum score 0-100 to accept a fuzzy match


# ── Fuzzy helpers ─────────────────────────────────────────────────────────────

def _fallback_fuzzy_score(
    query: str,
    candidate: str,
    allow_partial: bool = False,
) -> float:
    query_norm = re.sub(r"[^a-z0-9]+", "", query.lower())
    candidate_norm = re.sub(r"[^a-z0-9]+", "", candidate.lower())
    if not query_norm or not candidate_norm:
        return 0.0
    ratio = SequenceMatcher(None, query_norm, candidate_norm).ratio() * 100
    shorter, longer = sorted((query_norm, candidate_norm), key=len)
    partial = 0.0
    if allow_partial and len(shorter) <= len(longer):
        partial = max(
            SequenceMatcher(None, shorter, longer[i:i + len(shorter)]).ratio() * 100
            for i in range(len(longer) - len(shorter) + 1)
        )
    return max(ratio, partial)


def _extract_one(
    value: str,
    choices: list[str],
    allow_partial: bool = False,
):
    if FUZZY_AVAILABLE:
        return rfprocess.extractOne(value, choices, scorer=fuzz.WRatio)
    if not choices:
        return None
    scored = [
        (choice, _fallback_fuzzy_score(value, choice, allow_partial))
        for choice in choices
    ]
    choice, score = max(scored, key=lambda item: item[1])
    return choice, score, choices.index(choice)


def fuzzy_match_disease(value: str):
    """Return (canonical, score, matched_key) or (None, 0, None)."""
    if not _DISEASE_KEYS:
        return None, 0, None
    result = _extract_one(value, _DISEASE_KEYS)
    if result and result[1] >= FUZZY_THRESHOLD:
        matched_key = result[0]
        return CANCER_ALIASES.get(matched_key), result[1], matched_key
    return None, 0, None


def fuzzy_match_gene(value: str):
    """Return (canonical, score, matched_key) or (None, 0, None)."""
    if not _GENE_KEYS:
        return None, 0, None
    result = _extract_one(value, _GENE_KEYS)
    if result and result[1] >= FUZZY_THRESHOLD:
        matched_key = result[0]
        canonical = GENE_ALIASES.get(matched_key)
        if canonical in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}:
            return None, 0, None
        return canonical, result[1], matched_key
    return None, 0, None


def fuzzy_match_variant(
    value: str,
    canonical_gene: str | None,
    canonical_cancer: str | None = None,
):
    """Return (catalog_row, score) or (None, 0)."""
    if not canonical_gene:
        return None, 0
    # Build pool of (alias, row) for this gene
    pool = []
    for row in VARIANT_CATALOG:
        if row.get("gene") != canonical_gene:
            continue
        if canonical_cancer and row.get("disease_scope") != canonical_cancer:
            continue
        pool.append((row["variant"], row))
        for alias in row.get("variant_aliases", "").split(";"):
            alias = alias.strip()
            if alias:
                pool.append((alias, row))
    if not pool:
        return None, 0
    keys = [p[0] for p in pool]
    result = _extract_one(value, keys, allow_partial=True)
    if result and result[1] >= FUZZY_THRESHOLD:
        idx = keys.index(result[0])
        return pool[idx][1], result[1]
    return None, 0


# ── Numeric confidence scoring ────────────────────────────────────────────────

def compute_confidence_score(
    cancer_ok: bool,
    gene_ok: bool,
    variant_ok: bool,
    gene_match_method: str,   # "exact" | "fuzzy" | "none"
    variant_match_method: str,  # "catalog" | "fuzzy" | "alias" | "none"
    source_authority: float,   # 0.0–1.0: how authoritative is the source
    fuzzy_gene_score: float,   # 0–100 from rapidfuzz (normalised to 0–1)
    fuzzy_variant_score: float,
    context_consistent: bool,  # disease+gene+variant all resolved
) -> dict:
    """
    Compute a 0.0–1.0 confidence score from 6 weighted signals.
    Returns score_breakdown dict and final score.

    Weights (sum to 1.0):
        match_type       0.30
        source_authority 0.20
        string_similarity 0.20
        context_consistency 0.15
        alias_coverage   0.10
        variant_catalog  0.05
    """
    # match_type signal (0–1)
    if gene_match_method in {"exact", "catalog"} and variant_match_method in ("catalog", "alias"):
        match_type_score = 1.0
    elif gene_match_method in {"exact", "catalog"} and variant_match_method == "fuzzy":
        match_type_score = 0.75
    elif gene_match_method == "fuzzy" and variant_match_method in ("catalog", "alias"):
        match_type_score = 0.65
    elif gene_match_method == "fuzzy" and variant_match_method == "fuzzy":
        match_type_score = 0.50
    elif gene_match_method == "external_candidate" or variant_match_method == "external_candidate":
        match_type_score = 0.40
    elif gene_match_method in {"exact", "catalog"} or variant_match_method in ("catalog", "alias"):
        match_type_score = 0.45
    elif gene_match_method == "fuzzy" or variant_match_method == "fuzzy":
        match_type_score = 0.30
    else:
        match_type_score = 0.0

    # string_similarity signal (normalise fuzzy scores 0–100 → 0–1)
    gene_sim = (
        fuzzy_gene_score / 100.0
        if gene_match_method in {"fuzzy", "external_candidate"}
        else (1.0 if gene_ok else 0.0)
    )
    variant_sim = (
        fuzzy_variant_score / 100.0
        if variant_match_method in {"fuzzy", "external_candidate"}
        else (1.0 if variant_ok else 0.0)
    )
    string_similarity = (gene_sim + variant_sim) / 2

    # context_consistency signal
    context_score = 1.0 if context_consistent else (0.5 if (cancer_ok or gene_ok or variant_ok) else 0.0)

    # alias_coverage (proxy: more entities resolved = higher coverage)
    resolved = sum([cancer_ok, gene_ok, variant_ok])
    alias_coverage = resolved / 3.0

    # variant_catalog signal
    catalog_score = (
        1.0
        if variant_match_method == "catalog"
        else (
            0.25
            if variant_match_method == "external_candidate"
            else (0.5 if variant_ok else 0.0)
        )
    )

    breakdown = {
        "match_type":          round(match_type_score, 3),
        "source_authority":    round(source_authority, 3),
        "string_similarity":   round(string_similarity, 3),
        "context_consistency": round(context_score, 3),
        "alias_coverage":      round(alias_coverage, 3),
        "variant_catalog":     round(catalog_score, 3),
    }

    weights = {
        "match_type":          0.30,
        "source_authority":    0.20,
        "string_similarity":   0.20,
        "context_consistency": 0.15,
        "alias_coverage":      0.10,
        "variant_catalog":     0.05,
    }

    score = sum(breakdown[k] * weights[k] for k in breakdown)
    return {"score": round(score, 3), "breakdown": breakdown}


def score_to_confidence(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    if score >= 0.45:
        return "MEDIUM"
    return "LOW"


def score_to_status(score: float, canonical_gene, canonical_variant) -> str:
    if score >= 0.75:
        return "AUTO_RECONCILE"
    if canonical_gene or canonical_variant:
        return "REVIEW_REQUIRED"
    return "CANNOT_RECONCILE"


# ── Entity normalisation ──────────────────────────────────────────────────────

def normalize_cancer_type(value: str | None):
    if not value:
        return None, None, "none", 0.0
    raw = value.strip()
    canonical = (
        CANCER_ALIASES.get(value)
        or CANCER_ALIASES.get(raw)
        or CANCER_ALIASES.get(raw.lower())
    )
    if canonical:
        return canonical, "Cancer type alias match", "exact", 1.0

    # Fuzzy fallback
    canon_fuzzy, score, matched = fuzzy_match_disease(raw)
    if canon_fuzzy:
        return canon_fuzzy, f"Cancer type fuzzy match ({matched}, score {score})", "fuzzy", score / 100.0

    return None, None, "none", 0.0


def normalize_gene(value: str):
    raw = value.strip()
    canonical = GENE_ALIASES.get(value) or GENE_ALIASES.get(raw) or GENE_ALIASES.get(raw.lower())
    if canonical in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}:
        return None, None, "none", 0.0
    if canonical:
        return canonical, "Gene alias match", "exact", 1.0

    # Fuzzy fallback
    canon_fuzzy, score, matched = fuzzy_match_gene(raw)
    if canon_fuzzy:
        return canon_fuzzy, f"Gene fuzzy match ({matched}, score {score})", "fuzzy", score / 100.0

    return None, None, "none", 0.0


def get_gene_review_required(value: str):
    raw = value.strip()
    review = GENE_REVIEW_REQUIRED.get(value) or GENE_REVIEW_REQUIRED.get(raw)
    if review:
        return review
    if raw in REVIEW_REQUIRED_GENE_TERMS:
        return {
            "reason": (
                f"{raw} may refer to multiple NTRK-family genes and requires "
                "human review before selecting a canonical gene."
            )
        }
    return None


def get_gene_cannot_reconcile(value: str):
    return value.strip() in CANNOT_RECONCILE_GENE_TERMS


def find_catalog_variant(
    value: str,
    canonical_gene: str | None,
    gene_review_required: bool,
    canonical_cancer: str | None,
):
    raw = value.strip()
    candidate_genes = []
    if canonical_gene:
        candidate_genes.append(canonical_gene)
    if gene_review_required:
        candidate_genes.append("REVIEW_REQUIRED")
    candidate_genes.append("CANNOT_RECONCILE")

    for gene in candidate_genes:
        matches = (
            VARIANT_CATALOG_INDEX.get((gene, raw))
            or VARIANT_CATALOG_INDEX.get((gene, raw.lower()))
        )
        if matches:
            scoped_matches = [
                row for row in matches
                if not canonical_cancer or row.get("disease_scope") == canonical_cancer
            ]
            if scoped_matches:
                return scoped_matches[0], "Variant catalog match", "catalog", 1.0

    return None, None, "none", 0.0


def normalize_variant(
    value: str,
    canonical_gene: str | None,
    gene_review_required: bool = False,
    canonical_cancer: str | None = None,
):
    catalog_row, catalog_reason, catalog_method, _ = find_catalog_variant(
        value, canonical_gene, gene_review_required, canonical_cancer
    )
    if catalog_row:
        return catalog_row["variant"], catalog_reason, catalog_row, "catalog", 1.0

    raw = value.strip()
    if gene_review_required and raw.lower() in {"fusion", "rearrangement", "translocation"}:
        return CATEGORICAL_NTRK_FUSION, "Cat-VRS-style categorical fusion ambiguity", None, "alias", 0.85

    mapped = VARIANT_ALIASES.get(raw)
    if mapped:
        if "{gene}" in mapped:
            if canonical_gene:
                mapped = mapped.replace("{gene}", canonical_gene)
            else:
                mapped = None
        if mapped and " " in mapped:
            mapped_gene = mapped.split(" ", 1)[0]
            if mapped_gene.isupper() and canonical_gene != mapped_gene:
                mapped = None
        if mapped:
            return mapped, "Variant synonym match", None, "alias", 1.0

    # Fuzzy variant fallback
    if canonical_gene and not looks_like_protein_variant(raw):
        fuzz_row, fuzz_score = fuzzy_match_variant(raw, canonical_gene, canonical_cancer)
        if fuzz_row:
            return fuzz_row["variant"], f"Variant fuzzy match (score {fuzz_score})", fuzz_row, "fuzzy", fuzz_score / 100.0

    return None, None, None, "none", 0.0


def external_evidence_for_variant(canonical_gene: str | None, canonical_variant: str | None) -> list[EvidenceItem]:
    if not canonical_gene or not canonical_variant:
        return []

    evidence_items = []
    seen = set()
    for row in EXTERNAL_EVIDENCE.get(evidence_key(canonical_gene, canonical_variant), []):
        key = (row.get("source"), row.get("url"), row.get("description"))
        if key in seen:
            continue
        seen.add(key)
        evidence_items.append(EvidenceItem(
            source=row.get("source") or "External Evidence Reference",
            type="external_evidence_reference",
            description=row.get("description") or f"{canonical_variant} has locally curated supporting source context.",
            evidence_type=row.get("evidence_type") or "external_reference",
            confidence_weight=row.get("confidence_weight") or "MEDIUM",
            retrieval_mode=row.get("retrieval_mode") or "local_curated_external_reference",
            url=row.get("url") or None,
        ))

    # CIViC candidates are downloaded local provenance rows, not live API lookups.
    for row in CIVIC_CANDIDATES:
        if row.get("query_gene", "").strip().lower() != canonical_gene.strip().lower():
            continue
        terms = [
            row.get("molecular_profile", ""),
            row.get("variant_name", ""),
        ]
        if not any(canonical_variant.lower() in term.lower() for term in terms if term):
            continue
        variant_link = row.get("variant_link") or ""
        url = f"https://civicdb.org{variant_link}" if variant_link.startswith("/") else None
        key = ("CIViC", url, row.get("evidence_item_id"))
        if key in seen:
            continue
        seen.add(key)
        evidence_items.append(EvidenceItem(
            source="CIViC",
            type="external_evidence_candidate",
            description=(
                f"Local CIViC candidate row supports {canonical_variant}: "
                f"{row.get('evidence_type', 'evidence')} level {row.get('evidence_level') or 'unknown'}, "
                f"direction {row.get('evidence_direction') or 'unknown'}."
            ),
            evidence_type="external_candidate_evidence",
            confidence_weight="MEDIUM",
            retrieval_mode="local_civic_candidate_csv",
            url=url,
        ))
        if sum(1 for item in evidence_items if item.source == "CIViC") >= 2:
            break

    return evidence_items


def genes_from_categorical_variant_name(variant_name: str | None) -> list[str]:
    if not variant_name:
        return []

    genes = []
    for parenthetical in re.findall(r"\(([^)]+)\)", variant_name):
        for token in re.split(r"[/,; ]+", parenthetical):
            token = token.strip()
            if token and token.isupper() and any(char.isdigit() for char in token):
                genes.append(token)
    return genes


def catalog_review_candidate_rows(
    catalog_row: dict | None,
    canonical_gene: str | None,
    canonical_variant: str | None,
) -> list[dict]:
    if not catalog_row:
        return []

    disease_scope = catalog_row.get("disease_scope")
    alteration_type = catalog_row.get("alteration_type")
    catalog_gene = catalog_row.get("gene")
    candidate_genes = genes_from_categorical_variant_name(canonical_variant)
    if canonical_gene:
        candidate_genes.append(canonical_gene)
    if catalog_gene and catalog_gene not in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}:
        candidate_genes.append(catalog_gene)

    seen_genes = []
    for gene in candidate_genes:
        if gene not in seen_genes:
            seen_genes.append(gene)

    def is_candidate(row: dict, require_same_alteration: bool) -> bool:
        if row.get("mvp_status") != "AUTO_RECONCILE":
            return False
        if disease_scope and row.get("disease_scope") != disease_scope:
            return False
        if seen_genes and row.get("gene") not in seen_genes:
            return False
        if row.get("variant") == canonical_variant:
            return False
        if require_same_alteration and alteration_type and row.get("alteration_type") != alteration_type:
            return False
        return True

    rows = [row for row in VARIANT_CATALOG if is_candidate(row, require_same_alteration=True)]
    if not rows:
        rows = [row for row in VARIANT_CATALOG if is_candidate(row, require_same_alteration=False)]
    return rows[:3]


def alternatives_from_catalog_rows(
    rows: list[dict],
    category: str | None = None,
    requires_review: bool = True,
) -> list[dict]:
    return [
        {
            "id": row["gene"] + ":" + row["variant"],
            "name": row["variant"],
            "reason": row.get("notes", ""),
            "mvp_status": row.get("mvp_status", ""),
            "source": row.get("source", "manual_curated"),
            "category": category,
            "ambiguity_model": "Cat-VRS-inspired" if requires_review else None,
            "requires_review": requires_review,
        }
        for row in rows
    ]


def llm_review_suggestion(
    req: ReconcileRequest,
    canonical_cancer: str | None,
    canonical_gene: str | None,
    canonical_variant: str | None,
    alternatives: list,
    review_status: str,
    evidence: list[EvidenceItem],
    audit_trail: list[str],
) -> list:
    """Add an optional LLM suggestion, but only for human-review records."""
    if review_status != "REVIEW_REQUIRED":
        return alternatives

    candidates = []
    if canonical_variant:
        candidates.append(canonical_variant)
    elif canonical_gene:
        candidates.append(canonical_gene)
    for item in alternatives:
        name = item.get("name") if isinstance(item, dict) else None
        if name and name not in candidates:
            candidates.append(name)

    if not candidates:
        audit_trail.append("LLM suggestion skipped: no candidates available")
        return alternatives

    entity_type = "gene" if not canonical_gene else "variant"
    input_value = req.gene if entity_type == "gene" else req.variant
    suggestion = llm.disambiguate(
        entity_type=entity_type,
        input_value=input_value,
        candidates=candidates,
        context={
            "input_cancer_type": req.cancer_type,
            "canonical_cancer_type": canonical_cancer,
            "input_gene": req.gene,
            "canonical_gene": canonical_gene,
            "input_variant": req.variant,
            "canonical_variant": canonical_variant,
        },
    )
    provider = suggestion.get("provider", "unknown")
    audit_trail.append(f"LLM suggestion evaluated for REVIEW_REQUIRED only (provider: {provider})")

    best_match = suggestion.get("best_match")
    if not best_match:
        audit_trail.append("LLM suggestion returned no candidate")
        return alternatives

    confidence = suggestion.get("confidence", 0.0)
    rationale = suggestion.get("rationale") or "LLM suggested this candidate for human review."
    evidence.append(EvidenceItem(
        source=f"LLM suggestion ({provider})",
        type="llm_review_suggestion",
        description=(
            f"LLM suggested {best_match} with confidence {confidence}. "
            f"{rationale} This suggestion requires human review and cannot auto-reconcile."
        ),
        evidence_type="llm_suggestion_review_required",
        confidence_weight="LOW",
        retrieval_mode=f"llm_{provider}_review_required",
    ))
    alternatives.append({
        "id": f"llm:{best_match}",
        "name": best_match,
        "reason": rationale,
        "source": f"LLM suggestion ({provider})",
        "requires_review": True,
        "confidence": confidence,
    })
    audit_trail.append("LLM suggestion added for human review")
    return alternatives


# ── Main reconcile ────────────────────────────────────────────────────────────

def reconcile_record(
    req: ReconcileRequest,
    allow_live_lookup: bool = True,
) -> ReconcileResponse:
    audit_trail = ["Input received"]

    # Cancer type
    audit_trail.append("Cancer alias lookup attempted")
    canonical_cancer, cancer_reason, cancer_method, cancer_sim = normalize_cancer_type(req.cancer_type)

    # Gene
    audit_trail.append("Gene alias lookup attempted")
    canonical_gene, gene_reason, gene_method, gene_sim = normalize_gene(req.gene)
    audit_trail.append("Gene review-required lookup attempted")
    gene_review_required = get_gene_review_required(req.gene)
    gene_cannot_reconcile = get_gene_cannot_reconcile(req.gene)
    if gene_review_required:
        canonical_gene = None
        gene_reason = None
        gene_method = "none"
        gene_sim = 0.0
    if gene_cannot_reconcile:
        canonical_gene = None
        gene_reason = None
        gene_method = "none"
        gene_sim = 0.0

    external_gene_candidate = None
    if not canonical_gene and not gene_review_required and not gene_cannot_reconcile:
        audit_trail.append("External gene candidate lookup attempted")
        external_gene_candidate = (
            local_gene_catalog_candidate_lookup(req.gene, canonical_cancer)
            or external_gene_candidate_lookup(req.gene)
        )
        if external_gene_candidate:
            canonical_gene = external_gene_candidate["symbol"]
            gene_reason = external_gene_candidate["reason"]
            gene_method = external_gene_candidate.get("match_method", "external_candidate")
            gene_sim = external_gene_candidate.get("similarity", 0.85)
            audit_trail.append(
                "Local catalog gene match found"
                if gene_method == "catalog"
                else "External gene candidate found"
            )

    # Variant
    audit_trail.append("Variant lookup attempted")
    canonical_variant, variant_reason, variant_catalog_row, variant_method, variant_sim = normalize_variant(
        req.variant, canonical_gene, bool(gene_review_required), canonical_cancer
    )

    external_variant_candidates = []
    if not canonical_variant and canonical_gene and not gene_review_required and not gene_cannot_reconcile:
        audit_trail.append("External variant candidate lookup attempted")
        external_variant_candidates = external_variant_candidate_lookup(
            canonical_gene,
            req.variant,
        )
        if external_variant_candidates:
            canonical_variant = external_variant_candidates[0]["name"]
            variant_reason = "External API/syntax candidate lookup"
            variant_catalog_row = None
            variant_method = "external_candidate"
            variant_sim = 0.70
            audit_trail.append("External variant candidate found")

    # ── Build evidence list ───────────────────────────────────────────────────
    evidence = []
    alternatives = []

    if cancer_reason:
        audit_trail.append(f"Cancer type match ({cancer_method})")
        evidence.append(EvidenceItem(
            source="Seed Knowledge Base",
            type="cancer_type_alias",
            description=f"{req.cancer_type} was mapped to {canonical_cancer} ({cancer_method}).",
            evidence_type="alias_dictionary_match",
            confidence_weight="MEDIUM",
            retrieval_mode=f"local_{cancer_method}_alias",
        ))

    if gene_reason:
        audit_trail.append(f"Gene match ({gene_method})")
        if gene_method == "external_candidate":
            source = (
                external_gene_candidate.get("source", "External Gene API")
                if external_gene_candidate
                else "External Gene API"
            )
            is_local = source.startswith("Local")
            evidence.append(EvidenceItem(
                source=source,
                type="gene_catalog_candidate" if is_local else "gene_external_candidate",
                description=(
                    f"{req.gene} was mapped to candidate gene {canonical_gene}. "
                    f"{gene_reason} Human review is recommended before curation."
                ),
                evidence_type=(
                    "local_gene_catalog_candidate"
                    if is_local
                    else "external_gene_candidate"
                ),
                confidence_weight="MEDIUM",
                retrieval_mode=(
                    "local_gene_variant_catalog_candidate"
                    if is_local
                    else "external_mygene_api_candidate"
                ),
                url=external_gene_candidate.get("url") if external_gene_candidate else None,
            ))
        elif gene_method == "catalog":
            evidence.append(EvidenceItem(
                source=(
                    external_gene_candidate.get(
                        "source",
                        "Local Disease/Gene + Variant Catalog",
                    )
                    if external_gene_candidate
                    else "Local Disease/Gene + Variant Catalog"
                ),
                type="gene_catalog_match",
                description=f"{req.gene} was mapped to {canonical_gene}. {gene_reason}",
                evidence_type="local_gene_catalog_match",
                confidence_weight="HIGH",
                retrieval_mode="local_gene_variant_catalog",
            ))
        else:
            evidence.append(EvidenceItem(
                source="Seed Knowledge Base / HGNC-inspired",
                type="gene_alias",
                description=f"{req.gene} was mapped to {canonical_gene} ({gene_method}).",
                evidence_type="alias_dictionary_match",
                confidence_weight="HIGH" if gene_method == "exact" else "MEDIUM",
                retrieval_mode=f"local_{gene_method}_alias",
            ))

    if canonical_cancer and canonical_gene and (
        canonical_cancer.lower(), canonical_gene.upper()
    ) in DISEASE_GENE_CATALOG:
        audit_trail.append("Disease-gene catalog evidence added")
        evidence.append(EvidenceItem(
            source="Disease-Gene Catalog",
            type="disease_gene_context",
            description=f"{canonical_gene} is listed as a curated gene for {canonical_cancer}.",
            evidence_type="disease_gene_catalog_match",
            confidence_weight="MEDIUM",
            retrieval_mode="local_disease_gene_catalog",
        ))

    if gene_review_required:
        audit_trail.append("Gene ambiguity requiring review found")
        evidence.append(EvidenceItem(
            source="Seed Knowledge Base / HGNC-inspired",
            type="gene_review_required",
            description=(
                f"{req.gene} was preserved as a categorical NTRK fusion ambiguity. "
                "Candidates include NTRK1 Fusion, NTRK2 Fusion, and NTRK3 Fusion. "
                "Rather than guessing, the system recommends human review."
            ),
            evidence_type="cat_vrs_style_ambiguity",
            confidence_weight="MEDIUM",
            retrieval_mode="local_review_required",
            governance_standard="Cat-VRS-inspired / VA-Spec-inspired",
        ))
        # Populate Cat-VRS-inspired candidates without selecting a canonical gene.
        alternatives = [
            {
                "id": "NTRK1:fusion",
                "name": "NTRK1 Fusion",
                "reason": "Candidate member of the preserved categorical NTRK fusion ambiguity.",
                "category": CATEGORICAL_NTRK_FUSION,
                "ambiguity_model": "Cat-VRS-inspired",
                "categorical_variant": CATEGORICAL_NTRK_FUSION,
                "requires_review": True,
            },
            {
                "id": "NTRK2:fusion",
                "name": "NTRK2 Fusion",
                "reason": "Candidate member of the preserved categorical NTRK fusion ambiguity.",
                "category": CATEGORICAL_NTRK_FUSION,
                "ambiguity_model": "Cat-VRS-inspired",
                "categorical_variant": CATEGORICAL_NTRK_FUSION,
                "requires_review": True,
            },
            {
                "id": "NTRK3:fusion",
                "name": "NTRK3 Fusion",
                "reason": "Candidate member of the preserved categorical NTRK fusion ambiguity.",
                "category": CATEGORICAL_NTRK_FUSION,
                "ambiguity_model": "Cat-VRS-inspired",
                "categorical_variant": CATEGORICAL_NTRK_FUSION,
                "requires_review": True,
            },
        ]

    if variant_reason:
        audit_trail.append(f"Variant match ({variant_method})")
        if variant_method == "external_candidate":
            source = "Candidate Evidence Lookup"
            confidence_weight = "MEDIUM"
            evidence_type = "external_candidate_evidence"
            retrieval_mode = "external_api_or_syntax_candidate"
            description = (
                f"{req.variant} was mapped to candidate variant {canonical_variant}. "
                "This was found outside the local curated catalog and requires human review."
            )
        else:
            source = "Curated Gene Variant Catalog" if variant_catalog_row else "Seed Knowledge Base"
            confidence_weight = "HIGH" if variant_method == "catalog" else "MEDIUM"
            evidence_type = "alias_dictionary_match"
            retrieval_mode = f"local_{variant_method}"
            description = f"{req.variant} was mapped to {canonical_variant} ({variant_method})."
        evidence.append(EvidenceItem(
            source=source,
            type=(
                "variant_external_candidate"
                if variant_method == "external_candidate"
                else "variant_synonym"
            ),
            description=description,
            evidence_type=evidence_type,
            confidence_weight=confidence_weight,
            retrieval_mode=retrieval_mode,
        ))

        if variant_method == "external_candidate" and external_variant_candidates:
            alternatives = external_variant_candidates
            audit_trail.append("External candidate evidence generated; routed to REVIEW_REQUIRED")

        if variant_catalog_row and variant_catalog_row.get("mvp_status") == "REVIEW_REQUIRED":
            candidate_rows = catalog_review_candidate_rows(
                variant_catalog_row, canonical_gene, canonical_variant
            )
            if candidate_rows and not alternatives:
                alternatives = alternatives_from_catalog_rows(candidate_rows, canonical_variant)
            candidate_names = [
                item.get("name") for item in alternatives if item.get("name")
            ][:3]
            candidate_sentence = (
                f" Candidates include {', '.join(candidate_names)}."
                if candidate_names
                else " No specific candidate can be selected automatically."
            )
            evidence.append(EvidenceItem(
                source="Curated Gene Variant Catalog",
                type="variant_review_required",
                description=(
                    f"{req.variant} was preserved as {canonical_variant}. "
                    f"{variant_catalog_row.get('notes') or 'This catalog concept requires human review.'}"
                    f"{candidate_sentence} Rather than guessing, the system recommends human review."
                ),
                evidence_type="cat_vrs_style_ambiguity",
                confidence_weight="MEDIUM",
                retrieval_mode="local_catalog_review_required",
                governance_standard="Cat-VRS-inspired / VA-Spec-inspired",
            ))
            audit_trail.append("Catalog REVIEW_REQUIRED ambiguity evidence generated")

        external_items = external_evidence_for_variant(canonical_gene, canonical_variant)
        if external_items:
            evidence.extend(external_items)
            audit_trail.append(f"External evidence references added: {len(external_items)}")

        # Build alternatives from catalog (other variants for same gene)
        if canonical_gene and not alternatives:
            alt_rows = [
                r for r in VARIANT_CATALOG
                if r.get("gene") == canonical_gene and r.get("variant") != canonical_variant
            ][:3]
            alternatives = alternatives_from_catalog_rows(alt_rows, requires_review=False)

    if not evidence:
        audit_trail.append("No alias/synonym evidence found")

    # ── Compute numeric confidence score ──────────────────────────────────────
    context_consistent = bool(canonical_cancer and canonical_gene and canonical_variant)
    source_authority = (
        1.0
        if variant_method == "catalog"
        else (0.8 if gene_method in {"exact", "catalog"} else 0.5)
    )

    score_result = compute_confidence_score(
        cancer_ok=bool(canonical_cancer),
        gene_ok=bool(canonical_gene),
        variant_ok=bool(canonical_variant),
        gene_match_method=gene_method,
        variant_match_method=variant_method,
        source_authority=source_authority,
        fuzzy_gene_score=gene_sim * 100,
        fuzzy_variant_score=variant_sim * 100,
        context_consistent=context_consistent,
    )

    confidence_score = score_result["score"]
    score_breakdown = score_result["breakdown"]
    confidence = score_to_confidence(confidence_score)
    review_status = score_to_status(confidence_score, canonical_gene, canonical_variant)

    # Override confidence for special cases
    if gene_cannot_reconcile:
        canonical_variant = None
        confidence_score = 0.0
        score_breakdown = {k: 0.0 for k in score_breakdown}
        confidence = "LOW"
        review_status = "CANNOT_RECONCILE"

    if gene_review_required:
        confidence = "MEDIUM"
        review_status = "REVIEW_REQUIRED"
        confidence_score = min(max(confidence_score, 0.45), 0.74)

    if variant_catalog_row:
        catalog_status = variant_catalog_row.get("mvp_status")
        if catalog_status == "CANNOT_RECONCILE":
            review_status = "CANNOT_RECONCILE"
            confidence = "LOW"
            confidence_score = min(confidence_score, 0.3)
            canonical_variant = None
        elif catalog_status == "REVIEW_REQUIRED":
            review_status = "REVIEW_REQUIRED"
            confidence = "MEDIUM"
            confidence_score = min(max(confidence_score, 0.45), 0.74)
        elif catalog_status == "AUTO_RECONCILE" and canonical_gene and canonical_variant:
            confidence = "HIGH"
            review_status = "AUTO_RECONCILE"

    if gene_method == "external_candidate" or variant_method == "external_candidate":
        confidence = "MEDIUM"
        review_status = "REVIEW_REQUIRED"
        confidence_score = min(max(confidence_score, 0.45), 0.74)
        audit_trail.append("External candidate fallback requires human review")

    audit_trail.append(f"Confidence score: {confidence_score} ({confidence})")
    audit_trail.append(f"Review status decided: {review_status}")

    live_external_evidence_found = False
    live_external_lookup_error = False
    should_external_lookup = allow_live_lookup and (
        not canonical_cancer
        or not canonical_gene
        or not canonical_variant
        or review_status in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}
    )
    if should_external_lookup and req.gene and req.variant:
        audit_trail.append("Live external evidence lookup started")
        external_lookup_items = lookup_all_external_sources(req.gene, req.variant)
        external_evidence_items = [EvidenceItem(**item) for item in external_lookup_items]
        evidence.extend(external_evidence_items)
        live_external_evidence_found = any(
            item.evidence_type != "external_lookup_error"
            for item in external_evidence_items
        )
        live_external_lookup_error = any(
            item.evidence_type == "external_lookup_error"
            for item in external_evidence_items
        )
        audit_trail.append(
            f"Live external evidence lookup completed: {len(external_evidence_items)} evidence item(s)"
        )
        if live_external_evidence_found:
            confidence = "MEDIUM"
            review_status = "REVIEW_REQUIRED"
            confidence_score = min(max(confidence_score, 0.45), 0.74)
            audit_trail.append("External evidence retrieved from live sources")

    alternatives = llm_review_suggestion(
        req=req,
        canonical_cancer=canonical_cancer,
        canonical_gene=canonical_gene,
        canonical_variant=canonical_variant,
        alternatives=alternatives,
        review_status=review_status,
        evidence=evidence,
        audit_trail=audit_trail,
    )

    evidence_dicts = [e.model_dump() for e in evidence]
    explanation = build_explanation(evidence_dicts, confidence, review_status)
    audit_trail.append("Explanation generated")

    notes = []
    if gene_review_required:
        notes.append(gene_review_required.get("reason", "Gene requires human review."))
        notes.append(f"Ambiguity preserved as {CATEGORICAL_NTRK_FUSION} with candidate genes.")
        audit_trail.append("Gene marked for human review")
    if gene_method == "external_candidate":
        notes.append(
            "Gene was resolved from an external candidate lookup and should be curated "
            "before becoming an AUTO_RECONCILE rule."
        )
    if gene_method == "catalog" and external_gene_candidate:
        notes.append("Gene was resolved from local oncology catalog context.")
    if variant_method == "external_candidate":
        notes.append(
            "Variant was found as an external candidate and requires human review "
            "before adding to the local catalog."
        )
    if live_external_evidence_found:
        notes.append("External evidence is advisory and requires human review.")
    if live_external_lookup_error:
        notes.append("One or more external lookups failed; local reconciliation was preserved.")
    if not canonical_gene:
        notes.append("Gene could not be reconciled.")
        audit_trail.append("Gene unresolved")
    if not canonical_variant:
        notes.append("Variant could not be reconciled.")
        audit_trail.append("Variant unresolved")

    catalog_promotion_candidate = (
        variant_method == "external_candidate"
        or live_external_evidence_found
        or any(
            item.type == "variant_external_candidate"
            or item.retrieval_mode in {
                "external_api_or_syntax_candidate",
                "live_myvariant_api",
                "live_clinvar_api",
                "live_civic_api",
                "live_clingen_allele_registry_api",
            }
            for item in evidence
        )
    )
    curation_metadata = {
        "curation_stage": "harmonize",
        "curation_workflow": [
            "raw_input",
            "normalize",
            "harmonize",
            "evidence_discovery",
            "provenance_capture",
            "human_review",
            "curated_output",
        ],
        "aiws_use_case_alignment": [
            "AI-Assisted Curation",
            "AI Governance & Trust",
        ],
        "human_governance_required": review_status == "REVIEW_REQUIRED",
        "catalog_promotion_candidate": catalog_promotion_candidate,
        "standards_status": "standards-inspired prototype",
    }

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
        confidence_score=confidence_score,
        score_breakdown=score_breakdown,
        review_status=review_status,
        alternatives=alternatives,
        notes=notes,
        audit_trail=audit_trail,
        curation_metadata=curation_metadata,
    )
