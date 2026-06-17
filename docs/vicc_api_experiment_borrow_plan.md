# VICC API Experiment Borrow Plan (for `vanguard`)

## Purpose

This document identifies which ideas/code patterns from branch `vicc-api-experiment` are worth borrowing into `vanguard` without disrupting Checkpoint 1 scope.

**Goal:** Borrow only low-risk, high-value pieces for reconciliation workflow, evidence, and explainability.

---

## Branches Compared

- Target branch: `vanguard`
- Reference branch: `vicc-api-experiment`

---

## Executive Decision

### Safe to borrow now (Checkpoint 1)

1. **Deterministic explanation templates** for matched vs unresolved outputs
2. **Structured evidence metadata pattern** (source/type/confidence weight)
3. **Simple audit trail list** (steps performed during reconciliation)
4. **Fallback wording** for "normalized but weak evidence" vs "cannot reconcile"

### Do not borrow now (Checkpoint 1)

1. Full `src/` architecture from `vicc-api-experiment`
2. VICC/ClinVar/CIViC connector stack and async orchestration
3. New API schema contracts that conflict with current FastAPI response shape
4. Agent/workflow pipeline and related tests

These are **Checkpoint 2+** candidates only.

---

## Borrow Candidates (Detailed)

| Priority | Borrow candidate | Source in `vicc-api-experiment` | Where to apply in `vanguard` | Why useful now |
|---|---|---|---|---|
| P0 | Explanation-state wording (`normalized_with_evidence`, `normalized_without_external_evidence`, `unresolved`) | `src/services/reconciliation_service.py` | `backend/app/explain.py` (new), then called from `backend/app/reconcile.py` | Gives Michael ready-made explainability states tied to confidence/review |
| P0 | Evidence object conventions (`source`, `evidence_type`, `confidence_weight`) | `src/services/evidence/provider_router.py`, `src/services/evidence_resolution_service.py` | `backend/app/models.py` (`EvidenceItem`) + evidence assembly in `backend/app/reconcile.py` | Improves transparency with minimal code changes |
| P0 | Audit trail as ordered list of decisions | `src/services/reconciliation_service.py` | Add optional `audit_trail` in response model and append deterministic processing steps in `reconcile_record()` | Helps judge-facing explainability and debugging |
| P1 | Canonical schema naming ideas (`requires_human_review`, `cannot_reconcile`) | `src/reconciliation_schema.py` | Keep current `review_status`, but optionally add derived booleans for frontend simplicity | Good UX/API clarity; not required for Jun 6 |
| P2 | Multi-source evidence fallback (ClinVar/CIViC) | `src/services/evidence_resolution_service.py` | Future connector module after deterministic MVP is stable | Too much dependency risk for Checkpoint 1 |

---

## Task Ownership Mapping

| Team member | Related task | Borrowed item(s) they should use |
|---|---|---|
| **Michael** | Backend explainability + QA | Explanation-state templates, fallback wording, optional `audit_trail` construction |
| **Nikola** | Reconciliation logic + tests | Evidence metadata shape in `EvidenceItem`, optional `audit_trail` population, integrate `build_explanation()` |
| **Anne** | Frontend evidence/explanation rendering | Use richer `evidence` fields and display explanation + review state clearly |
| **Eric** | Platform/CI + integration support | Ensure tests pass after model changes; enforce schema consistency in CI |
| **Justin** | Scope governance | Keep borrow set minimal to avoid architecture drift before Jun 6 |

---

## Practical Implementation Plan (Jun 1 - Jun 6)

### Step 1 (Michael) — `backend/app/explain.py`

Create `build_explanation(method, confidence, review_status, evidence)` with deterministic templates:

- Alias/evidence present -> concise high-confidence explanation
- Partial/medium confidence -> normalized but recommend review
- No match -> cannot reconcile + human review required

### Step 2 (Nikola) — `backend/app/reconcile.py`

- Keep current normalization logic unchanged
- Call `build_explanation(...)`
- Add basic `audit_trail` entries (e.g., alias lookup attempted, variant synonym matched, no match)

### Step 3 (Nikola + Michael) — `backend/app/models.py`

- Extend `EvidenceItem` only if needed (`evidence_type`, `confidence_weight`)
- Add `audit_trail` field to response model as optional list
- Preserve backward compatibility for existing frontend fields

### Step 4 (Anne)

Render in UI:

- `explanation`
- `evidence` list with source/type
- (if added) short `audit_trail` expandable section

### Step 5 (Eric)

- Run/guard backend tests in CI
- Ensure schema changes do not break existing API contract expectations

---

## Out of Scope Before Jun 6

The following should **not** be merged into `vanguard` before Checkpoint 1:

- Replacing current `backend/app/*` with `src/*` architecture
- Bringing in VICC live API dependency stack
- Migrating to new request/response contracts used in `vicc-api-experiment`
- Introducing agent orchestration pipeline

---

## Merge Safety Rules

1. Keep deterministic reconciliation as the source of truth.
2. Borrow patterns, not whole subsystems.
3. Every borrowed change must be covered by test updates.
4. Preserve current endpoint contract for frontend stability.

---

## Acceptance Criteria

This borrow plan is successful if by Jun 6:

- Explanation text is deterministic and consistent
- Evidence payload is clearer than current baseline
- Optional audit trail exists without breaking frontend
- No architecture migration occurs
- Benchmark progress and API stability are preserved

---

## Related Files (Current Branch)

- `backend/app/reconcile.py`
- `backend/app/models.py`
- `backend/tests/test_reconcile.py`
- `frontend/src/main.jsx`
- `docs/team_tasks.md`
- `docs/checkpoint1_submission_draft.md`
