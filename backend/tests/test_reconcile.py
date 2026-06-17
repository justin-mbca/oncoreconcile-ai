import csv
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models import ReconcileRequest
from app.reconcile import reconcile_record
from app import reconcile as reconcile_module


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "data" / "benchmark_cases.csv"
client = TestClient(app)


def load_benchmark_cases():
    with BENCHMARK_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def expected_optional_gene(row):
    if row["expected_gene"] in {"REVIEW_REQUIRED", "CANNOT_RECONCILE"}:
        return None
    return row["expected_gene"]


def expected_optional_variant(row):
    if row["expected_variant"] == "CANNOT_RECONCILE":
        return None
    return row["expected_variant"]


def test_benchmark_cases_file_is_well_formed():
    rows = load_benchmark_cases()
    assert len(rows) == 156
    assert {row["expected_status"] for row in rows} == {
        "AUTO_RECONCILE",
        "REVIEW_REQUIRED",
        "CANNOT_RECONCILE",
    }


def test_all_benchmark_cases_reconcile_to_expected_status_and_concepts():
    failures = []
    for row in load_benchmark_cases():
        result = reconcile_record(
            ReconcileRequest(
                case_id=row["case_id"],
                cancer_type=row["input_disease"],
                gene=row["input_gene"],
                variant=row["input_variant"],
            )
        )
        expected_gene = expected_optional_gene(row)
        expected_variant = expected_optional_variant(row)

        checks = {
            "disease": result.canonical.cancer_type == row["expected_disease"],
            "gene": (
                result.canonical.gene == expected_gene
                or row["expected_gene"] == "REVIEW_REQUIRED"
            ),
            "variant": result.canonical.variant == expected_variant,
            "status": result.review_status == row["expected_status"],
        }
        if not all(checks.values()):
            failures.append(
                {
                    "case_id": row["case_id"],
                    "checks": checks,
                    "actual": (
                        result.canonical.cancer_type,
                        result.canonical.gene,
                        result.canonical.variant,
                        result.review_status,
                    ),
                    "expected": (
                        row["expected_disease"],
                        expected_gene,
                        expected_variant,
                        row["expected_status"],
                    ),
                }
            )

    assert failures == []


def test_review_required_trk_fusion_does_not_guess_specific_ntrk_gene():
    req = ReconcileRequest(cancer_type="NSCLC", gene="TRK", variant="pan-trk fusion")
    result = reconcile_record(req)
    assert result.review_status == "REVIEW_REQUIRED"
    assert result.confidence == "MEDIUM"
    assert result.canonical.cancer_type == "Lung Non-Small Cell Carcinoma"
    assert result.canonical.gene is None
    assert result.canonical.variant == "Categorical NTRK Fusion (NTRK1/NTRK2/NTRK3)"
    assert "multiple NTRK-family genes" in " ".join(result.notes)
    assert any(item.evidence_type == "cat_vrs_style_ambiguity" for item in result.evidence)
    assert {item["name"] for item in result.alternatives[:3]} == {
        "NTRK1 Fusion",
        "NTRK2 Fusion",
        "NTRK3 Fusion",
    }
    assert {item["categorical_variant"] for item in result.alternatives[:3]} == {
        "Categorical NTRK Fusion (NTRK1/NTRK2/NTRK3)"
    }


def test_review_required_trk_bare_fusion_preserves_family_variant():
    req = ReconcileRequest(cancer_type="NSCLC", gene="TRK", variant="fusion")
    result = reconcile_record(req)

    assert result.review_status == "REVIEW_REQUIRED"
    assert result.canonical.gene is None
    assert result.canonical.variant == "Categorical NTRK Fusion (NTRK1/NTRK2/NTRK3)"
    assert "categorical NTRK fusion ambiguity" in result.explanation


def test_catalog_review_required_variant_generates_governance_evidence_and_candidates():
    req = ReconcileRequest(cancer_type="Melanoma", gene="BRAF", variant="V600")
    result = reconcile_record(req)

    assert result.review_status == "REVIEW_REQUIRED"
    assert result.canonical.gene == "BRAF"
    assert result.canonical.variant == "BRAF V600 Mutation"
    assert any(item.evidence_type == "cat_vrs_style_ambiguity" for item in result.evidence)
    assert any(item.type == "variant_review_required" for item in result.evidence)
    assert {item["name"] for item in result.alternatives[:2]} == {
        "BRAF V600E",
        "BRAF V600K",
    }


def test_unknown_gene_routes_to_cannot_reconcile():
    req = ReconcileRequest(cancer_type="NSCLC", gene="unknown_gene", variant="unknown_variant")
    result = reconcile_record(req)
    assert result.review_status == "CANNOT_RECONCILE"
    assert result.confidence == "LOW"
    assert result.canonical.gene is None
    assert result.canonical.variant is None
    assert "CANNOT_RECONCILE" in result.explanation


def test_empty_cancer_type_still_reconciles_gene_and_variant():
    req = ReconcileRequest(cancer_type=None, gene="HER2", variant="Amplification")
    result = reconcile_record(req)
    assert result.canonical.gene == "ERBB2"
    assert result.canonical.variant == "ERBB2 Amplification"
    assert result.review_status == "AUTO_RECONCILE"


def test_explanation_always_non_empty():
    req = ReconcileRequest(cancer_type="NSCLC", gene="FAKE_GENE_XYZ", variant="FAKE_VARIANT_XYZ")
    result = reconcile_record(req)
    assert result.explanation


def test_audit_trail_present_and_non_empty():
    req = ReconcileRequest(cancer_type="NSCLC", gene="HER2", variant="Amplification")
    result = reconcile_record(req)
    assert result.audit_trail
    assert "Confidence score" in " ".join(result.audit_trail)


def test_evidence_has_metadata_fields():
    req = ReconcileRequest(cancer_type="NSCLC", gene="HER2", variant="Amplification")
    result = reconcile_record(req)
    assert result.evidence
    for item in result.evidence:
        assert item.evidence_type
        assert item.retrieval_mode
        assert item.timestamp
        assert item.governance_standard


def test_external_evidence_sources_are_added_for_catalog_matches():
    req = ReconcileRequest(cancer_type="NSCLC", gene="EGFR", variant="Ex19del")
    result = reconcile_record(req)

    sources = {item.source for item in result.evidence}
    assert {"ClinVar", "CIViC", "OncoKB"}.issubset(sources)
    assert "External evidence references added" in " ".join(result.audit_trail)


def test_llm_suggestion_is_review_required_only(monkeypatch):
    def fake_disambiguate(entity_type, input_value, candidates, context):
        return {
            "best_match": "NTRK1 Fusion",
            "confidence": 0.62,
            "rationale": "TRK fusion may map to an NTRK-family fusion.",
            "alternatives_considered": candidates,
            "provider": "test",
        }

    monkeypatch.setattr(reconcile_module.llm, "disambiguate", fake_disambiguate)

    result = reconcile_record(ReconcileRequest(cancer_type="NSCLC", gene="TRK", variant="fusion"))

    assert result.review_status == "REVIEW_REQUIRED"
    assert result.canonical.gene is None
    assert any(item.evidence_type == "llm_suggestion_review_required" for item in result.evidence)
    assert "LLM suggestion added for human review" in " ".join(result.audit_trail)


def test_llm_is_not_called_for_auto_reconcile(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("LLM should not be called for AUTO_RECONCILE")

    monkeypatch.setattr(reconcile_module.llm, "disambiguate", fail_if_called)

    result = reconcile_record(ReconcileRequest(cancer_type="NSCLC", gene="HER2", variant="amp"))

    assert result.review_status == "AUTO_RECONCILE"
    assert not any(item.evidence_type == "llm_suggestion_review_required" for item in result.evidence)


def test_benchmark_endpoint_reports_mvp_metrics():
    response = client.get("/benchmark")
    assert response.status_code == 200
    payload = response.json()

    assert payload["total_cases"] == 156
    assert payload["accuracy"] >= 0.90
    assert payload["coverage"] >= 0.95
    assert "review_rate" in payload
    assert payload["target_status"]["accuracy"] is True
    assert payload["target_status"]["coverage"] is True


def test_review_queue_edit_decision_records_audit_trail():
    reconcile_response = client.post(
        "/reconcile",
        json={"case_id": "review-edit-1", "cancer_type": "NSCLC", "gene": "TRK", "variant": "fusion"},
    )
    assert reconcile_response.status_code == 200

    decision_response = client.post(
        "/review-queue/review-edit-1/decision",
        json={
            "case_id": "review-edit-1",
            "decision": "edit",
            "curator_id": "curator-test",
            "override_canonical": {
                "cancer_type": "Lung Non-Small Cell Carcinoma",
                "gene": "NTRK1",
                "variant": "NTRK1 Fusion",
            },
            "notes": "Edited after human review.",
        },
    )
    assert decision_response.status_code == 200
    item = decision_response.json()["item"]

    assert item["decision"] == "edit"
    assert item["canonical"]["gene"] == "NTRK1"
    assert item["decision_timestamp"]
    assert any("Human review decision: edit" in entry for entry in item["audit_trail"])


def test_review_queue_reopen_moves_item_back_to_pending():
    reconcile_response = client.post(
        "/reconcile",
        json={"case_id": "review-reopen-1", "cancer_type": "NSCLC", "gene": "TRK", "variant": "fusion"},
    )
    assert reconcile_response.status_code == 200

    approve_response = client.post(
        "/review-queue/review-reopen-1/decision",
        json={
            "case_id": "review-reopen-1",
            "decision": "approve",
            "curator_id": "curator-test",
        },
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["item"]["decision"] == "approve"

    reopen_response = client.post(
        "/review-queue/review-reopen-1/decision",
        json={
            "case_id": "review-reopen-1",
            "decision": "reopen",
            "curator_id": "curator-test",
            "notes": "Reopened after curator reconsideration.",
        },
    )
    assert reopen_response.status_code == 200
    item = reopen_response.json()["item"]

    assert item["decision"] is None
    assert any("Human review reopened" in entry for entry in item["audit_trail"])

    pending_response = client.get("/review-queue?status=pending")
    assert pending_response.status_code == 200
    assert any(row["case_id"] == "review-reopen-1" for row in pending_response.json()["items"])
