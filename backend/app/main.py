import csv
import io
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    ReconcileRequest, BatchRequest, BatchResponse,
    ReviewDecision, ReviewQueueItem, ReviewQueueResponse,
)
from .reconcile import reconcile_record
from . import review_store

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "data" / "benchmark_cases.csv"

app = FastAPI(
    title="OncoReconcile AI API",
    description="Human-governed oncology entity reconciliation API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "project": "OncoReconcile AI",
        "version": "2.0.0",
        "status": "ok",
        "docs": "/docs",
        "mvp": {
            "workflow": [
                "normalize",
                "reconcile",
                "detect_ambiguity",
                "explain",
                "review",
                "audit",
            ],
            "standards_alignment": {
                "implemented": ["HGNC-inspired", "HGVS-inspired", "ClinVar-inspired", "ClinGen-inspired"],
                "partially_implemented": ["GA4GH Cat-VRS-inspired", "GA4GH VA-Spec-inspired"],
                "future": ["GA4GH VRS", "FHIR Genomics", "OMOP Oncology"],
            },
        },
    }


def queue_review_required(result) -> None:
    if result.review_status != "REVIEW_REQUIRED":
        return

    case_id = result.case_id or str(uuid.uuid4())
    review_store.add_to_queue(ReviewQueueItem(
        case_id=case_id,
        input=result.input,
        canonical=result.canonical,
        confidence=result.confidence,
        confidence_score=result.confidence_score,
        score_breakdown=result.score_breakdown,
        review_status=result.review_status,
        explanation=result.explanation,
        evidence=result.evidence,
        alternatives=result.alternatives,
        notes=result.notes,
        audit_trail=result.audit_trail,
    ))


def benchmark_metrics() -> dict:
    if not BENCHMARK_PATH.exists():
        raise HTTPException(status_code=404, detail="Benchmark file not found.")

    with BENCHMARK_PATH.open(newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    if not cases:
        raise HTTPException(status_code=400, detail="Benchmark file is empty.")

    total = len(cases)
    full_correct = 0
    status_correct = 0
    resolved = 0
    review_required = 0
    cannot_reconcile = 0
    failures = []

    for row in cases:
        result = reconcile_record(ReconcileRequest(
            case_id=row.get("case_id") or None,
            cancer_type=row.get("input_disease") or None,
            gene=row["input_gene"],
            variant=row["input_variant"],
        ))

        expected_gene = None if row["expected_gene"] in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"} else row["expected_gene"]
        expected_variant = None if row["expected_variant"] == "CANNOT_RECONCILE" else row["expected_variant"]
        expected_status = row["expected_status"]

        disease_ok = result.canonical.cancer_type == row["expected_disease"]
        gene_ok = result.canonical.gene == expected_gene or row["expected_gene"] == "REVIEW_REQUIRED"
        variant_ok = result.canonical.variant == expected_variant
        status_ok = result.review_status == expected_status

        if status_ok:
            status_correct += 1
        if disease_ok and gene_ok and variant_ok and status_ok:
            full_correct += 1
        if result.review_status != "CANNOT_RECONCILE":
            resolved += 1
        if result.review_status == "REVIEW_REQUIRED":
            review_required += 1
        if result.review_status == "CANNOT_RECONCILE":
            cannot_reconcile += 1
        if not (disease_ok and gene_ok and variant_ok and status_ok):
            failures.append({
                "case_id": row["case_id"],
                "expected_status": expected_status,
                "actual_status": result.review_status,
                "expected_gene": expected_gene,
                "actual_gene": result.canonical.gene,
                "expected_variant": expected_variant,
                "actual_variant": result.canonical.variant,
            })

    def rate(value: int) -> float:
        return round(value / total, 4)

    return {
        "benchmark_file": str(BENCHMARK_PATH.relative_to(ROOT)),
        "total_cases": total,
        "accuracy": rate(full_correct),
        "status_accuracy": rate(status_correct),
        "coverage": rate(resolved),
        "review_rate": rate(review_required),
        "cannot_reconcile_rate": rate(cannot_reconcile),
        "targets": {
            "accuracy": 0.90,
            "coverage": 0.95,
        },
        "target_status": {
            "accuracy": rate(full_correct) >= 0.90,
            "coverage": rate(resolved) >= 0.95,
        },
        "counts": {
            "full_correct": full_correct,
            "status_correct": status_correct,
            "resolved": resolved,
            "review_required": review_required,
            "cannot_reconcile": cannot_reconcile,
        },
        "failures": failures[:20],
    }


# ── Single record ─────────────────────────────────────────────────────────────

@app.post("/reconcile")
def reconcile(req: ReconcileRequest):
    result = reconcile_record(req)
    queue_review_required(result)
    return result


# ── JSON batch ────────────────────────────────────────────────────────────────

@app.post("/reconcile/batch")
def reconcile_batch(req: BatchRequest):
    results = [reconcile_record(record) for record in req.records]
    for result in results:
        queue_review_required(result)
    summary = {
        "total_records": len(results),
        "auto_reconcile": sum(r.review_status == "AUTO_RECONCILE" for r in results),
        "review_required": sum(r.review_status == "REVIEW_REQUIRED" for r in results),
        "cannot_reconcile": sum(r.review_status == "CANNOT_RECONCILE" for r in results),
    }
    return BatchResponse(results=results, summary=summary)


# ── CSV file upload ───────────────────────────────────────────────────────────

@app.post("/reconcile/upload")
async def reconcile_upload(file: UploadFile = File(...)):
    """
    Upload a CSV file with columns: case_id (opt), cancer_type (opt), gene, variant.
    Returns batch reconciliation results + summary.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    text = content.decode("utf-8-sig")  # handle BOM
    reader = csv.DictReader(io.StringIO(text))

    required = {"gene", "variant"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=422,
            detail=f"CSV must contain columns: {required}. Found: {reader.fieldnames}"
        )

    records = []
    for row in reader:
        records.append(ReconcileRequest(
            case_id=row.get("case_id") or None,
            cancer_type=row.get("cancer_type") or None,
            gene=row["gene"].strip(),
            variant=row["variant"].strip(),
        ))

    if not records:
        raise HTTPException(status_code=400, detail="CSV file is empty.")

    results = [reconcile_record(r) for r in records]
    for result in results:
        queue_review_required(result)

    summary = {
        "total_records": len(results),
        "auto_reconcile": sum(r.review_status == "AUTO_RECONCILE" for r in results),
        "review_required": sum(r.review_status == "REVIEW_REQUIRED" for r in results),
        "cannot_reconcile": sum(r.review_status == "CANNOT_RECONCILE" for r in results),
        "filename": file.filename,
    }
    return BatchResponse(results=results, summary=summary)


# ── Review queue ──────────────────────────────────────────────────────────────

@app.get("/benchmark")
def get_benchmark_metrics():
    """Evaluate benchmark accuracy, coverage, and review rate for demo validation."""
    return benchmark_metrics()


@app.get("/review-queue")
def get_review_queue(status: str = Query(default="pending", enum=["pending", "reviewed", "all"])):
    """Return items in the review queue. Filter by status: pending | reviewed | all."""
    filter_status = None if status == "all" else status
    items = review_store.get_queue(filter_status)
    return ReviewQueueResponse(
        items=items,
        total=len(review_store.get_queue()),
        pending=len(review_store.get_queue("pending")),
        reviewed=len(review_store.get_queue("reviewed")),
    )


@app.get("/review-queue/{case_id}")
def get_review_item(case_id: str):
    """Retrieve a single review queue item by case_id."""
    item = review_store.get_item(case_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found in review queue.")
    return item


@app.post("/review-queue/{case_id}/decision")
def submit_review_decision(case_id: str, decision: ReviewDecision):
    """Submit a curator decision (approve | reject | edit | override) for a case."""
    decision.case_id = case_id
    updated = review_store.apply_decision(decision)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found in review queue.")
    return {"status": "ok", "case_id": case_id, "decision": decision.decision, "item": updated}


@app.delete("/review-queue")
def clear_review_queue():
    """Clear the entire review queue (admin/testing use)."""
    review_store.clear_queue()
    return {"status": "ok", "message": "Review queue cleared."}
