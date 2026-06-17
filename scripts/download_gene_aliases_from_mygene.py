import json
import time
from pathlib import Path

import requests


DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
DATA_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)

OUT_JSON = DATA_DIR / "gene_aliases.json"
OUT_RAW_JSON = RAW_DIR / "raw_gene_alias_candidates.json"

MYGENE_QUERY_URL = "https://mygene.info/v3/query"

GENES = [
    "EGFR", "ERBB2", "TP53", "KRAS", "BRAF", "MET",
    "ALK", "ROS1", "RET", "NTRK1", "NTRK2", "NTRK3"
]

MANUAL_SAFE_ALIASES = {
    "EGFR": "EGFR",
    "ERBB1": "EGFR",
    "HER1": "EGFR",

    "ERBB2": "ERBB2",
    "HER2": "ERBB2",
    "HER-2": "ERBB2",
    "NEU": "ERBB2",

    "TP53": "TP53",
    "p53": "TP53",
    "P53": "TP53",

    "KRAS": "KRAS",
    "K-RAS": "KRAS",
    "K-Ras": "KRAS",

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
    "ROS": "ROS1",

    "RET": "RET",

    "NTRK1": "NTRK1",
    "NTRK2": "NTRK2",
    "NTRK3": "NTRK3",

    "TRK": "REVIEW_REQUIRED",
    "trk": "REVIEW_REQUIRED",

    "unknown_gene": "CANNOT_RECONCILE"
}


def query_mygene(symbol: str) -> dict:
    params = {
        "q": f"symbol:{symbol}",
        "species": "human",
        "fields": "symbol,name,alias,other_names",
        "size": 5,
    }
    response = requests.get(MYGENE_QUERY_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_aliases(symbol: str, data: dict) -> list[str]:
    aliases = []

    for hit in data.get("hits", []):
        if hit.get("symbol") != symbol:
            continue

        for field in ["alias", "other_names"]:
            value = hit.get(field)

            if isinstance(value, list):
                aliases.extend(value)
            elif isinstance(value, str):
                aliases.append(value)

    return sorted(set(a.strip() for a in aliases if isinstance(a, str) and a.strip()))


def main():
    print("Downloading gene aliases from MyGene.info...")

    raw_candidates = {}
    curated_aliases = dict(MANUAL_SAFE_ALIASES)

    for gene in GENES:
        print(f"Querying {gene}")

        try:
            data = query_mygene(gene)
            aliases = extract_aliases(gene, data)

            raw_candidates[gene] = aliases

            for alias in aliases:
                if len(alias) <= 40:
                    curated_aliases[alias] = gene

            time.sleep(0.4)

        except Exception as exc:
            print(f"[WARN] Failed for {gene}: {exc}")

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(dict(sorted(curated_aliases.items())), f, indent=2, ensure_ascii=False)

    with OUT_RAW_JSON.open("w", encoding="utf-8") as f:
        json.dump(raw_candidates, f, indent=2, ensure_ascii=False)

    print(f"Saved curated aliases: {OUT_JSON}")
    print(f"Saved raw candidates: {OUT_RAW_JSON}")
    print(f"Curated alias count: {len(curated_aliases)}")


if __name__ == "__main__":
    main()
