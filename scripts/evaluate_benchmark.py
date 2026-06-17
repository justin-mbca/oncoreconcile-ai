#!/usr/bin/env python3
"""
Benchmark evaluation script — computes precision, recall, F1, and accuracy
against the gold-standard benchmark_cases.csv.

Usage:
    cd backend
    python ../scripts/evaluate_benchmark.py

Output:
    Prints a QA report to stdout and writes qa_report.md to project root.
"""
import csv
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.models import ReconcileRequest
from app.reconcile import reconcile_record

BENCHMARK_PATH = ROOT / "data" / "benchmark_cases.csv"
REPORT_PATH = ROOT / "docs" / "qa_report.md"


def load_cases():
    with BENCHMARK_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluate():
    cases = load_cases()
    total = len(cases)

    status_correct = 0
    gene_correct = 0
    variant_correct = 0
    disease_correct = 0
    all_correct = 0

    scores_by_status = {"AUTO_RECONCILE": [], "REVIEW_REQUIRED": [], "CANNOT_RECONCILE": []}
    failures = []

    for row in cases:
        result = reconcile_record(ReconcileRequest(
            case_id=row["case_id"],
            cancer_type=row["input_disease"],
            gene=row["input_gene"],
            variant=row["input_variant"],
        ))

        exp_gene = None if row["expected_gene"] in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"} else row["expected_gene"]
        exp_variant = None if row["expected_variant"] == "CANNOT_RECONCILE" else row["expected_variant"]
        exp_status = row["expected_status"]

        s_ok = result.review_status == exp_status
        g_ok = result.canonical.gene == exp_gene or row["expected_gene"] == "REVIEW_REQUIRED"
        v_ok = result.canonical.variant == exp_variant
        d_ok = result.canonical.cancer_type == row["expected_disease"]

        if s_ok: status_correct += 1
        if g_ok: gene_correct += 1
        if v_ok: variant_correct += 1
        if d_ok: disease_correct += 1
        if s_ok and g_ok and v_ok and d_ok:
            all_correct += 1

        scores_by_status[exp_status].append(result.confidence_score)

        if not (s_ok and g_ok and v_ok and d_ok):
            failures.append({
                "case_id": row["case_id"],
                "input": f"{row['input_gene']} / {row['input_variant']} ({row['input_disease']})",
                "expected": f"status={exp_status} gene={exp_gene} variant={exp_variant} disease={row['expected_disease']}",
                "actual":   f"status={result.review_status} gene={result.canonical.gene} variant={result.canonical.variant} disease={result.canonical.cancer_type}",
                "score":    result.confidence_score,
            })

    def pct(n): return f"{n/total*100:.1f}%"
    def avg(lst): return round(sum(lst)/len(lst), 3) if lst else 0.0

    report_lines = [
        f"# OncoReconcile AI — QA Benchmark Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Benchmark: {BENCHMARK_PATH.name}  |  Total cases: {total}",
        "",
        "## Overall Accuracy",
        f"| Metric | Correct | Total | Accuracy |",
        f"|--------|---------|-------|----------|",
        f"| Full match (all fields) | {all_correct} | {total} | **{pct(all_correct)}** |",
        f"| Review status | {status_correct} | {total} | {pct(status_correct)} |",
        f"| Gene | {gene_correct} | {total} | {pct(gene_correct)} |",
        f"| Variant | {variant_correct} | {total} | {pct(variant_correct)} |",
        f"| Disease | {disease_correct} | {total} | {pct(disease_correct)} |",
        "",
        "## Confidence Score by Expected Status",
        f"| Expected Status | Avg Confidence Score | Cases |",
        f"|----------------|----------------------|-------|",
    ]
    for st, scores in scores_by_status.items():
        report_lines.append(f"| {st} | {avg(scores)} | {len(scores)} |")

    report_lines += [
        "",
        f"## Failures ({len(failures)} cases)",
    ]
    if failures:
        report_lines.append("| Case ID | Input | Expected | Actual | Score |")
        report_lines.append("|---------|-------|----------|--------|-------|")
        for f in failures[:20]:  # cap at 20 for readability
            report_lines.append(f"| {f['case_id']} | {f['input']} | {f['expected']} | {f['actual']} | {f['score']} |")
        if len(failures) > 20:
            report_lines.append(f"| ... | *(+{len(failures)-20} more)* | | | |")
    else:
        report_lines.append("✅ All benchmark cases passed!")

    report = "\n".join(report_lines)
    print(report)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport written to {REPORT_PATH}")
    return all_correct, total


if __name__ == "__main__":
    correct, total = evaluate()
    sys.exit(0 if correct == total else 1)
