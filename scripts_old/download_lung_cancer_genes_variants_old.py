import json
import time
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
import requests


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUT_GENE_ALIASES_JSON = DATA_DIR / "gene_aliases.json"
OUT_VARIANT_ALIASES_JSON = DATA_DIR / "variant_aliases.json"
OUT_CANDIDATES_CSV = DATA_DIR / "civic_gene_variant_candidates.csv"


# ------------------------------------------------------------
# Selected disease aliases from your current MVP
# ------------------------------------------------------------

DISEASE_ALIASES = {
    "NSCLC": "Lung Non-Small Cell Carcinoma",
    "Non-Small Cell Lung Cancer": "Lung Non-Small Cell Carcinoma",

    "LUAD": "Lung Adenocarcinoma",
    "Adenocarcinoma of the Lung": "Lung Adenocarcinoma",
    "Adenocarcinoma of Lung": "Lung Adenocarcinoma",

    "LUSC": "Lung Squamous Cell Carcinoma",
    "Lung Squamous Cell Carcinoma": "Lung Squamous Cell Carcinoma",

    "Small Cell Carcinoma of Lung": "Lung Small Cell Carcinoma",
    "Lung Small Cell Carcinoma": "Lung Small Cell Carcinoma",
}


# ------------------------------------------------------------
# MVP gene seed list
# You can expand this later.
# ------------------------------------------------------------

LUNG_CANCER_GENE_SEEDS = [
    "EGFR",
    "ERBB2",
    "TP53",
    "KRAS",
    "BRAF",
    "MET",
    "ALK",
    "ROS1",
    "RET",
    "NTRK1",
    "NTRK2",
    "NTRK3",
]


# ------------------------------------------------------------
# API endpoints
# ------------------------------------------------------------

CIVIC_GENE_URL = "https://civicdb.org/api/genes/{symbols}"
MYGENE_QUERY_URL = "https://mygene.info/v3/query"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_get_json(url: str, params: Dict[str, Any] | None = None) -> Any:
    """GET JSON with simple error handling."""
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def normalize_alias(alias: str) -> str:
    """Basic cleanup for aliases."""
    return alias.strip()


def add_alias(alias_map: Dict[str, str], alias: str, canonical: str) -> None:
    """Add alias only when non-empty."""
    if alias and isinstance(alias, str):
        alias_map[normalize_alias(alias)] = canonical


# ------------------------------------------------------------
# CIViC download
# ------------------------------------------------------------

def fetch_civic_genes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    CIViC supports fetching multiple genes by Entrez symbol:
    /api/genes/TP53,BRAF?identifier_type=entrez_symbol
    """
    joined = ",".join(symbols)
    url = CIVIC_GENE_URL.format(symbols=joined)

    data = safe_get_json(
        url,
        params={"identifier_type": "entrez_symbol"}
    )

    # CIViC may return either a list or records depending on endpoint behavior.
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]

    return []


def extract_from_civic(genes: List[Dict[str, Any]]) -> tuple[Dict[str, str], Dict[str, str], List[Dict[str, Any]]]:
    """
    Extract:
    - gene aliases
    - variant aliases/candidates
    - candidate rows for review
    """
    gene_aliases: Dict[str, str] = {}
    variant_aliases: Dict[str, str] = {}
    candidate_rows: List[Dict[str, Any]] = []

    for gene in genes:
        canonical_gene = gene.get("name")
        if not canonical_gene:
            continue

        # Add canonical gene itself
        add_alias(gene_aliases, canonical_gene, canonical_gene)

        # Add CIViC gene aliases
        for alias in gene.get("aliases", []) or []:
            add_alias(gene_aliases, alias, canonical_gene)

        # Extract variant names from CIViC gene record
        for variant in gene.get("variants", []) or []:
            variant_name = variant.get("name")
            if not variant_name:
                continue

            # For MVP, canonical variant is stored as:
            # "{GENE} {VARIANT_NAME}"
            canonical_variant = f"{canonical_gene} {variant_name}"

            add_alias(variant_aliases, variant_name, canonical_variant)
            add_alias(variant_aliases, canonical_variant, canonical_variant)

            candidate_rows.append({
                "source": "CIViC",
                "canonical_gene": canonical_gene,
                "gene_aliases": "; ".join(gene.get("aliases", []) or []),
                "variant_name": variant_name,
                "canonical_variant": canonical_variant,
                "accepted_evidence_count": (
                    variant.get("evidence_items", {}) or {}
                ).get("accepted_count"),
                "submitted_evidence_count": (
                    variant.get("evidence_items", {}) or {}
                ).get("submitted_count"),
                "rejected_evidence_count": (
                    variant.get("evidence_items", {}) or {}
                ).get("rejected_count"),
            })

    return gene_aliases, variant_aliases, candidate_rows


# ------------------------------------------------------------
# MyGene.info alias expansion
# ------------------------------------------------------------

def fetch_mygene_aliases(symbol: str) -> List[str]:
    """
    Query MyGene.info for human gene aliases.

    We keep this conservative because aliases can be noisy.
    """
    params = {
        "q": f"symbol:{symbol}",
        "species": "human",
        "fields": "symbol,name,alias,other_names",
        "size": 5,
    }

    data = safe_get_json(MYGENE_QUERY_URL, params=params)

    aliases: List[str] = []

    for hit in data.get("hits", []):
        if hit.get("symbol") != symbol:
            continue

        raw_alias = hit.get("alias")

        if isinstance(raw_alias, list):
            aliases.extend(raw_alias)
        elif isinstance(raw_alias, str):
            aliases.append(raw_alias)

        other_names = hit.get("other_names")
        if isinstance(other_names, list):
            aliases.extend(other_names)
        elif isinstance(other_names, str):
            aliases.append(other_names)

    # Deduplicate
    return sorted(set(a.strip() for a in aliases if isinstance(a, str) and a.strip()))


def expand_gene_aliases_with_mygene(gene_aliases: Dict[str, str], canonical_genes: List[str]) -> None:
    """Add aliases from MyGene.info into gene_aliases map."""
    for symbol in canonical_genes:
        try:
            aliases = fetch_mygene_aliases(symbol)

            # Be conservative: only add short-ish aliases, not long descriptions.
            for alias in aliases:
                if len(alias) <= 30:
                    add_alias(gene_aliases, alias, symbol)

            time.sleep(0.4)

        except Exception as exc:
            print(f"[WARN] MyGene failed for {symbol}: {exc}")


# ------------------------------------------------------------
# Add manual MVP-safe aliases
# ------------------------------------------------------------

def add_manual_mvp_aliases(gene_aliases: Dict[str, str], variant_aliases: Dict[str, str]) -> None:
    """
    These are clinically common aliases and useful for the competition MVP.
    Keep them because APIs may not contain report-style shorthand.
    """

    manual_gene_aliases = {
        "HER2": "ERBB2",
        "HER-2": "ERBB2",
        "p53": "TP53",
        "P53": "TP53",
        "c-MET": "MET",
        "cMET": "MET",
        "TRK": "REVIEW_REQUIRED",
        "trk": "REVIEW_REQUIRED",
        "unknown_gene": "CANNOT_RECONCILE",
    }

    manual_variant_aliases = {
        "amp": "{gene} Amplification",
        "amplification": "{gene} Amplification",
        "Amplification": "{gene} Amplification",
        "copy gain": "{gene} Copy Number Gain",
        "copy number gain": "{gene} Copy Number Gain",

        "fusion": "{gene} Fusion",
        "Fusion": "{gene} Fusion",
        "rearrangement": "{gene} Fusion",
        "translocation": "{gene} Fusion",

        "Ex19del": "EGFR Exon 19 Deletion",
        "del19": "EGFR Exon 19 Deletion",
        "EGFR Ex19del": "EGFR Exon 19 Deletion",
        "EGFR exon 19 deletion": "EGFR Exon 19 Deletion",

        "L858R": "EGFR L858R",
        "T790M": "EGFR T790M",
        "G12C": "KRAS G12C",
        "G12D": "KRAS G12D",
        "V600E": "BRAF V600E",
        "BRAF V600E": "BRAF V600E",

        "METex14": "MET Exon 14 Skipping",
        "MET exon14 skipping": "MET Exon 14 Skipping",
        "Exon 14 Skipping": "MET Exon 14 Skipping",

        "positive": "REVIEW_REQUIRED",
        "unknown_variant": "CANNOT_RECONCILE",
    }

    gene_aliases.update(manual_gene_aliases)
    variant_aliases.update(manual_variant_aliases)


# ------------------------------------------------------------
# Save outputs
# ------------------------------------------------------------

def save_json(path: Path, data: Dict[str, str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(dict(sorted(data.items())), f, indent=2, ensure_ascii=False)


def main() -> None:
    print("Downloading CIViC gene and variant candidates...")

    civic_genes = fetch_civic_genes(LUNG_CANCER_GENE_SEEDS)
    print(f"CIViC genes returned: {len(civic_genes)}")

    gene_aliases, variant_aliases, candidate_rows = extract_from_civic(civic_genes)

    print("Expanding gene aliases with MyGene.info...")
    expand_gene_aliases_with_mygene(gene_aliases, LUNG_CANCER_GENE_SEEDS)

    print("Adding manual MVP aliases...")
    add_manual_mvp_aliases(gene_aliases, variant_aliases)

    print("Saving outputs...")

    save_json(OUT_GENE_ALIASES_JSON, gene_aliases)
    save_json(OUT_VARIANT_ALIASES_JSON, variant_aliases)

    pd.DataFrame(candidate_rows).to_csv(OUT_CANDIDATES_CSV, index=False)

    print("\nDone.")
    print(f"Gene aliases: {len(gene_aliases)} -> {OUT_GENE_ALIASES_JSON}")
    print(f"Variant aliases: {len(variant_aliases)} -> {OUT_VARIANT_ALIASES_JSON}")
    print(f"Candidate rows: {len(candidate_rows)} -> {OUT_CANDIDATES_CSV}")


if __name__ == "__main__":
    print("=== SCRIPT STARTED ===")
    main()
    #print("=== SCRIPT STARTED ===")