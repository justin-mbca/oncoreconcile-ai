import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUT_CATALOG = DATA_DIR / "gene_variant_catalog.csv"

GENE_VARIANT_ROWS = [
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "EGFR",
        "variant": "EGFR Exon 19 Deletion",
        "variant_aliases": "Ex19del; del19; EGFR Ex19del; EGFR exon 19 deletion; exon19del",
        "alteration_type": "Deletion",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Common NSCLC EGFR alteration."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "EGFR",
        "variant": "EGFR L858R",
        "variant_aliases": "L858R; EGFR L858R",
        "alteration_type": "SNV",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Common EGFR activating mutation."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "EGFR",
        "variant": "EGFR T790M",
        "variant_aliases": "T790M; EGFR T790M",
        "alteration_type": "SNV",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Common EGFR resistance mutation."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "ERBB2",
        "variant": "ERBB2 Amplification",
        "variant_aliases": "amp; amplification; Amplification; gene amplification",
        "alteration_type": "Copy Number",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Used in demo: HER2 + amp."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "KRAS",
        "variant": "KRAS G12C",
        "variant_aliases": "G12C; KRAS G12C",
        "alteration_type": "SNV",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Common KRAS alteration."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "BRAF",
        "variant": "BRAF V600E",
        "variant_aliases": "V600E; BRAF V600E",
        "alteration_type": "SNV",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Canonical BRAF alteration."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "MET",
        "variant": "MET Exon 14 Skipping",
        "variant_aliases": "METex14; MET exon14 skipping; MET exon 14 skipping; Exon 14 Skipping",
        "alteration_type": "Splice / Exon Skipping",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Important MET alteration in NSCLC."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "ALK",
        "variant": "ALK Fusion",
        "variant_aliases": "ALK fusion; ALK rearrangement; rearrangement; fusion",
        "alteration_type": "Fusion",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "ALK fusion/rearrangement."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "ROS1",
        "variant": "ROS1 Fusion",
        "variant_aliases": "ROS1 fusion; ROS1 rearrangement; ROS1 translocation; fusion",
        "alteration_type": "Fusion",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "ROS1 fusion/rearrangement."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "RET",
        "variant": "RET Fusion",
        "variant_aliases": "RET fusion; RET rearrangement; fusion",
        "alteration_type": "Fusion",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "RET fusion/rearrangement."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "REVIEW_REQUIRED",
        "variant": "TRK Fusion",
        "variant_aliases": "TRK fusion; pan-TRK fusion; pan-trk fusion; NTRK fusion",
        "alteration_type": "Fusion",
        "source": "manual_seed",
        "mvp_status": "REVIEW_REQUIRED",
        "notes": "Generic TRK/NTRK wording may refer to NTRK1, NTRK2, or NTRK3."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "TP53",
        "variant": "TP53 R175H",
        "variant_aliases": "R175H; TP53 R175H",
        "alteration_type": "SNV",
        "source": "manual_seed",
        "mvp_status": "AUTO_RECONCILE",
        "notes": "Useful p53/TP53 benchmark example."
    },
    {
        "disease_scope": "Lung Non-Small Cell Carcinoma",
        "gene": "CANNOT_RECONCILE",
        "variant": "unknown_variant",
        "variant_aliases": "unknown_variant; unknown alteration",
        "alteration_type": "Unknown",
        "source": "manual_seed",
        "mvp_status": "CANNOT_RECONCILE",
        "notes": "Explicit cannot-reconcile benchmark support."
    }
]


def main():
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
        writer.writerows(GENE_VARIANT_ROWS)

    print(f"Done: {OUT_CATALOG}")
    print(f"Rows written: {len(GENE_VARIANT_ROWS)}")


if __name__ == "__main__":
    main()
