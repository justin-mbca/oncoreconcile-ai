import csv
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import ReconcileRequest
from app.reconcile import reconcile_record
from app import reconcile as reconcile_module
from app import external_lookup
from app import review_store


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "data" / "benchmark_cases.csv"
client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_review_queue_and_live_lookup(monkeypatch):
    original_review_queue = (
        review_store.REVIEW_QUEUE_PATH.read_text(encoding="utf-8")
        if review_store.REVIEW_QUEUE_PATH.exists()
        else None
    )
    monkeypatch.setattr(reconcile_module, "lookup_myvariant", lambda gene, variant: [])
    review_store.clear_queue()
    yield
    review_store.clear_queue()
    if original_review_queue is None:
        review_store.REVIEW_QUEUE_PATH.unlink(missing_ok=True)
    else:
        review_store.REVIEW_QUEUE_PATH.write_text(original_review_queue, encoding="utf-8")
    review_store._store.clear()
    review_store._load_store()


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
    assert len(rows) == 161
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


def test_local_catalog_gene_with_scoped_variant_auto_reconciles():
    req = ReconcileRequest(cancer_type="Breast Cancer", gene="PIK3CA", variant="E545K")
    result = reconcile_record(req)

    assert result.review_status == "AUTO_RECONCILE"
    assert result.confidence == "HIGH"
    assert result.canonical.cancer_type == "Breast Invasive Carcinoma"
    assert result.canonical.gene == "PIK3CA"
    assert result.canonical.variant == "PIK3CA E545K"
    assert any(item.evidence_type == "local_gene_catalog_match" for item in result.evidence)


def test_cross_context_variant_candidate_routes_to_human_review():
    req = ReconcileRequest(cancer_type="NSCLC", gene="PIK3CA", variant="E545K")
    result = reconcile_record(req)

    assert result.review_status == "REVIEW_REQUIRED"
    assert result.confidence == "MEDIUM"
    assert result.canonical.cancer_type == "Lung Non-Small Cell Carcinoma"
    assert result.canonical.gene == "PIK3CA"
    assert result.canonical.variant == "PIK3CA E545K"
    assert any(item.evidence_type == "local_gene_catalog_candidate" for item in result.evidence)
    assert any(item.evidence_type == "external_candidate_evidence" for item in result.evidence)
    assert "External candidate fallback requires human review" in " ".join(result.audit_trail)


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


def test_myvariant_lookup_success_returns_evidence(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "hits": [
                    {
                        "_id": "chr7:g.55181378A>T",
                        "clinvar": {"rcv": []},
                        "dbsnp": {"rsid": "rs123"},
                    }
                ]
            }

    monkeypatch.setattr(external_lookup.httpx, "get", lambda *args, **kwargs: FakeResponse())

    evidence = external_lookup.lookup_myvariant("EGFR", "C797S")

    assert len(evidence) == 1
    assert evidence[0]["source"] == "MyVariant.info"
    assert evidence[0]["evidence_type"] == "external_lookup"
    assert evidence[0]["retrieval_mode"] == "live_myvariant_api"
    assert evidence[0]["external_id"] == "chr7:g.55181378A>T"


def test_myvariant_lookup_failure_returns_error_evidence(monkeypatch):
    def fail_request(*args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(external_lookup.httpx, "get", fail_request)

    evidence = external_lookup.lookup_myvariant("EGFR", "C797S")

    assert len(evidence) == 1
    assert evidence[0]["evidence_type"] == "external_lookup_error"
    assert evidence[0]["retrieval_mode"] == "live_myvariant_api_error"
    assert "network unavailable" in evidence[0]["description"]


def test_unknown_local_variant_triggers_myvariant_lookup(monkeypatch):
    def fake_lookup(gene, variant):
        return [{
            "source": "MyVariant.info",
            "type": "external_variant_lookup",
            "description": f"External evidence candidate found for {gene} {variant}.",
            "evidence_type": "external_lookup",
            "confidence_weight": "LOW",
            "retrieval_mode": "live_myvariant_api",
            "external_id": "myvariant:EGFR-C797S",
            "timestamp": "2026-06-17T00:00:00+00:00",
        }]

    monkeypatch.setattr(reconcile_module, "external_variant_candidate_lookup", lambda gene, variant: [])
    monkeypatch.setattr(reconcile_module, "lookup_myvariant", fake_lookup)

    result = reconcile_record(ReconcileRequest(cancer_type="NSCLC", gene="EGFR", variant="C797S"))

    assert result.review_status == "REVIEW_REQUIRED"
    assert any(item.retrieval_mode == "live_myvariant_api" for item in result.evidence)
    assert "Live MyVariant lookup started" in " ".join(result.audit_trail)
    assert "Live MyVariant lookup completed: 1 evidence item(s)" in " ".join(result.audit_trail)


def test_external_evidence_turns_cannot_reconcile_into_review_required(monkeypatch):
    def fake_lookup(gene, variant):
        return [{
            "source": "MyVariant.info",
            "type": "external_variant_lookup",
            "description": f"External evidence candidate found for {gene} {variant}.",
            "evidence_type": "external_lookup",
            "confidence_weight": "LOW",
            "retrieval_mode": "live_myvariant_api",
            "external_id": "myvariant:unknown",
            "timestamp": "2026-06-17T00:00:00+00:00",
        }]

    monkeypatch.setattr(reconcile_module, "external_variant_candidate_lookup", lambda gene, variant: [])
    monkeypatch.setattr(reconcile_module, "lookup_myvariant", fake_lookup)

    response = client.post(
        "/reconcile",
        json={"case_id": "myvariant-review-1", "cancer_type": "NSCLC", "gene": "unknown_gene", "variant": "C797S"},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["review_status"] == "REVIEW_REQUIRED"
    assert any(item["retrieval_mode"] == "live_myvariant_api" for item in payload["evidence"])
    assert "Live external evidence found; routed to human review" in " ".join(payload["audit_trail"])

    persisted = json.loads(review_store.REVIEW_QUEUE_PATH.read_text(encoding="utf-8"))
    assert any(item["case_id"] == "myvariant-review-1" for item in persisted["items"])


def test_auto_reconcile_does_not_run_myvariant_lookup(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("AUTO_RECONCILE should not call live MyVariant lookup")

    monkeypatch.setattr(reconcile_module, "lookup_myvariant", fail_if_called)

    result = reconcile_record(ReconcileRequest(cancer_type="NSCLC", gene="EGFR", variant="Ex19del"))

    assert result.review_status == "AUTO_RECONCILE"
    assert not any(item.retrieval_mode == "live_myvariant_api" for item in result.evidence)


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

    assert payload["total_cases"] == 161
    assert payload["accuracy"] >= 0.90
    assert payload["coverage"] >= 0.95
    assert "review_rate" in payload
    assert payload["target_status"]["accuracy"] is True
    assert payload["target_status"]["coverage"] is True
    assert payload["counts"]["total_records"] == 161
    assert "candidate_evidence_cases" in payload["counts"]
    assert "approved_review_cases" in payload["counts"]


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


def test_review_queue_items_and_decisions_are_persisted_to_file():
    reconcile_response = client.post(
        "/reconcile",
        json={"case_id": "persist-review-1", "cancer_type": "AML", "gene": "IDH2", "variant": "R172K"},
    )
    assert reconcile_response.status_code == 200
    assert reconcile_response.json()["review_status"] == "REVIEW_REQUIRED"

    persisted = json.loads(review_store.REVIEW_QUEUE_PATH.read_text(encoding="utf-8"))
    persisted_item = next(item for item in persisted["items"] if item["case_id"] == "persist-review-1")
    assert persisted_item["canonical"]["variant"] == "IDH2 R172K"
    assert persisted_item["decision"] is None

    decision_response = client.post(
        "/review-queue/persist-review-1/decision",
        json={
            "case_id": "persist-review-1",
            "decision": "approve",
            "curator_id": "curator-test",
            "notes": "Approved after curator review.",
        },
    )
    assert decision_response.status_code == 200

    persisted = json.loads(review_store.REVIEW_QUEUE_PATH.read_text(encoding="utf-8"))
    persisted_item = next(item for item in persisted["items"] if item["case_id"] == "persist-review-1")
    assert persisted_item["decision"] == "approve"
    assert persisted_item["curator_id"] == "curator-test"
    assert persisted_item["created_at"]
    assert persisted_item["updated_at"]
    assert any("Human review decision: approve" in entry for entry in persisted_item["audit_trail"])


def test_review_queue_uses_stable_key_and_avoids_duplicates():
    payload = {"cancer_type": "AML", "gene": "IDH2", "variant": "R172K"}

    first = client.post("/reconcile", json=payload)
    second = client.post("/reconcile", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    queue = client.get("/review-queue?status=all").json()
    assert queue["total"] == 1
    assert queue["items"][0]["case_id"].startswith("review-")


def test_promote_to_catalog_is_an_explicit_disabled_stub():
    client.post(
        "/reconcile",
        json={"case_id": "promote-stub-1", "cancer_type": "AML", "gene": "IDH2", "variant": "R172K"},
    )

    response = client.post("/review-queue/promote-stub-1/promote")

    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"
    assert "do not modify" in response.json()["message"].lower()


def test_standards_alignment_endpoint_is_explicitly_non_compliant():
    response = client.get("/standards/alignment")

    assert response.status_code == 200
    payload = response.json()
    assert payload["product_positioning"] == "AI-assisted oncology curation and harmonization"
    assert "AI-Assisted Curation" in payload["aligned_use_cases"]
    assert "not an official GA4GH compliant implementation" in payload["disclaimer"]


def test_provenance_export_accepts_original_case_input():
    response = client.post(
        "/export/provenance",
        json={"cancer_type": "NSCLC", "gene": "HER2", "variant": "amp"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "PROV-O-inspired"
    assert payload["entity"]["canonical"]["gene"] == "ERBB2"
    assert payload["activity"]["name"] == "oncology_entity_reconciliation"
    assert payload["generated_at"]


def test_export_endpoints_accept_an_existing_reconciliation_result():
    reconciliation = client.post(
        "/reconcile",
        json={"cancer_type": "NSCLC", "gene": "HER2", "variant": "amp"},
    ).json()

    response = client.post("/export/provenance", json=reconciliation)

    assert response.status_code == 200
    assert response.json()["entity"]["canonical"]["gene"] == "ERBB2"


def test_vrs_ready_export_is_clearly_a_stub():
    response = client.post(
        "/export/vrs-ready",
        json={"cancer_type": "NSCLC", "gene": "EGFR", "variant": "Ex19del"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "VRS-ready-stub"
    assert payload["variant"] == "EGFR Exon 19 Deletion"
    assert "not an official GA4GH VRS object" in payload["note"]


def test_cat_vrs_ready_export_preserves_ntrk_ambiguity():
    response = client.post(
        "/export/cat-vrs-ready",
        json={"cancer_type": "NSCLC", "gene": "TRK", "variant": "fusion"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "Cat-VRS-ready-stub"
    assert payload["ambiguity_preserved"] is True
    assert set(payload["members"][:3]) == {
        "NTRK1 Fusion",
        "NTRK2 Fusion",
        "NTRK3 Fusion",
    }


def test_va_spec_ready_export_contains_evidence_and_provenance():
    response = client.post(
        "/export/va-spec-ready",
        json={"cancer_type": "NSCLC", "gene": "EGFR", "variant": "C797S"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "VA-Spec-ready-stub"
    assert payload["review_status"] == "REVIEW_REQUIRED"
    assert payload["evidence"]
    assert payload["provenance"]["type"] == "PROV-O-inspired"


def test_reconciliation_output_includes_curation_metadata():
    response = client.post(
        "/reconcile",
        json={"cancer_type": "NSCLC", "gene": "HER2", "variant": "amp"},
    )

    assert response.status_code == 200
    metadata = response.json()["curation_metadata"]
    assert metadata["curation_stage"] == "harmonize"
    assert metadata["human_governance_required"] is False
    assert metadata["catalog_promotion_candidate"] is False


def test_review_candidate_curation_metadata_requires_governance_and_promotion_review():
    response = client.post(
        "/reconcile",
        json={"cancer_type": "NSCLC", "gene": "EGFR", "variant": "C797S"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_status"] == "REVIEW_REQUIRED"
    assert payload["curation_metadata"]["human_governance_required"] is True
    assert payload["curation_metadata"]["catalog_promotion_candidate"] is True


def test_curation_report_combines_result_provenance_and_standards_stubs():
    response = client.post(
        "/curation/report",
        json={"case_id": "curation-report-1", "cancer_type": "NSCLC", "gene": "EGFR", "variant": "C797S"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reconciliation_result"]["review_status"] == "REVIEW_REQUIRED"
    assert payload["provenance_export"]["type"] == "PROV-O-inspired"
    assert payload["standards_ready_exports"]["vrs_ready"]["type"] == "VRS-ready-stub"
    assert payload["standards_ready_exports"]["cat_vrs_ready"]["type"] == "Cat-VRS-ready-stub"
    assert payload["standards_ready_exports"]["va_spec_ready"]["type"] == "VA-Spec-ready-stub"
    assert payload["governance_summary"]["requires_human_review"] is True
    assert payload["governance_summary"]["candidate_for_catalog_promotion"] is True


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
