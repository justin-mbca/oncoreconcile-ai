#!/usr/bin/env python3
"""
Generate a reproducible oncology benchmark dataset from public + seeded sources.

Outputs:
- data/generated/gene_aliases_generated.csv
- data/generated/cancer_aliases_generated.csv
- data/generated/variant_aliases_generated.csv
- data/generated/benchmark_generated.csv
- data/generated/provenance_report.md

Important:
- This script does NOT read any existing OncoReconcile benchmark CSV.
- Benchmark rows are generated from:
  * HGNC REST API gene aliases
  * Manual disease seed list
  * Manual variant seed list
  * Synthetic ambiguity/negative test construction
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


# ----------------------------- Configuration ----------------------------- #

TARGET_GENES = [
    "EGFR",
    "KRAS",
    "ALK",
    "ROS1",
    "RET",
    "MET",
    "ERBB2",
    "TP53",
    "BRAF",
    "PIK3CA",
    "NTRK1",
    "NTRK2",
    "NTRK3",
]

# Requirement #2: small disease alias seed list
DISEASE_SEEDS = {
    "NSCLC": "Non-Small Cell Lung Cancer",
    "Non-Small Cell Lung Cancer": "Non-Small Cell Lung Cancer",
    "LUAD": "Lung Adenocarcinoma",
    "Lung Adenocarcinoma": "Lung Adenocarcinoma",
}

# Requirement #3: variant seeds for common NSCLC biomarkers
VARIANT_SEEDS = {
    "EGFR": [
        "EGFR Exon 19 Deletion",
        "EGFR p.L858R",
        "EGFR p.T790M",
    ],
    "KRAS": ["KRAS p.G12C"],
    "BRAF": ["BRAF p.V600E"],
    "MET": ["MET Exon 14 Skipping"],
    "ALK": ["ALK Fusion"],
    "ROS1": ["ROS1 Fusion"],
    "RET": ["RET Fusion"],
    "ERBB2": ["ERBB2 Amplification"],
    "TP53": ["TP53 p.R175H"],
    "PIK3CA": ["PIK3CA p.E545K"],
}

# Shorthand/alias-style variant phrasing for MEDIUM difficulty generation
VARIANT_SHORTHANDS = {
    "EGFR Exon 19 Deletion": ["Ex19del", "del19"],
    "EGFR p.L858R": ["L858R"],
    "EGFR p.T790M": ["T790M"],
    "KRAS p.G12C": ["G12C"],
    "BRAF p.V600E": ["V600E"],
    "MET Exon 14 Skipping": ["Exon 14 Skipping", "METex14"],
    "ALK Fusion": ["fusion", "rearrangement"],
    "ROS1 Fusion": ["fusion", "rearrangement"],
    "RET Fusion": ["fusion"],
    "ERBB2 Amplification": ["amp", "Amplification"],
    "TP53 p.R175H": ["R175H"],
    "PIK3CA p.E545K": ["E545K"],
}

HGNC_FETCH_URL = "https://rest.genenames.org/fetch/symbol/{symbol}"


# ------------------------------- Utilities ------------------------------- #


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def fetch_hgnc_record(symbol: str) -> dict | None:
    """Fetch a gene record from HGNC REST API by approved symbol."""
    url = HGNC_FETCH_URL.format(symbol=quote(symbol))
    req = Request(url=url, headers={"Accept": "application/json", "User-Agent": "OncoReconcile-BenchmarkGenerator/1.0"})

    try:
        with urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except HTTPError as exc:
        logging.warning("HGNC HTTPError for %s: %s", symbol, exc)
    except URLError as exc:
        logging.warning("HGNC URLError for %s: %s", symbol, exc)
    except TimeoutError:
        logging.warning("HGNC timeout for %s", symbol)
    except json.JSONDecodeError as exc:
        logging.warning("HGNC JSON decode error for %s: %s", symbol, exc)

    return None


def build_gene_alias_map(genes: List[str]) -> Dict[str, Set[str]]:
    """
    Build {canonical_symbol -> set_of_aliases} from HGNC.

    Includes approved symbol itself and known alias/previous symbols.
    """
    alias_map: Dict[str, Set[str]] = {}

    for symbol in genes:
        alias_map[symbol] = {symbol}
        record = fetch_hgnc_record(symbol)

        if not record:
            logging.warning("No HGNC payload for %s; using symbol only.", symbol)
            continue

        docs = record.get("response", {}).get("docs", [])
        if not docs:
            logging.warning("No HGNC docs for %s; using symbol only.", symbol)
            continue

        doc = docs[0]
        approved_symbol = doc.get("symbol", symbol)
        alias_map.setdefault(approved_symbol, set()).add(approved_symbol)

        for key in ("alias_symbol", "prev_symbol"):
            for name in doc.get(key, []) or []:
                if isinstance(name, str) and name.strip():
                    alias_map[approved_symbol].add(name.strip())

    return alias_map


def pick_first_noncanonical_aliases(alias_map: Dict[str, Set[str]]) -> Dict[str, str]:
    """Pick one stable alias per gene for MEDIUM-case generation where possible."""
    chosen: Dict[str, str] = {}
    for canonical, aliases in alias_map.items():
        candidates = sorted(a for a in aliases if a != canonical)
        if candidates:
            chosen[canonical] = candidates[0]
    return chosen


def flatten_variant_alias_rows() -> List[dict]:
    rows: List[dict] = []

    # Canonical rows
    for canonical_gene, variants in VARIANT_SEEDS.items():
        for canonical_variant in variants:
            rows.append(
                {
                    "variant_alias": canonical_variant,
                    "canonical_variant": canonical_variant,
                    "source": "Manual variant seed",
                    "curation_note": f"Canonical seed for {canonical_gene}.",
                }
            )

    # Shorthand rows
    for canonical_variant, aliases in VARIANT_SHORTHANDS.items():
        for alias in aliases:
            rows.append(
                {
                    "variant_alias": alias,
                    "canonical_variant": canonical_variant,
                    "source": "Manual variant seed",
                    "curation_note": "Shorthand/synonym included for MEDIUM case generation.",
                }
            )

    # Deduplicate by variant_alias, preferring first occurrence
    seen = set()
    deduped = []
    for row in rows:
        key = row["variant_alias"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return deduped


# -------------------------- Benchmark case builders ----------------------- #


def build_easy_cases() -> List[dict]:
    """EASY: exact gene symbol + exact canonical variant."""
    cases: List[dict] = []

    for gene in sorted(VARIANT_SEEDS):
        for canonical_variant in VARIANT_SEEDS[gene]:
            cancer_in = "NSCLC"
            expected_cancer = DISEASE_SEEDS[cancer_in]

            # Keep LUAD examples for selected genes to diversify disease seed usage.
            if gene in {"EGFR", "BRAF", "MET", "TP53"}:
                cancer_in = "LUAD"
                expected_cancer = DISEASE_SEEDS[cancer_in]

            cases.append(
                {
                    "cancer_type": cancer_in,
                    "gene": gene,
                    "variant": canonical_variant,
                    "expected_cancer_type": expected_cancer,
                    "expected_gene": gene,
                    "expected_variant": canonical_variant,
                    "difficulty": "EASY",
                    "source": "Manual disease seed;Manual variant seed",
                    "curation_note": "Exact symbol + exact canonical variant.",
                }
            )

    return cases


def build_medium_cases(alias_choice: Dict[str, str]) -> List[dict]:
    """MEDIUM: HGNC gene aliases + variant shorthand."""
    cases: List[dict] = []

    for gene in sorted(VARIANT_SEEDS):
        if gene not in alias_choice:
            continue

        gene_alias = alias_choice[gene]
        for canonical_variant in VARIANT_SEEDS[gene]:
            shorthands = VARIANT_SHORTHANDS.get(canonical_variant, [])
            if not shorthands:
                continue

            variant_in = shorthands[0]
            cancer_in = "Non-Small Cell Lung Cancer" if gene != "BRAF" else "Lung Adenocarcinoma"
            expected_cancer = DISEASE_SEEDS.get(cancer_in, cancer_in)

            cases.append(
                {
                    "cancer_type": cancer_in,
                    "gene": gene_alias,
                    "variant": variant_in,
                    "expected_cancer_type": expected_cancer,
                    "expected_gene": gene,
                    "expected_variant": canonical_variant,
                    "difficulty": "MEDIUM",
                    "source": "HGNC-derived;Manual disease seed;Manual variant seed",
                    "curation_note": "Gene alias + variant shorthand/synonym.",
                }
            )

    return cases


def build_difficult_cases(alias_choice: Dict[str, str]) -> List[dict]:
    """
    DIFFICULT: ambiguous disease/variant terms + unknown genes/variants.
    Includes synthetic ambiguity tests and unresolved negatives.
    """
    erb_alias = alias_choice.get("ERBB2", "HER2")
    egfr_alias = alias_choice.get("EGFR", "HER1")

    return [
        {
            "cancer_type": "lung cancer",
            "gene": erb_alias,
            "variant": "copy gain",
            "expected_cancer_type": "Non-Small Cell Lung Cancer",
            "expected_gene": "ERBB2",
            "expected_variant": "ERBB2 Amplification",
            "difficulty": "DIFFICULT",
            "source": "HGNC-derived;Synthetic ambiguity test",
            "curation_note": "Ambiguous disease and copy-number phrasing.",
        },
        {
            "cancer_type": "thoracic malignancy",
            "gene": "ALK",
            "variant": "positive",
            "expected_cancer_type": "",
            "expected_gene": "ALK",
            "expected_variant": "ALK Fusion",
            "difficulty": "DIFFICULT",
            "source": "Synthetic ambiguity test",
            "curation_note": "Ambiguous disease + non-specific variant wording.",
        },
        {
            "cancer_type": "NSCLC",
            "gene": "UNKNOWN_GENE",
            "variant": "G12C",
            "expected_cancer_type": "Non-Small Cell Lung Cancer",
            "expected_gene": "",
            "expected_variant": "",
            "difficulty": "DIFFICULT",
            "source": "Synthetic ambiguity test",
            "curation_note": "Unknown gene negative control.",
        },
        {
            "cancer_type": "LUAD",
            "gene": "EGFR",
            "variant": "uncommon activating change",
            "expected_cancer_type": "Lung Adenocarcinoma",
            "expected_gene": "EGFR",
            "expected_variant": "",
            "difficulty": "DIFFICULT",
            "source": "Manual disease seed;Synthetic ambiguity test",
            "curation_note": "Known gene, unresolved variant wording.",
        },
        {
            "cancer_type": "NSCLC NOS",
            "gene": egfr_alias,
            "variant": "exon 19-like deletion",
            "expected_cancer_type": "",
            "expected_gene": "EGFR",
            "expected_variant": "EGFR Exon 19 Deletion",
            "difficulty": "DIFFICULT",
            "source": "HGNC-derived;Synthetic ambiguity test",
            "curation_note": "Non-seed disease alias and fuzzy variant phrase.",
        },
        {
            "cancer_type": "Lung Adeno Ca",
            "gene": "MET",
            "variant": "ex14 skip",
            "expected_cancer_type": "",
            "expected_gene": "MET",
            "expected_variant": "MET Exon 14 Skipping",
            "difficulty": "DIFFICULT",
            "source": "Synthetic ambiguity test",
            "curation_note": "Abbreviated disease + shorthand variant phrase.",
        },
        {
            "cancer_type": "NSCLC",
            "gene": "BRAF",
            "variant": "V600-like",
            "expected_cancer_type": "Non-Small Cell Lung Cancer",
            "expected_gene": "BRAF",
            "expected_variant": "",
            "difficulty": "DIFFICULT",
            "source": "Manual disease seed;Synthetic ambiguity test",
            "curation_note": "Ambiguous hotspot class without exact substitution.",
        },
        {
            "cancer_type": "Non-Small Cell Lung Cancer",
            "gene": "KRAS",
            "variant": "UNKNOWN_VARIANT",
            "expected_cancer_type": "Non-Small Cell Lung Cancer",
            "expected_gene": "KRAS",
            "expected_variant": "",
            "difficulty": "DIFFICULT",
            "source": "Manual disease seed;Synthetic ambiguity test",
            "curation_note": "Unknown variant negative control.",
        },
    ]


# ------------------------------- IO helpers ------------------------------ #


def write_csv(path: Path, fieldnames: List[str], rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_provenance_report(path: Path, benchmark_rows: List[dict], stats: dict) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Generated Benchmark Provenance Report",
        "",
        f"Generated at: {generated_at}",
        "",
        "## Method",
        "",
        "This dataset was generated from scratch using:",
        "- HGNC REST API (gene alias retrieval)",
        "- Manual disease seed list",
        "- Manual variant seed list",
        "- Synthetic ambiguity/negative-test construction",
        "",
        "No existing benchmark rows were read by this generator.",
        "",
        "## Summary Statistics",
        "",
        f"- Total Cases: {stats['total_cases']}",
        f"- Easy Cases: {stats['easy_cases']}",
        f"- Medium Cases: {stats['medium_cases']}",
        f"- Difficult Cases: {stats['difficult_cases']}",
        f"- Gene Alias Count: {stats['gene_alias_count']}",
        f"- Disease Alias Count: {stats['disease_alias_count']}",
        f"- Variant Alias Count: {stats['variant_alias_count']}",
        "",
        "## Row-level Provenance",
        "",
        "| case_id | difficulty | source | curation_note |",
        "|---|---|---|---|",
    ]

    for row in benchmark_rows:
        lines.append(
            f"| {row['case_id']} | {row['difficulty']} | {row['source']} | {row['curation_note']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------- Main ---------------------------------- #


def main() -> None:
    configure_logging()

    root = repo_root_from_script()
    out_dir = root / "data" / "generated"

    logging.info("Fetching HGNC aliases for %d target genes...", len(TARGET_GENES))
    gene_alias_map = build_gene_alias_map(TARGET_GENES)
    alias_choice = pick_first_noncanonical_aliases(gene_alias_map)

    # Build alias CSV rows
    gene_alias_rows = []
    for canonical_gene in sorted(gene_alias_map):
        for alias in sorted(gene_alias_map[canonical_gene]):
            gene_alias_rows.append(
                {
                    "gene_alias": alias,
                    "canonical_gene": canonical_gene,
                    "source": "HGNC-derived",
                    "curation_note": "Retrieved from HGNC approved/alias/previous symbol fields.",
                }
            )

    cancer_alias_rows = [
        {
            "cancer_alias": alias,
            "canonical_cancer_type": canonical,
            "source": "Manual disease seed",
            "curation_note": "Seed disease alias for controlled benchmark generation.",
        }
        for alias, canonical in DISEASE_SEEDS.items()
    ]

    variant_alias_rows = flatten_variant_alias_rows()

    # Build benchmark cases from scratch
    easy_cases = build_easy_cases()
    medium_cases = build_medium_cases(alias_choice)
    difficult_cases = build_difficult_cases(alias_choice)

    benchmark_cases = easy_cases + medium_cases + difficult_cases

    # Assign deterministic case IDs
    for idx, row in enumerate(benchmark_cases, start=1):
        row["case_id"] = f"case_{idx:03d}"

    # Write output files
    write_csv(
        out_dir / "gene_aliases_generated.csv",
        ["gene_alias", "canonical_gene", "source", "curation_note"],
        gene_alias_rows,
    )

    write_csv(
        out_dir / "cancer_aliases_generated.csv",
        ["cancer_alias", "canonical_cancer_type", "source", "curation_note"],
        cancer_alias_rows,
    )

    write_csv(
        out_dir / "variant_aliases_generated.csv",
        ["variant_alias", "canonical_variant", "source", "curation_note"],
        variant_alias_rows,
    )

    write_csv(
        out_dir / "benchmark_generated.csv",
        [
            "case_id",
            "cancer_type",
            "gene",
            "variant",
            "expected_cancer_type",
            "expected_gene",
            "expected_variant",
            "difficulty",
            "source",
            "curation_note",
        ],
        benchmark_cases,
    )

    stats = {
        "total_cases": len(benchmark_cases),
        "easy_cases": len(easy_cases),
        "medium_cases": len(medium_cases),
        "difficult_cases": len(difficult_cases),
        "gene_alias_count": len(gene_alias_rows),
        "disease_alias_count": len(cancer_alias_rows),
        "variant_alias_count": len(variant_alias_rows),
    }

    write_provenance_report(out_dir / "provenance_report.md", benchmark_cases, stats)

    # Requirement #10: print summary statistics
    print("\nBenchmark generation complete.")
    print(f"Total Cases: {stats['total_cases']}")
    print(f"Easy Cases: {stats['easy_cases']}")
    print(f"Medium Cases: {stats['medium_cases']}")
    print(f"Difficult Cases: {stats['difficult_cases']}")
    print(f"Gene Alias Count: {stats['gene_alias_count']}")
    print(f"Disease Alias Count: {stats['disease_alias_count']}")
    print(f"Variant Alias Count: {stats['variant_alias_count']}")
    print(f"Output directory: {out_dir}")


if __name__ == "__main__":
    main()
