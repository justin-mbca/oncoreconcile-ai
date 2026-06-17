import json
import time
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
import requests


print("=== SCRIPT STARTED ===")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUT_GENE_ALIASES_JSON = DATA_DIR / "gene_aliases.json"
OUT_VARIANT_ALIASES_JSON = DATA_DIR / "variant_aliases.json"
OUT_CANDIDATES_CSV = DATA_DIR / "gene_variant_candidates.csv"

MYGENE_QUERY_URL = "https://mygene.info/v3/query"

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


MANUAL_GENE_ALIASES = {
    "EGFR": "EGFR",
    "ERBB2": "ERBB2",
    "HER2": "ERBB2",
    "HER-2": "ERBB2",
    "NEU": "ERBB2",

    "TP53": "TP53",
    "p53": "TP53",
    "P53": "TP53",

    "KRAS": "KRAS",
    "BRAF": "BRAF",
    "B-RAF": "BRAF",
    "BRAF1": "BRAF",

    "MET": "MET",
    "c-MET": "MET",
    "cMET": "MET",
    "HGFR": "MET",

    "ALK": "ALK",
    "Anaplastic Lymphoma Kinase": "ALK",

    "ROS1": "ROS1",
    "RET": "RET",

    "NTRK1": "NTRK1",
    "NTRK2": "NTRK2",
    "NTRK3": "NTRK3",

    "TRK": "REVIEW_REQUIRED",
    "trk": "REVIEW_REQUIRED",

    "unknown_gene": "CANNOT_RECONCILE"
}


MANUAL_VARIANT_ALIASES = {
    "amp": "{gene} Amplification",
    "amplification": "{gene} Amplification",
    "Amplification": "{gene} Amplification",
    "gene amplification": "{gene} Amplification",

    "copy gain": "{gene} Copy Number Gain",
    "copy number gain": "{gene} Copy Number Gain",

    "fusion": "{gene} Fusion",
    "Fusion": "{gene} Fusion",
    "rearrangement": "{gene} Fusion",
    "translocation": "{gene} Fusion",

    "ALK rearrangement": "ALK Fusion",
    "ROS1 translocation": "ROS1 Fusion",
    "RET fusion": "RET Fusion",
    "NTRK fusion": "NTRK Fusion",
    "pan-trk fusion": "REVIEW_REQUIRED",

    "Ex19del": "EGFR Exon 19 Deletion",
    "del19": "EGFR Exon 19 Deletion",
    "EGFR Ex19del": "EGFR Exon 19 Deletion",
    "EGFR exon 19 deletion": "EGFR Exon 19 Deletion",
    "exon19del": "EGFR Exon 19 Deletion",

    "L858R": "EGFR L858R",
    "T790M": "EGFR T790M",

    "G12C": "KRAS G12C",
    "G12D": "KRAS G12D",
    "G12V": "KRAS G12V",

    "V600E": "BRAF V600E",
    "BRAF V600E": "BRAF V600E",
    "V600K": "BRAF V600K",

    "METex14": "MET Exon 14 Skipping",
    "MET exon14 skipping": "MET Exon 14 Skipping",
    "MET exon 14 skipping": "MET Exon 14 Skipping",
    "Exon 14 Skipping": "MET Exon 14 Skipping",

    "positive": "REVIEW_REQUIRED",
    "abnormal": "REVIEW_REQUIRED",
    "mutation": "REVIEW_REQUIRED",

    "unknown_variant": "CANNOT_RECONCILE"
}


def safe_get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_mygene_aliases(symbol: str) -> List[str]:
    print(f"Querying MyGene.info for {symbol}")

    params = {
        "q": f"symbol:{symbol}",
        "species": "human",
        "fields": "symbol,name,alias,other_names",
        "size": 5,
    }

    data = safe_get_json(MYGENE_QUERY_URL, params)
    aliases = []

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

    aliases = sorted(set(a.strip() for a in aliases if isinstance(a, str) and a.strip()))
    return aliases


def save_json(path: Path, data: Dict[str, str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(dict(sorted(data.items())), f, indent=2, ensure_ascii=False)


def main():
    print("Data directory:", DATA_DIR.resolve())

    gene_aliases = dict(MANUAL_GENE_ALIASES)
    variant_aliases = dict(MANUAL_VARIANT_ALIASES)

    candidate_rows = []

    for gene in LUNG_CANCER_GENE_SEEDS:
        gene_aliases[gene] = gene

        try:
            aliases = fetch_mygene_aliases(gene)
            print(f"  aliases found: {aliases}")

            for alias in aliases:
                if len(alias) <= 40:
                    gene_aliases[alias] = gene

            candidate_rows.append({
                "source": "MyGene.info",
                "canonical_gene": gene,
                "aliases": "; ".join(aliases)
            })

            time.sleep(0.4)

        except Exception as exc:
            print(f"[WARN] MyGene.info failed for {gene}: {exc}")

    print("Saving files...")

    save_json(OUT_GENE_ALIASES_JSON, gene_aliases)
    save_json(OUT_VARIANT_ALIASES_JSON, variant_aliases)
    pd.DataFrame(candidate_rows).to_csv(OUT_CANDIDATES_CSV, index=False)

    print("Done.")
    print(f"Gene aliases: {len(gene_aliases)} -> {OUT_GENE_ALIASES_JSON}")
    print(f"Variant aliases: {len(variant_aliases)} -> {OUT_VARIANT_ALIASES_JSON}")
    print(f"Candidate rows: {len(candidate_rows)} -> {OUT_CANDIDATES_CSV}")


if __name__ == "__main__":
    main()