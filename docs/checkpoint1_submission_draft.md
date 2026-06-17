# Checkpoint 1 Submission Draft

**Target Submission Date:** June 6, 2026  
**Prepared by:** Justin (Lead)  
**Status:** DRAFT — team deliverables due June 6

---

## Executive Summary

OncoReconcile AI is a human-governed oncology reconciliation workbench that transforms messy cancer types, genes, and variants into trusted canonical oncology concepts. 

**Checkpoint 1 deliverable:** Working MVP with deterministic reconciliation pipeline, foundational frontend, and QA-validated test suite (20+ benchmark cases).

---

## Deliverables Checklist

### Backend (Nikola + Michael)

**Parallel split to avoid conflicts (agreed):**

| Backend slice | Primary owner | File(s) |
|---|---|---|
| Deterministic reconciliation logic + benchmark tests | Nikola | `backend/app/reconcile.py`, `backend/tests/test_reconcile.py` |
| Explanation renderer + explainability QA | Michael | `backend/app/explain.py`, eval CSV |
| Final integration call (`reconcile_record()` -> `build_explanation(...)`) | Nikola (or Michael in a tiny isolated PR) | `backend/app/reconcile.py` |

**Handoff contract:** `build_explanation(method, confidence, review_status, evidence)` returns deterministic text and must never fail API response generation.

- [ ] **Deterministic reconciliation stable** — all easy/medium benchmark cases passing
  - **Proof:** `backend/tests/test_reconcile.py` with 20+ test cases from NSCLC benchmark
  - **Entry point:** `backend/app/reconcile.py` — `reconcile_record()` function
  - **Status on Jun 1:** 2 tests passing; 18 benchmark cases awaiting implementation
  
- [ ] **Explanation templates drafted** — confidence and review status rules finalized
  - **Proof:** `backend/app/explain.py` — `build_explanation()` function with rules per confidence level
  - **Status on Jun 1:** Not started; scaffolded by Michael this week

- [ ] **API contract frozen** — `/reconcile` and `/reconcile/batch` endpoints documented and working
  - **Proof:** [API Contract](../contracts/api_contract.md) + Swagger UI at `http://127.0.0.1:8000/docs`
  - **Example request:** `{ "cancer_type": "NSCLC", "gene": "HER2", "variant": "Amplification" }`
  - **Example response:** `{ "canonical_cancer_type": "Non-Small Cell Lung Cancer", "canonical_gene": "ERBB2", "canonical_variant": "Amplification", "confidence": "HIGH", "review_status": "AUTO_RECONCILE" }`
  - **Status on Jun 1:** Defined and working (2 test cases verified)

- [ ] **Endpoint reliability** — error handling, edge cases, CORS working
  - **Tests:** `backend/tests/test_reconcile.py` includes edge cases (None, empty string, typo variants)
  - **Status on Jun 1:** Basic CORS enabled; needs comprehensive edge case coverage

### Data (Rin + Wei)

- [ ] **P0 alias JSON updates** — essential variants added to `data/variant_aliases.json`
  - **Priority variants:** `E545K`, `METex14`, `ALK rearrangement`, `BRAF V600E`, `MSI-H`
  - **Evidence rows:** Each entry includes source (ClinVar, OncoKB, custom), confidence, and notes
  - **Status on Jun 1:** Variants not yet added; need P0 list finalized
  - **Proof:** Updated `data/variant_aliases.json` with 10+ entries

- [ ] **Cancer type alias cleanup** — all TCGA + NCI synonyms in `data/cancer_aliases.json`
  - **Status on Jun 1:** File exists; needs review against standard oncology reference
  - **Proof:** `data/cancer_aliases.json` with 50+ mappings (NSCLC, LUAD, SCLC, etc.)

- [ ] **Wei's validation feedback** — 3 structured feedback notes submitted
  - **Template:** Date, use case tested, 2-3 key findings, 1-2 blockers (if any)
  - **Status on Jun 1:** Not submitted; due by June 6
  - **Proof:** `docs/checkpoint1_feedback_notes.md` with 3 dated entries

### Frontend (Anne + Eric)

- [ ] **Manual input form + result display** — user can input cancer type/gene/variant and see canonical output
  - **Proof:** `frontend/src/main.jsx` — form component + results table
  - **Fields displayed:** Canonical name, confidence (HIGH/MEDIUM/LOW), review status (AUTO_RECONCILE/REVIEW_REQUIRED/CANNOT_RECONCILE), explanation
  - **Status on Jun 1:** Form and results table working; evidence list not yet rendered
  - **URL:** `http://localhost:5173`

- [ ] **Evidence rendering** — confidence score explanation with sources
  - **Proof:** Results table includes evidence column linking to alias source and confidence justification
  - **Status on Jun 1:** Not yet rendered; Anne's task this week
  - **Example:** "HIGH confidence from alias dictionary (ClinVar source)"

- [ ] **CSV upload stub** — UI mock for batch reconciliation (optional for Checkpoint 1 if time)
  - **Status on Jun 1:** Not started; Anne's P1 after evidence rendering
  - **Proof:** `frontend/src/components/CsvUpload.jsx` with file picker + mock results table

- [ ] **Environment config** — `.env.local` hardened, API URL parameterized
  - **Proof:** `frontend/.env.local` with `VITE_API_BASE_URL=http://127.0.0.1:8000` (dev) and production URL
  - **Status on Jun 1:** Not yet created; Eric's task this week
  - **CI check:** Frontend build passes on GitHub Actions

### Platform / DevOps (Eric)

- [ ] **CI baseline** — GitHub Actions workflow runs pytest on backend PRs
  - **Proof:** `.github/workflows/backend-ci.yml` runs `pytest backend/tests/test_reconcile.py` on push to main + PRs
  - **Status on Jun 1:** Not yet created; Eric's P0 task
  - **Requirement:** All Checkpoint 1 PRs must pass CI before merge

- [ ] **Branch protections** — main branch requires CI passing + 1 review
  - **Status on Jun 1:** Needs configuration via GitHub; Eric's task
  - **Proof:** GitHub repo settings screenshot

- [ ] **Project board discipline** — all Checkpoint 1 tasks tracked with Jun 6 deadline
  - **Status on Jun 1:** Not yet set up; Eric to configure
  - **Proof:** GitHub Project board with 5 columns (Backlog, In Progress, In Review, Testing, Done)

---

## Benchmark Validation

**Target:** 80%+ pass rate on NSCLC benchmark (20 easy/medium cases) by Jun 6.

**Dataset:** `data/nsclc_benchmark.csv` — 30 real-world reconciliation cases (10 easy, 10 medium, 10 hard)

### Easy Cases (should all pass by Jun 6)

| Case ID | Cancer Type | Gene | Variant | Expected Canonical | Method |
|---|---|---|---|---|---|
| E001 | NSCLC | HER2 | Amplification | Non-Small Cell Lung Cancer / ERBB2 / Amplification | Alias |
| E002 | Lung Cancer | TP53 | R175H | Lung Cancer / TP53 / R175H | Alias + fuzzy |
| E003 | LUAD | EGFR | Ex19del | Lung Adenocarcinoma / EGFR / Exon 19 Deletion | Alias + normalize |

**Current status:** 2/3 passing (E001, E002)

### Medium Cases (target 80%+ by Jun 6)

| Case ID | Cancer Type | Gene | Variant | Challenge | Method |
|---|---|---|---|---|---|
| M001 | Adenocarcinoma | EGFR | Exon 19 deletion | Free-text variance in variant naming | Fuzzy + pattern match |
| M002 | LUAD | ERBB2 | Gene amplification | Gene synonym + generic variant | Alias + embedding (P1 task) |
| M003 | NSCLC NOS | MET | Exon 14 skipping | Space + abbreviation variance | Fuzzy |

**Current status:** 0/3 implemented; Nikola to expand test suite this week

### Hard Cases (defer to Checkpoint 2)

| Case ID | Cancer Type | Gene | Variant | Challenge | Method |
|---|---|---|---|---|---|
| H001 | Squamous | KRAS | G12C mutation | Free-text free form | LLM fallback (Jun 30+) |
| H002 | Small cell | Unknown | Biomarker signature | Entity resolution | LLM + embedding (Jun 30+) |

**Checkpoint 1 approach:** Document that hard cases route to REVIEW_REQUIRED + LOW confidence, with LLM fallback deferred.

---

## Documentation Package

Submission includes:

1. **[README.md](../README.md)** — One-sentence pitch, problem, MVP scope, how to run
2. **[API Contract](../contracts/api_contract.md)** — Request/response schemas + examples
3. **[Architecture](../docs/architecture.md)** — System design, reconciliation pipeline, confidence/review rules
4. **[MVP Definition](../docs/mvp.md)** — Scope, inputs, outputs, confidence matrix, review status matrix
5. **[Team Tasks](../docs/team_tasks.md)** — Ownership, tasks, blockers, milestone plan
6. **[Onboarding Guide](../docs/onboarding.md)** — How to build, run, test, deploy
7. **[Meeting Agenda (Jun 1)](../docs/meeting_agenda_jun1.md)** — Team kickoff + task alignment

### Quick-Start Instructions

**For judges to run the demo:**

```bash
# Terminal 1: Backend
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Browser: http://localhost:5173
# Try: cancer_type=NSCLC, gene=HER2, variant=Amplification
```

---

## Confidence & Review Rules (Checkpoint 1)

| Method | Confidence | Review Status | Explanation |
|---|---|---|---|
| **Alias dict lookup** | HIGH | AUTO_RECONCILE | Exact match in curated alias dictionary (source: ClinVar, OncoKB, custom) |
| **Fuzzy matching** | MEDIUM | AUTO_RECONCILE | Pattern-match within cancer type name or variant description (e.g., "Ex19del" → "Exon 19 Deletion") |
| **No match** | LOW | CANNOT_RECONCILE | No deterministic or fuzzy match found; requires manual review or LLM fallback (deferred to Jun 30) |

**Note:** Embedding-based matching (ML) is scheduled for Checkpoint 2. LLM fallback deferred to Jun 30+ per scope guardrails.

---

## Risk & Mitigation

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Test suite incomplete (18 benchmark cases pending) | Medium | Nikola + Michael complete 20-case suite by Jun 4; run full suite Jun 5 | Nikola |
| P0 alias data not finalized | Medium | Rin finalizes 10-case variant list by Jun 3; update JSON by Jun 5 | Rin |
| Frontend evidence rendering not done | Low-Medium | Anne prioritizes rendering this week; can defer CSV upload to Checkpoint 2 | Anne |
| CI/branch protections not configured | Low | Eric sets up workflow by Jun 3; test on PR before Jun 5 | Eric |
| Wei's feedback not submitted | Low | Wei submits 3 notes async by Jun 6 EOD | Wei |

**Contingency:** If any blocker emerges, Justin to reassign tasks or negotiate scope with judges by Jun 5 11:59 PM.

---

## Success Criteria

By **June 6, 2026, 11:59 PM UTC:**

- ✅ Backend: 20 benchmark test cases run; ≥16/20 passing (80%+)
- ✅ Frontend: Manual input form + results display working; evidence rendering complete
- ✅ Data: P0 alias updates merged; 10+ new variant entries in `variant_aliases.json`
- ✅ Platform: CI baseline configured; branch protections active
- ✅ Docs: All markdown files reviewed + links verified
- ✅ Demo: End-to-end flow (input → canonical output) works on judges' machines

---

## Checkpoint 1 vs. Beyond

### In Checkpoint 1 ✅

- Deterministic alias-based reconciliation (HIGH confidence)
- Fuzzy matching for cancer type (MEDIUM confidence)
- Manual UI input + results display
- 20-case benchmark validation
- Evidence and explainability templates
- Platform basics (CI, branch protections)

### Deferred to Checkpoint 2 (Jun 27)

- Embedding-based matching (ML, MEDIUM confidence)
- CSV batch upload + results export
- Full evidence display with source links
- Hard benchmark cases (H001-H010)

### Deferred to Final Submission (Jul 11) + Post-Submission

- LLM fallback (LOW confidence) — **earliest start Jun 30, 2026**
- Performance optimization
- Deployment & hosting
- Presentation materials

---

## Commit Log (in progress)

As of June 1, 2026:

- `04afcc7` — Extend agenda to 90 min with vibe coding session
- `1320d52` — Update MVP confidence and review rules to clarify fuzzy, ML, and LLM methods
- `9a7ac8b` — Add do-now vs wait-for blocker guidance for each team member
- `1a2d331` — Add Jun 1 kickoff meeting agenda with links
- `f611d50` — Add comprehensive team task plan for Checkpoint 1

**By Jun 6:** Expect 15-20 additional commits as team completes deliverables.

---

## Next Checkpoint (Jun 27)

At Checkpoint 2, we will:

- Add embedding-based reconciliation (MEDIUM confidence tier)
- Implement CSV batch upload + export
- Expand test suite to all 30 benchmark cases
- Add hard-case handling strategy (route to REVIEW_REQUIRED + mark for Jun 30 LLM work)
- Refine explainability with source attribution
- Hardening for production demo

---

## Approval

- [ ] **Justin (Lead)** — MVP scope frozen, team ready, submission package approved by Jun 6 EOD
- [ ] **Nikola (Backend)** — Reconciliation pipeline passing 80%+ benchmarks by Jun 6 EOD
- [ ] **Rin (Data)** — P0 aliases finalized and merged by Jun 6 EOD
- [ ] **Michael (Backend explainability)** — Explanation rules drafted and tested by Jun 6 EOD
- [ ] **Anne (Frontend)** — Manual input + results display + evidence rendering complete by Jun 6 EOD
- [ ] **Eric (Platform)** — CI and branch protections active by Jun 6 EOD

---

**Last updated:** June 1, 2026, 11:00 PM UTC  
**Next review:** June 4, 2026 (team async check-in before final push)
