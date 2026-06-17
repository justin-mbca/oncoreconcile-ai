import csv
from pathlib import Path


DATA_DIR = Path("data")

INPUT_REVIEWED = DATA_DIR / "reviewed_gene_variant_catalog.csv"
OUT_CATALOG = DATA_DIR / "gene_variant_catalog.csv"


def main():
    if not INPUT_REVIEWED.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_REVIEWED}. Create this file after human review."
        )

    approved_rows = []

    with INPUT_REVIEWED.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            approved = str(row.get("approved", "")).strip().lower()
            if approved in {"yes", "y", "true", "1"}:
                approved_rows.append({
                    "disease_scope": row.get("disease_scope", ""),
                    "gene": row.get("gene", ""),
                    "variant": row.get("variant", ""),
                    "variant_aliases": row.get("variant_aliases", ""),
                    "alteration_type": row.get("alteration_type", ""),
                    "source": row.get("source", ""),
                    "mvp_status": row.get("mvp_status", ""),
                    "notes": row.get("notes", ""),
                })

    fieldnames = [
        "disease_scope",
        "gene",
        "variant",
        "variant_aliases",
        "alteration_type",
        "source",
        "mvp_status",
        "notes",
    ]

    with OUT_CATALOG.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(approved_rows)

    print(f"Approved rows: {len(approved_rows)}")
    print(f"Saved curated catalog: {OUT_CATALOG}")


if __name__ == "__main__":
    main()
