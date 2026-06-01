# Task-Driven Team Plan

This team uses task-driven ownership instead of rigid roles.

Each person can use AI/vibe coding, but every task must produce a visible deliverable.

---

## Suggested Ownership

| Area | Suggested Owner | Deliverable | Availability |
|---|---|---|---|
| Architecture + contracts | Justin | MVP, API contract, architecture docs | Lead |
| Reconciliation rules + Backend API | Nikola | reconciliation logic, FastAPI endpoint, alias dictionaries | Active |
| Frontend UI | Anne | upload page and results table — AI-assisted; data analytics + DB background, learning frontend | Active — also setting up Discord for team comms |
| Backend Explainability + QA | Michael | backend explanation renderer, confidence-language rules, explainability tests, evaluation dataset | Active |
| Platform/GitHub + PM | Eric | repo structure, Docker, CI, GitHub board, issue management; full-stack capable for unblocking | Busy — focused tasks only |
| Benchmark dataset | Rin | 20 NSCLC cases (✅ completed per instructions) | Busy — dataset done, limited going forward |
| Backend (limited support) + Deferred LLM Fallback | Hao | async backend support when available; evaluate **LLM fallback layer** for hard/unmatched cases (only after deterministic pipeline is stable), target start **Jun 30, 2026** | Busy (travel); LLM task starts no earlier than Jun 30, 2026 |
| Customer validation (side support) | Wei | async notes and interview feedback only — no meeting obligation; minimum **1 structured feedback note/week** | Side support only |

---

## Dependency Blockers — What to Do Now vs. Wait For

Each person has a **do-now track** (unblocked work they can start today) and a **wait-for track** (work that needs something else first).

---

### Nikola

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| Rin's new alias data not merged yet | Improving reconciliation coverage for `E545K`, `METex14`, etc. | Write expanded unit tests for all 20 benchmark cases using **existing** alias data; mark expected-fail cases as `xfail` with a comment | Rin's PR is merged → remove `xfail`, run tests green |
| Embedding model not installed | P1 embedding similarity work | Write the embedding function **stub** with a clear interface; return `None` until model is loaded | Michael or Nikola installs `sentence-transformers` in `requirements.txt` |

**Do now:** Expand `test_reconcile.py` to 20 cases. Stub embedding layer interface. Both are fully unblocked.

---

### Rin

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| Needs to know canonical string format exactly | Adding new aliases without drift | Open [data/nsclc_benchmark.csv](data/nsclc_benchmark.csv) — column `expected_variant` is the exact canonical string to use in every JSON value | — no wait needed; benchmark file is the source of truth |
| Hard-case file needs design agreement | `nsclc_hard_cases.csv` creation | Start with P0 JSON alias updates only (`E545K`, `METex14`, `ALK rearrangement`) — no design agreement needed for JSON | Hard-case schema is confirmed (columns already defined in this doc) |

**Do now:** P0 JSON alias additions. Fully unblocked.

---

### Michael

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| Nikola still editing `reconcile.py` mapping logic | Explanation renderer edits in same file | Build explanation renderer as a **separate function** `build_explanation(evidence, confidence)` in a new file `backend/app/explain.py`; import it from `reconcile.py` later | Nikola's mapping PR is merged → wire `explain.py` into `reconcile_record()` |
| Need real output samples to build eval CSV | `explainability_eval.csv` population | Run the existing backend locally (`uvicorn app.main:app`) and POST the 20 benchmark cases manually to collect real output samples | — no wait; backend runs today |

**Do now:** Create `backend/app/explain.py` with renderer logic. Run backend locally to generate eval CSV rows. Both fully unblocked.

---

### Anne

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| API URL is hardcoded — needs Eric's env config | Full local dev setup | Use hardcoded URL temporarily; add a `TODO` comment at line 19 of `main.jsx` | Eric adds env config → replace with `import.meta.env.VITE_API_BASE_URL` |
| Batch endpoint behavior needs Nikola/Eric to confirm payload | CSV upload + batch results table | Build the CSV parse and UI table first with **mock data** (`const mockResult = [...]`); swap in real API call once batch is confirmed | Nikola/Eric post a sample batch response in Discord |
| Backend evidence list content may change | Evidence rendering in UI | Render `result.evidence` as a simple list today — it already works with current backend; just not rendered yet | — no wait needed; evidence is already returned by the API |

**Do now:** Add evidence list rendering (no blocker). Build CSV UI with mock data. Both fully unblocked.

---

### Eric

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| Anne is still building CSV UI | Frontend pairing on batch flow | Set up CI workflow file (`.github/workflows/backend-ci.yml`) — fully unblocked | Anne signals she is ready to wire the batch API call |
| Backend is still evolving | Full env config hardening | Create `frontend/.env.local` and update `main.jsx` line 19 — small change, fully independent | — no wait needed |

**Do now:** Create CI workflow. Add `frontend/.env.local`. Both fully unblocked.

---

### Hao

| Blocker | Blocked task | Do now instead | Come back when |
|---|---|---|---|
| Travel + deterministic pipeline not yet stable | LLM fallback implementation | Nothing assigned until Jun 30, 2026 — **no action needed now** | Returns from trip AND Nikola's P0+P1 reconciliation is stable |

---

### Dependency-first execution order

1. **Rin P0 data update** (variant aliases) — unblocked now
2. **Nikola test expansion + embedding stub** — unblocked now, data improvement follows Rin's PR
3. **Michael `explain.py` creation + eval CSV** — unblocked now, wiring follows Nikola's PR
4. **Anne evidence rendering + CSV UI with mock** — unblocked now, batch wiring follows Nikola/Eric confirmation
5. **Eric CI + env config** — unblocked now, full pairing follows Anne's readiness
6. **Hao LLM fallback** — deferred to Jun 30, 2026

---

## Nikola: Reconciliation Methods + Real Example Data

### Code entry points

- [backend/app/reconcile.py](backend/app/reconcile.py) — all reconciliation logic lives here
  - `normalize_cancer_type()` — cancer alias lookup
  - `normalize_gene()` — gene alias lookup
  - `normalize_variant()` — variant alias lookup with `{gene}` template substitution
  - `get_confidence()` — confidence scoring logic
  - `get_review_status()` — review status logic
  - `reconcile_record()` — main entry point called by the API
- [backend/app/models.py](backend/app/models.py) — request/response schema (`ReconcileRequest`, `ReconcileResponse`)
- [backend/tests/test_reconcile.py](backend/tests/test_reconcile.py) — existing 2 tests; expand to cover all 20 benchmark cases
- [data/nsclc_benchmark.csv](data/nsclc_benchmark.csv) — 20 benchmark cases with expected outputs to test against
- [data/variant_aliases.json](data/variant_aliases.json), [data/gene_aliases.json](data/gene_aliases.json), [data/cancer_aliases.json](data/cancer_aliases.json) — alias dictionaries loaded at startup

Use this table to prioritize implementation work for reconciliation.

| Priority | Method to Explore | Real Example Input | Expected Canonical Output | Notes |
|---|---|---|---|---|
| P0 | Alias dictionary exact match | `HER2` + `Amplification` | `ERBB2 Amplification` | Already aligned with current deterministic MVP pipeline |
| P0 | Alias dictionary exact match | `p53` + `R175H` | `TP53 p.R175H` | Gene alias + variant shorthand |
| P0 | Rule template with gene context | `ERBB2` + `exon20ins` | `ERBB2 Exon 20 Insertion` | Use template-style variant normalization |
| P1 | Cancer type fuzzy normalization (RapidFuzz) | `lung cancer` | `Non-Small Cell Lung Cancer` | Only for cancer type free-text normalization |
| P1 | Embedding similarity (biomedical model) | `pan-trk fusion` | `NTRK Fusion` | Benchmark case_014 (difficult); semantic synonym handling |
| P1 | Embedding similarity (biomedical model) | `rearrangement` with gene `ROS1` | `ROS1 Fusion` | Benchmark case_011; clinical synonym mapping |
| P2 | LLM fallback (deferred; owned by Hao after trip) after deterministic + embedding fail | `unknown_gene` + `G12C` | low-confidence suggestion or unresolved | Must return LOW confidence and require human review |

Recommended models for Nikola (embedding experiments):

- `pritamdeka/S-PubMedBert-MS-MARCO`
- `dmis-lab/biobert-base-cased-v1.2`

Success criteria for Nikola experiments:

- Improve difficult benchmark reconciliation while preserving deterministic behavior for easy/medium cases
- Do not downgrade precision on gene/variant canonical outputs that already reconcile correctly
- Keep final review gating: MEDIUM/LOW must remain human-governed

---

## Rin: Data Expansion Instructions (MVP)

Rin can continue with data tasks using this exact checklist.

### File entry points

- [data/variant_aliases.json](data/variant_aliases.json) — JSON key/value map, `"input_term": "Canonical Output"`. Edit directly in any text editor or VS Code.
- [data/gene_aliases.json](data/gene_aliases.json) — same format; maps gene aliases to HGNC canonical symbols
- [data/cancer_aliases.json](data/cancer_aliases.json) — same format; maps cancer type aliases to canonical disease names
- [data/nsclc_benchmark.csv](data/nsclc_benchmark.csv) — **reference file**; do not edit; use this to know what canonical values must match exactly
- New file to create: [data/nsclc_hard_cases.csv](data/nsclc_hard_cases.csv) — follow same column structure as benchmark CSV
- New file to create: [data/evidence_map.csv](data/evidence_map.csv) — trace every alias to its source

### How to validate your changes

1. Open [data/nsclc_benchmark.csv](data/nsclc_benchmark.csv)
2. For every alias you add to a JSON file, check that the canonical value in your JSON **exactly matches** the `expected_*` column in the benchmark
3. Check for duplicate keys in JSON files (each input term must appear only once)
4. Run `python3 -c "import json; json.load(open('data/variant_aliases.json'))"` from repo root to verify JSON is valid

### Goal

Increase deterministic reconciliation coverage for easy/medium cases and provide clean evaluation data for difficult cases.

### Deliverables (exact files)

1. Update [data/variant_aliases.json](data/variant_aliases.json)
2. Update [data/gene_aliases.json](data/gene_aliases.json)
3. Update [data/cancer_aliases.json](data/cancer_aliases.json)
4. Create [data/nsclc_hard_cases.csv](data/nsclc_hard_cases.csv)
5. Create [data/evidence_map.csv](data/evidence_map.csv)

### What to add (minimum required)

#### A) Variant aliases (highest priority)

Add entries missing from benchmark-driven expectations, including:

- `E545K` -> `PIK3CA p.E545K` (required to cover benchmark case_017)
- `PIK3CA E545K` -> `PIK3CA p.E545K`
- `EGFR exon 19 deletion` -> `EGFR Exon 19 Deletion`
- `EGFR exon19del` -> `EGFR Exon 19 Deletion`
- `METex14` -> `MET Exon 14 Skipping`
- `MET exon14 skipping` -> `MET Exon 14 Skipping`
- `ALK rearrangement` -> `ALK Fusion`
- `ROS1 translocation` -> `ROS1 Fusion`

#### B) Gene aliases (priority 2)

Add common spellings/case/noise variants:

- `erbB2` -> `ERBB2`
- `ERB-B2` -> `ERBB2`
- `trk` -> `NTRK`
- `c-met` -> `MET`

#### C) Cancer type aliases (priority 2)

Add common clinic text forms:

- `non small cell lung cancer` -> `Non-Small Cell Lung Cancer`
- `nsclc adenocarcinoma` -> `Lung Adenocarcinoma`
- `lung adeno ca` -> `Lung Adenocarcinoma`

### New hard-case file format

For [data/nsclc_hard_cases.csv](data/nsclc_hard_cases.csv), use columns:

`case_id,cancer_type,gene,variant,expected_cancer_type,expected_gene,expected_variant,difficulty,why_hard`

Add at least 15 rows with real messy values (abbreviations, typos, synonym phrases, ambiguous terms).

Example rows:

- `hard_001,non small cell lung ca,HER-2,copy number gain,Non-Small Cell Lung Cancer,ERBB2,ERBB2 Copy Number Gain,DIFFICULT,spacing+hyphen+synonym`
- `hard_002,LUAD,p53,Arg175His,Lung Adenocarcinoma,TP53,TP53 p.R175H,DIFFICULT,protein longform`
- `hard_003,NSCLC,ROS1,translocation,Non-Small Cell Lung Cancer,ROS1,ROS1 Fusion,DIFFICULT,synonym to fusion`

### Evidence mapping file format

For [data/evidence_map.csv](data/evidence_map.csv), use columns:

`input_term,canonical_term,entity_type,source,source_id,evidence_note`

Example rows:

- `HER2,ERBB2,gene,HGNC,HGNC:3430,Approved symbol mapping`
- `p53,TP53,gene,HGNC,HGNC:11998,Approved symbol mapping`
- `Ex19del,EGFR Exon 19 Deletion,variant,Seed Knowledge Base,SKB-VAR-001,Canonical exon-19 deletion phrase`

### Quality rules (must follow)

- No duplicate keys in JSON files
- Keep canonical values exactly as used by backend outputs (same case/spelling)
- Every new alias should have at least one evidence row in `evidence_map.csv`
- Validate CSV has no empty required fields

### Done criteria for Rin

- Benchmark case_017 reconciles to `PIK3CA p.E545K`
- At least 15 hard cases added and reviewed
- Evidence rows added for all newly added aliases

---

## Anne: Frontend UI Tasks

### Code entry points

- [frontend/src/main.jsx](frontend/src/main.jsx) — the entire React app is in this one file
  - `form` state (lines 6-10) — holds `cancer_type`, `gene`, `variant` input values
  - `submitRecord()` function (lines 15-38) — sends `POST /reconcile` and stores response in `result`
  - API URL **hardcoded** as `http://127.0.0.1:8000/reconcile` (line 19) — move to `import.meta.env.VITE_API_BASE_URL`
  - Results table (lines 76-100) — currently renders `canonical`, `confidence`, `review_status`, `explanation` only
  - **Missing:** `evidence` list is NOT rendered — needs to be added
  - **Missing:** CSV upload and batch flow — not yet implemented
- [frontend/src/style.css](frontend/src/style.css) — all styles live here
- [frontend/vite.config.js](frontend/vite.config.js) — Vite + React plugin config
- [frontend/package.json](frontend/package.json) — dependencies (`react`, `vite`, `@vitejs/plugin-react`)
- [contracts/api_contract.md](contracts/api_contract.md) — **read this first** to understand all response fields Anne must render
- [contracts/output.example.json](contracts/output.example.json) — paste this into the browser console to test UI rendering

### Task scope for Anne (priority order)

#### P0 — Evidence list rendering

- In the result section of `main.jsx`, add an evidence list below the table:
  - `result.evidence` is an array of objects: `{ source, type, description }`
  - Render each as a bullet: `{item.source}: {item.description}`

#### P0 — Environment-based API URL

- Replace `http://127.0.0.1:8000` with `import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'`
- Create `frontend/.env.local` with `VITE_API_BASE_URL=http://127.0.0.1:8000`

#### P1 — CSV upload + batch flow

- Add a file input (`<input type="file" accept=".csv" />`) in a new card section
- On file select, parse CSV rows using `FileReader` + `split('\n')`
- Map each row to `{ cancer_type, gene, variant }` objects
- Send as `POST /reconcile/batch` with body `{ records: [...] }`
- Render results in a table with one row per record

#### P1 — Confidence + review status color coding

- `HIGH` / `AUTO_RECONCILE` → green badge
- `MEDIUM` / `REVIEW_REQUIRED` → yellow badge
- `LOW` / `CANNOT_RECONCILE` → red badge

### Done criteria for Anne

- Manual single-record input renders all fields including evidence list
- CSV upload sends batch request and renders results table
- API URL is env-based, not hardcoded
- Error and loading states display cleanly

---

## Michael: Backend Explainability + Quality Tasks

Michael can contribute in these concrete areas beyond prompt/model evaluation.

### Deliverables (exact files)

1. Update [docs/prompts/explainability_prompt.md](docs/prompts/explainability_prompt.md)
2. Update [backend/app/reconcile.py](backend/app/reconcile.py) explanation/notes generation paths
3. Create [backend/tests/test_explainability.py](backend/tests/test_explainability.py)
4. Create [data/explainability_eval.csv](data/explainability_eval.csv)

### Code entry points

- [backend/app/reconcile.py](backend/app/reconcile.py) — explanation is generated inside `reconcile_record()` function
  - Look for the `explanation` field construction near the bottom of the function (after evidence is built)
  - This is where the renderer logic should be added/replaced
- [backend/app/models.py](backend/app/models.py) — `ReconcileResponse.explanation` is a plain `str`; `confidence` and `review_status` are plain `str` (can be hardened to `Literal` types)
- [backend/tests/test_reconcile.py](backend/tests/test_reconcile.py) — existing test file; add `test_explainability.py` alongside it
- [docs/prompts/explainability_prompt.md](docs/prompts/explainability_prompt.md) — existing prompt template to extend

### Task Scope

#### 1) Explanation style guide + templates

- Define 4 explanation templates in [docs/prompts/explainability_prompt.md](docs/prompts/explainability_prompt.md):
	- exact alias match
	- context-based variant mapping
	- low-confidence suggestion
	- cannot reconcile
- Ensure outputs avoid treatment/clinical recommendation language.

#### 2) Evidence-to-text renderer

- Implement a deterministic renderer in [backend/app/reconcile.py](backend/app/reconcile.py) that converts `evidence` + `notes` into concise explanation text.
- Keep explanation length target: 1-3 sentences.

#### 3) Confidence-language consistency

- Add wording guardrails:
	- `HIGH`: definitive language allowed ("recognized alias", "mapped directly")
	- `MEDIUM`: cautious language ("likely", "requires review")
	- `LOW`: uncertainty language ("possible match", "manual review required")

#### 4) Explainability test coverage

- Add tests in [backend/tests/test_explainability.py](backend/tests/test_explainability.py):
	- explanation present and non-empty
	- no prohibited terms (`treatment`, `therapy`, `recommend`, `drug`)
	- confidence-specific wording appears for `HIGH`, `MEDIUM`, `LOW`
	- `CANNOT_RECONCILE` includes explicit manual-review statement

#### 5) Human evaluation set

- Build [data/explainability_eval.csv](data/explainability_eval.csv) with columns:
	- `case_id,input_gene,input_variant,canonical_gene,canonical_variant,confidence,explanation,clarity_1to5,faithfulness_1to5,needs_edit`
- Seed at least 20 rows from benchmark outputs for quick reviewer scoring.

### Done criteria for Michael

- Explanations are deterministic and consistent with confidence/review status
- Explainability tests pass in CI
- Evaluation CSV created and ready for clinician/data-team review

---

## Eric: Full-Stack Platform Support Tasks (Focused)

Eric should stay in platform ownership and take targeted unblocker tasks across backend + frontend.

### Core platform ownership (must keep)

- GitHub project board hygiene (priority labels, assignees, due dates)
- PR quality gates (required checks, review rules, branch protection)
- Docker/dev runbook stability for team onboarding

### Code entry points

- [backend/app/main.py](backend/app/main.py) — hardcoded CORS origins list (lines 14–22); replace with env-based config
- [frontend/src/main.jsx](frontend/src/main.jsx) — API URL hardcoded as `http://127.0.0.1:8000`; move to `import.meta.env.VITE_API_BASE_URL`
- [frontend/vite.config.js](frontend/vite.config.js) — Vite config; add `envPrefix` or proxy config here for env support
- [backend/requirements.txt](backend/requirements.txt) — add `python-dotenv` if env file loading needed in backend
- CI setup: create `.github/workflows/backend-ci.yml` with `pytest` command using `backend/.venv`

### Backend support tasks (time-boxed)

1. Add environment-based API config support for local/dev
	- Ensure backend and frontend use configurable base URLs and ports
2. Add structured API error envelope consistency
	- Keep response format stable for frontend consumption
3. Add/maintain CI test command for backend
	- Verify unit tests run on pull requests

### Frontend support tasks for Anne (pairing)

1. API integration hardening
	- Help Anne switch to environment-based API endpoint handling
2. Result rendering completion
	- Ensure confidence, review status, evidence, and explanation render cleanly
3. CSV flow support
	- Assist with file upload parse + batch request wiring to backend

### Recommended execution split (low overhead)

- 70% platform/PM guardrails
- 20% frontend pairing with Anne
- 10% backend unblockers only

### Done criteria for Eric

- CI and branch protections are active and documented
- Anne can run frontend against backend without manual URL edits
- One full batch flow (CSV -> `/reconcile/batch` -> UI table) works end-to-end

---

## Current Sprint Tasks

### Task 1: API Contract

Deliverables:

- `contracts/api_contract.md`
- `contracts/input.example.json`
- `contracts/output.example.json`

Due: Tuesday

---

### Task 2: Benchmark Dataset

Deliverable:

- `data/nsclc_benchmark.csv`

Due: Wednesday

---

### Task 3: Alias Dictionaries

Deliverables:

- `data/cancer_aliases.json`
- `data/gene_aliases.json`
- `data/variant_aliases.json`

Due: Thursday

---

### Task 4: Backend Endpoint

Deliverable:

- `POST /reconcile`

Due: Thursday

---

### Task 5: Frontend Input Page

Deliverable:

- manual input or CSV upload page

Due: Friday

---

### Task 6: Result Display

Deliverable:

- result table or JSON display

Due: Sunday

---

### Task 7: Explainability

Deliverable:

- explanation text for each result

Due: Sunday

---

### Task 8: Weekly Demo

Deliverable:

- one complete record through the pipeline

Due: Sunday

---

## Competition Milestone Plan (May 16 - Jul 18, 2026)

Official milestones:

- Checkpoint 1: **Jun 6, 2026**
- Checkpoint 2: **Jun 27, 2026**
- Final Submission: **Jul 11, 2026**
- Final Presentation (if selected): **~Jul 18, 2026**

### Reasonable task list by person

| Owner | By Checkpoint 1 (Jun 6) | By Checkpoint 2 (Jun 27) | By Final Submission (Jul 11) |
|---|---|---|---|
| Justin (Lead) | Freeze MVP scope + API contract v1; approve task owners and dependency order | Lock judging narrative, architecture diagram, and risk log | Final technical review, submission package sign-off, presentation story approval |
| Nikola (Backend reconciliation) | Deterministic reconciliation stable for benchmark easy/medium; endpoint reliability | Add prioritized improvements (fuzzy for cancer type + selected embedding experiments for hard cases) without breaking deterministic path | Final backend stability, edge-case handling, benchmark pass report |
| Rin (Data) | Deliver P0 alias updates (`E545K` and high-value variants) + evidence rows | Deliver hard-case dataset and expanded alias coverage with QA cleanup | Final data freeze, provenance cleanup, handoff notes for judges/demo |
| Michael (Backend explainability + QA) | Deterministic explanation templates and confidence-language rules drafted | Explainability tests in CI + evaluation sheet scored for quality | Final explainability polish for demo cases and reviewer-ready examples |
| Anne (Frontend) | Manual input + single-result rendering (canonical/confidence/review) | Batch CSV upload + results table + evidence/explanation display | Demo-ready UX polish, error/loading states, stable end-to-end flow |
| Eric (Platform/PM/full-stack support) | CI baseline, branch protections, project board discipline; unblock Anne API integration | Environment config hardening, batch flow reliability, release checklist | Final release hardening, demo runbook, rollback/fix playbook |
| Hao (Limited backend support + deferred LLM fallback) | Async code review on backend PRs as available (if bandwidth) | LLM fallback design note + model shortlist by **Jun 30, 2026** (post-checkpoint workstream) | Optional LLM fallback integration for hard/unmatched cases with LOW confidence + REVIEW_REQUIRED by **Jul 8, 2026** |
| Wei (Side support) | Submit **3 structured feedback notes** (template-based) by Jun 6 | Submit **1 synthesis memo** (top 5 usability issues + recommendations) by Jun 27 | Submit **final validation summary** (top 10 insights + 3 demo quotes) by Jul 11 |

### Weekly cadence to stay on track

- **Mon-Tue:** build + data updates
- **Wed:** integration checkpoint (backend/frontend/data)
- **Thu:** bugfix + test hardening
- **Fri:** demo rehearsal + issue triage
- **Weekend (light):** backup buffer only for critical blockers

### Scope guardrails (important)

- Before Jun 6: prioritize deterministic MVP completion over new model experimentation
- Jun 7-Jun 27: controlled improvements only if benchmark and demo path remain stable
- LLM fallback is explicitly deprioritized for Checkpoint 1 and Checkpoint 2; earliest start is **Jun 30, 2026** after core pipeline stability review
- After Jun 27: feature freeze bias; focus on quality, reliability, and presentation clarity
