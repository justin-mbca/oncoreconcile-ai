import csv
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUT_CATALOG = DATA_DIR / "gene_variant_catalog.csv"

FIELDNAMES = [
    "disease_scope",
    "gene",
    "variant",
    "variant_aliases",
    "alteration_type",
    "source",
    "mvp_status",
    "notes",
]

ROWS = [
    # EGFR
    ["Lung Non-Small Cell Carcinoma", "EGFR", "EGFR Exon 19 Deletion", "Ex19del; del19; EGFR Ex19del; EGFR exon 19 deletion; exon19del", "Deletion", "manual_curated", "AUTO_RECONCILE", "Common NSCLC EGFR alteration."],
    ["Lung Non-Small Cell Carcinoma", "EGFR", "EGFR L858R", "L858R; EGFR L858R", "SNV", "manual_curated", "AUTO_RECONCILE", "Common EGFR activating mutation."],
    ["Lung Non-Small Cell Carcinoma", "EGFR", "EGFR T790M", "T790M; EGFR T790M", "SNV", "manual_curated", "AUTO_RECONCILE", "Common EGFR resistance mutation."],
    ["Lung Non-Small Cell Carcinoma", "EGFR", "EGFR Exon 20 Insertion", "Exon20ins; EGFR exon 20 insertion", "Insertion", "manual_curated", "REVIEW_REQUIRED", "EGFR exon 20 insertion wording may require more specific review."],

    # KRAS
    ["Lung Non-Small Cell Carcinoma", "KRAS", "KRAS G12C", "G12C; KRAS G12C", "SNV", "manual_curated", "AUTO_RECONCILE", "Common KRAS alteration."],
    ["Lung Non-Small Cell Carcinoma", "KRAS", "KRAS G12D", "G12D; KRAS G12D", "SNV", "manual_curated", "AUTO_RECONCILE", "Common KRAS codon 12 alteration."],
    ["Lung Non-Small Cell Carcinoma", "KRAS", "KRAS G12V", "G12V; KRAS G12V", "SNV", "manual_curated", "AUTO_RECONCILE", "Common KRAS codon 12 alteration."],
    ["Lung Non-Small Cell Carcinoma", "KRAS", "KRAS Mutation", "KRAS mutation; mutation", "Mutation", "manual_curated", "REVIEW_REQUIRED", "Generic KRAS mutation needs specific alteration."],

    # BRAF
    ["Lung Non-Small Cell Carcinoma", "BRAF", "BRAF V600E", "V600E; BRAF V600E", "SNV", "manual_curated", "AUTO_RECONCILE", "Canonical BRAF alteration."],
    ["Lung Non-Small Cell Carcinoma", "BRAF", "BRAF V600K", "V600K; BRAF V600K", "SNV", "manual_curated", "AUTO_RECONCILE", "BRAF V600 alteration."],
    ["Lung Non-Small Cell Carcinoma", "BRAF", "BRAF Mutation", "BRAF mutation; mutation", "Mutation", "manual_curated", "REVIEW_REQUIRED", "Generic BRAF mutation needs specific alteration."],

    # ERBB2
    ["Lung Non-Small Cell Carcinoma", "ERBB2", "ERBB2 Amplification", "HER2 amp; HER2 amplification; ERBB2 amplification; amp; amplification; gene amplification", "Copy Number", "manual_curated", "AUTO_RECONCILE", "HER2/ERBB2 amplification example."],
    ["Lung Non-Small Cell Carcinoma", "ERBB2", "ERBB2 Copy Number Gain", "HER2 copy gain; ERBB2 copy gain; copy gain; copy number gain", "Copy Number", "manual_curated", "AUTO_RECONCILE", "ERBB2 copy-number wording."],
    ["Lung Non-Small Cell Carcinoma", "ERBB2", "ERBB2 Mutation", "HER2 mutation; ERBB2 mutation; mutation", "Mutation", "manual_curated", "REVIEW_REQUIRED", "Generic ERBB2 mutation requires specific variant detail."],

    # MET
    ["Lung Non-Small Cell Carcinoma", "MET", "MET Exon 14 Skipping", "METex14; MET exon14 skipping; MET exon 14 skipping; Exon 14 Skipping", "Splice / Exon Skipping", "manual_curated", "AUTO_RECONCILE", "Important MET alteration in NSCLC."],
    ["Lung Non-Small Cell Carcinoma", "MET", "MET Amplification", "MET amp; MET amplification; amp; amplification", "Copy Number", "manual_curated", "AUTO_RECONCILE", "MET copy-number alteration."],
    ["Lung Non-Small Cell Carcinoma", "MET", "MET Mutation", "MET mutation; mutation", "Mutation", "manual_curated", "REVIEW_REQUIRED", "Generic MET mutation needs specific alteration."],

    # Fusion genes
    ["Lung Non-Small Cell Carcinoma", "ALK", "ALK Fusion", "ALK fusion; ALK rearrangement; ALK translocation; fusion; rearrangement", "Fusion", "manual_curated", "AUTO_RECONCILE", "ALK fusion/rearrangement."],
    ["Lung Non-Small Cell Carcinoma", "ROS1", "ROS1 Fusion", "ROS1 fusion; ROS1 rearrangement; ROS1 translocation; fusion; rearrangement; translocation", "Fusion", "manual_curated", "AUTO_RECONCILE", "ROS1 fusion/rearrangement."],
    ["Lung Non-Small Cell Carcinoma", "RET", "RET Fusion", "RET fusion; RET rearrangement; RET translocation; fusion; rearrangement; translocation", "Fusion", "manual_curated", "AUTO_RECONCILE", "RET fusion/rearrangement."],
    ["Lung Non-Small Cell Carcinoma", "NTRK1", "NTRK1 Fusion", "NTRK1 fusion", "Fusion", "manual_curated", "AUTO_RECONCILE", "Specific NTRK1 fusion."],
    ["Lung Non-Small Cell Carcinoma", "NTRK2", "NTRK2 Fusion", "NTRK2 fusion", "Fusion", "manual_curated", "AUTO_RECONCILE", "Specific NTRK2 fusion."],
    ["Lung Non-Small Cell Carcinoma", "NTRK3", "NTRK3 Fusion", "NTRK3 fusion", "Fusion", "manual_curated", "AUTO_RECONCILE", "Specific NTRK3 fusion."],

    # TP53
    ["Lung Non-Small Cell Carcinoma", "TP53", "TP53 R175H", "R175H; TP53 R175H", "SNV", "manual_curated", "AUTO_RECONCILE", "Useful p53/TP53 benchmark example."],
    ["Lung Non-Small Cell Carcinoma", "TP53", "TP53 Mutation", "p53 mutation; TP53 mutation; mutation", "Mutation", "manual_curated", "REVIEW_REQUIRED", "Generic TP53 mutation requires specific variant detail."],

    # Review-required examples
    ["Lung Non-Small Cell Carcinoma", "REVIEW_REQUIRED", "TRK Fusion", "TRK fusion; pan-TRK fusion; pan-trk fusion; NTRK fusion", "Fusion", "manual_curated", "REVIEW_REQUIRED", "Generic TRK/NTRK wording may refer to NTRK1, NTRK2, or NTRK3."],
    ["Lung Non-Small Cell Carcinoma", "REVIEW_REQUIRED", "Generic Positive", "positive; abnormal; detected", "Unknown", "manual_curated", "REVIEW_REQUIRED", "Positive alone lacks enough variant detail."],
    ["Lung Non-Small Cell Carcinoma", "REVIEW_REQUIRED", "Generic Mutation", "mutation; mutated; alteration", "Unknown", "manual_curated", "REVIEW_REQUIRED", "Generic mutation wording requires a specific gene and alteration."],

    # Cannot-reconcile examples
    ["Lung Non-Small Cell Carcinoma", "CANNOT_RECONCILE", "unknown_variant", "unknown_variant; unknown alteration", "Unknown", "manual_curated", "CANNOT_RECONCILE", "Explicit cannot-reconcile benchmark support."],
    ["Lung Non-Small Cell Carcinoma", "CANNOT_RECONCILE", "invalid_variant", "XYZ999; ABC123", "Unknown", "manual_curated", "CANNOT_RECONCILE", "Synthetic invalid examples for safe failure testing."],
]


def main() -> None:
    with OUT_CATALOG.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDNAMES)
        writer.writerows(ROWS)

    print(f"Saved: {OUT_CATALOG}")
    print(f"Rows written: {len(ROWS)}")


if __name__ == "__main__":
    main()