import csv
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")

GENE_ALIASES_FILE = DATA_DIR / "gene_aliases.json"
DISEASE_ALIASES_FILE = DATA_DIR / "disease_aliases.json"
GENE_VARIANT_CATALOG_FILE = DATA_DIR / "gene_variant_catalog.csv"
OUT_FILE = DATA_DIR / "benchmark_cases.csv"

MAX_GENE_ALIASES_PER_GENE = 3
MAX_VARIANT_ALIASES_PER_VARIANT = 3
MVP_BENCHMARK_DISEASE_SCOPES = {"Lung Non-Small Cell Carcinoma"}

FIELDNAMES = [
    "case_id",
    "input_disease",
    "input_gene",
    "input_variant",
    "expected_disease",
    "expected_gene",
    "expected_variant",
    "expected_status",
    "category",
    "source",
    "notes",
]


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"[WARN] Missing {path}; using empty dictionary.")
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_catalog(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_aliases(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(";") if x.strip()]


def build_reverse_gene_aliases(gene_aliases: dict) -> dict:
    reverse = defaultdict(list)

    for alias, canonical in gene_aliases.items():
        reverse[canonical].append(alias)

    return reverse


def pick_disease_alias(disease_aliases: dict, canonical_disease: str) -> str:
    for alias, canonical in disease_aliases.items():
        if canonical == canonical_disease and alias != canonical_disease:
            return alias
    return canonical_disease


def generate_cases():
    gene_aliases = load_json(GENE_ALIASES_FILE)
    disease_aliases = load_json(DISEASE_ALIASES_FILE)
    catalog = load_catalog(GENE_VARIANT_CATALOG_FILE)

    reverse_gene_aliases = build_reverse_gene_aliases(gene_aliases)

    cases = []
    case_id = 1

    for row in catalog:
        disease_scope = row["disease_scope"]
        if disease_scope not in MVP_BENCHMARK_DISEASE_SCOPES:
            continue

        gene = row["gene"]
        variant = row["variant"]
        variant_aliases = split_aliases(row["variant_aliases"])
        status = row["mvp_status"]
        notes = row.get("notes", "")
        source = row.get("source", "")

        input_disease = pick_disease_alias(disease_aliases, disease_scope)

        category = (
            "AUTO"
            if status == "AUTO_RECONCILE"
            else "REVIEW"
            if status == "REVIEW_REQUIRED"
            else "CANNOT"
        )

        if status == "AUTO_RECONCILE":
            gene_inputs = reverse_gene_aliases.get(gene, [gene])
            gene_inputs = gene_inputs[:MAX_GENE_ALIASES_PER_GENE]

            variant_inputs = variant_aliases[:MAX_VARIANT_ALIASES_PER_VARIANT]
            if not variant_inputs:
                variant_inputs = [variant]

            for input_gene in gene_inputs:
                for input_variant in variant_inputs:
                    cases.append({
                        "case_id": f"case_{case_id:03d}",
                        "input_disease": input_disease,
                        "input_gene": input_gene,
                        "input_variant": input_variant,
                        "expected_disease": disease_scope,
                        "expected_gene": gene,
                        "expected_variant": variant,
                        "expected_status": status,
                        "category": category,
                        "source": source,
                        "notes": notes,
                    })
                    case_id += 1

        elif status == "REVIEW_REQUIRED":
            variant_inputs = variant_aliases[:MAX_VARIANT_ALIASES_PER_VARIANT] or [variant]

            for input_variant in variant_inputs:
                cases.append({
                    "case_id": f"case_{case_id:03d}",
                    "input_disease": input_disease,
                    "input_gene": "TRK" if "TRK" in variant.upper() else gene,
                    "input_variant": input_variant,
                    "expected_disease": disease_scope,
                    "expected_gene": "REVIEW_REQUIRED",
                    "expected_variant": variant,
                    "expected_status": status,
                    "category": category,
                    "source": source,
                    "notes": notes,
                })
                case_id += 1

        elif status == "CANNOT_RECONCILE":
            variant_inputs = variant_aliases[:MAX_VARIANT_ALIASES_PER_VARIANT] or [variant]

            for input_variant in variant_inputs:
                cases.append({
                    "case_id": f"case_{case_id:03d}",
                    "input_disease": input_disease,
                    "input_gene": "unknown_gene",
                    "input_variant": input_variant,
                    "expected_disease": disease_scope,
                    "expected_gene": "CANNOT_RECONCILE",
                    "expected_variant": "CANNOT_RECONCILE",
                    "expected_status": status,
                    "category": category,
                    "source": source,
                    "notes": notes,
                })
                case_id += 1

    return cases


def main():
    cases = generate_cases()

    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(cases)

    print(f"Saved: {OUT_FILE}")
    print(f"Benchmark cases generated: {len(cases)}")


if __name__ == "__main__":
    main()
