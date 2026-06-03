"""
Reference test suite — 20 NSCLC benchmark cases.

Owner: Nikola
Branch: nikola/reconcile-tests (branch off vanguard_justin)
Due: June 6, 2026

Instructions:
  - Do NOT change reconcile.py mapping logic in this file.
  - Add/fix tests only. Mark unresolvable cases as xfail with a reason comment.
  - Run: cd backend && PYTHONPATH=. pytest -v
"""

import pytest
from app.models import ReconcileRequest
from app.reconcile import reconcile_record


# ─── EASY CASES ──────────────────────────────────────────────────────────────

def test_case001_egfr_ex19del():
    req = ReconcileRequest(case_id="case_001", cancer_type="NSCLC", gene="EGFR", variant="Ex19del")
    r = reconcile_record(req)
    assert r.canonical.cancer_type == "Non-Small Cell Lung Cancer"
    assert r.canonical.gene == "EGFR"
    assert r.canonical.variant == "EGFR Exon 19 Deletion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case002_egfr_t790m():
    req = ReconcileRequest(case_id="case_002", cancer_type="LUAD", gene="EGFR", variant="T790M")
    r = reconcile_record(req)
    assert r.canonical.cancer_type == "Lung Adenocarcinoma"
    assert r.canonical.gene == "EGFR"
    assert r.canonical.variant == "EGFR p.T790M"
    assert r.review_status == "AUTO_RECONCILE"


def test_case003_kras_g12c():
    req = ReconcileRequest(case_id="case_003", cancer_type="Non-Small Cell Lung Cancer", gene="KRAS", variant="G12C")
    r = reconcile_record(req)
    assert r.canonical.gene == "KRAS"
    assert r.canonical.variant == "KRAS p.G12C"
    assert r.review_status == "AUTO_RECONCILE"


def test_case004_alk_fusion():
    req = ReconcileRequest(case_id="case_004", cancer_type="NSCLC", gene="ALK", variant="Fusion")
    r = reconcile_record(req)
    assert r.canonical.gene == "ALK"
    assert r.canonical.variant == "ALK Fusion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case005_met_exon14():
    req = ReconcileRequest(case_id="case_005", cancer_type="Lung Adenocarcinoma", gene="MET", variant="Exon 14 Skipping")
    r = reconcile_record(req)
    assert r.canonical.gene == "MET"
    assert r.canonical.variant == "MET Exon 14 Skipping"
    assert r.review_status == "AUTO_RECONCILE"


def test_case006_her2_amplification():
    req = ReconcileRequest(case_id="case_006", cancer_type="NSCLC", gene="HER2", variant="Amplification")
    r = reconcile_record(req)
    assert r.canonical.gene == "ERBB2"
    assert r.canonical.variant == "ERBB2 Amplification"
    assert r.review_status == "AUTO_RECONCILE"


def test_case010_egfr_l858r():
    req = ReconcileRequest(case_id="case_010", cancer_type="NSCLC", gene="EGFR", variant="L858R")
    r = reconcile_record(req)
    assert r.canonical.gene == "EGFR"
    assert r.canonical.variant == "EGFR p.L858R"
    assert r.review_status == "AUTO_RECONCILE"


def test_case012_ret_fusion():
    req = ReconcileRequest(case_id="case_012", cancer_type="NSCLC", gene="RET", variant="fusion")
    r = reconcile_record(req)
    assert r.canonical.gene == "RET"
    assert r.canonical.variant == "RET Fusion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case013_braf_v600e():
    req = ReconcileRequest(case_id="case_013", cancer_type="LUAD", gene="BRAF", variant="V600E")
    r = reconcile_record(req)
    assert r.canonical.gene == "BRAF"
    assert r.canonical.variant == "BRAF p.V600E"
    assert r.review_status == "AUTO_RECONCILE"


# ─── MEDIUM CASES ─────────────────────────────────────────────────────────────

def test_case007_her2_hyphen_amp():
    req = ReconcileRequest(case_id="case_007", cancer_type="NSCLC", gene="HER-2", variant="amp")
    r = reconcile_record(req)
    assert r.canonical.gene == "ERBB2"
    assert r.canonical.variant == "ERBB2 Amplification"
    assert r.review_status == "AUTO_RECONCILE"


def test_case008_p53_r175h():
    req = ReconcileRequest(case_id="case_008", cancer_type="LUAD", gene="p53", variant="R175H")
    r = reconcile_record(req)
    assert r.canonical.gene == "TP53"
    assert r.canonical.variant == "TP53 p.R175H"
    assert r.review_status == "AUTO_RECONCILE"


def test_case009_erbb2_exon20ins():
    req = ReconcileRequest(case_id="case_009", cancer_type="NSCLC", gene="ERBB2", variant="exon20ins")
    r = reconcile_record(req)
    assert r.canonical.gene == "ERBB2"
    assert r.canonical.variant == "ERBB2 Exon 20 Insertion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case011_ros1_rearrangement():
    req = ReconcileRequest(case_id="case_011", cancer_type="NSCLC", gene="ROS1", variant="rearrangement")
    r = reconcile_record(req)
    assert r.canonical.gene == "ROS1"
    assert r.canonical.variant == "ROS1 Fusion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case015_egfr_del19():
    req = ReconcileRequest(case_id="case_015", cancer_type="NSCLC", gene="EGFR", variant="del19")
    r = reconcile_record(req)
    assert r.canonical.gene == "EGFR"
    assert r.canonical.variant == "EGFR Exon 19 Deletion"
    assert r.review_status == "AUTO_RECONCILE"


def test_case016_egfr_e746_a750del():
    req = ReconcileRequest(case_id="case_016", cancer_type="NSCLC", gene="EGFR", variant="E746_A750del")
    r = reconcile_record(req)
    assert r.canonical.gene == "EGFR"
    assert r.canonical.variant == "EGFR p.E746_A750del"
    assert r.review_status == "AUTO_RECONCILE"


def test_case017_pik3ca_e545k():
    req = ReconcileRequest(case_id="case_017", cancer_type="NSCLC", gene="PIK3CA", variant="E545K")
    r = reconcile_record(req)
    assert r.canonical.gene == "PIK3CA"
    assert r.canonical.variant == "PIK3CA p.E545K"
    assert r.review_status == "AUTO_RECONCILE"


# ─── DIFFICULT / EDGE CASES ──────────────────────────────────────────────────

def test_case014_ntrk_pan_trk_fusion():
    req = ReconcileRequest(case_id="case_014", cancer_type="NSCLC", gene="NTRK", variant="pan-trk fusion")
    r = reconcile_record(req)
    assert r.canonical.gene == "NTRK"
    assert r.canonical.variant == "NTRK Fusion"


@pytest.mark.xfail(reason="unknown_gene not in alias dict; expected CANNOT_RECONCILE")
def test_case018_unknown_gene():
    req = ReconcileRequest(case_id="case_018", cancer_type="NSCLC", gene="unknown_gene", variant="G12C")
    r = reconcile_record(req)
    assert r.review_status == "CANNOT_RECONCILE"
    assert r.canonical.gene is None


def test_case019_alk_positive():
    req = ReconcileRequest(case_id="case_019", cancer_type="NSCLC", gene="ALK", variant="positive")
    r = reconcile_record(req)
    assert r.canonical.gene == "ALK"
    assert r.canonical.variant == "ALK Alteration"


def test_case020_her2_copy_gain_lung_cancer():
    req = ReconcileRequest(case_id="case_020", cancer_type="lung cancer", gene="HER2", variant="copy gain")
    r = reconcile_record(req)
    assert r.canonical.cancer_type == "Non-Small Cell Lung Cancer"
    assert r.canonical.gene == "ERBB2"
    assert r.canonical.variant == "ERBB2 Copy Number Gain"


# ─── EDGE CASES ───────────────────────────────────────────────────────────────

def test_empty_cancer_type_still_reconciles():
    req = ReconcileRequest(cancer_type=None, gene="HER2", variant="Amplification")
    r = reconcile_record(req)
    assert r.canonical.gene == "ERBB2"
    assert r.canonical.variant == "ERBB2 Amplification"
    assert r.review_status == "AUTO_RECONCILE"


def test_unrecognised_gene_routes_to_cannot_reconcile():
    # All three fields unrecognized → LOW confidence + CANNOT_RECONCILE
    req = ReconcileRequest(cancer_type="FAKE_CANCER_XYZ", gene="FAKE_GENE_XYZ", variant="FAKE_VARIANT_XYZ")
    r = reconcile_record(req)
    assert r.review_status == "CANNOT_RECONCILE"
    assert r.confidence == "LOW"


def test_explanation_always_non_empty():
    req = ReconcileRequest(cancer_type="NSCLC", gene="FAKE_GENE_XYZ", variant="FAKE_VARIANT_XYZ")
    r = reconcile_record(req)
    assert r.explanation
    assert len(r.explanation) > 0


def test_audit_trail_present_and_non_empty():
    req = ReconcileRequest(cancer_type="NSCLC", gene="HER2", variant="Amplification")
    r = reconcile_record(req)
    assert r.audit_trail
    assert len(r.audit_trail) > 0
    assert "Confidence computed" in " ".join(r.audit_trail)


def test_evidence_has_metadata_fields():
    req = ReconcileRequest(cancer_type="NSCLC", gene="HER2", variant="Amplification")
    r = reconcile_record(req)
    assert r.evidence
    for item in r.evidence:
        assert item.evidence_type == "alias_dictionary_match"
        assert item.retrieval_mode == "local_seed_alias"
