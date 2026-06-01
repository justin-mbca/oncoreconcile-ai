# Team Kickoff Meeting — June 1, 2026

**Duration:** 90 minutes  
**Format:** Screen share + live demo + live vibe coding session — no slides needed  
**Goal:** Everyone leaves knowing exactly what to build by June 6 (Checkpoint 1) — and has already tried building it

---

## Pre-Meeting (send before the call)

Ask all attendees to read their section in the task plan before joining:

- 📋 [Team Task Plan](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md)
- 🏁 [MVP Definition](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/mvp.md)

---

## Agenda

### 1 — Welcome + Context (5 min)

- What is OncoReconcile AI?
- What is the DFWIT AI & Startup Competition?
- Competition timeline: Checkpoint 1 is **June 6** — 5 days away

📎 [README](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/README.md)

---

### 2 — Live Demo (5 min)

Show the working system:

1. Backend running at `http://127.0.0.1:8000`
2. Frontend running at `http://localhost:5173`
3. Input: `NSCLC` / `HER2` / `Amplification`
4. Output: `ERBB2 Amplification` · `HIGH` · `AUTO_RECONCILE`
5. Show Swagger UI: `http://127.0.0.1:8000/docs`

📎 [Demo Script](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/demo/demo_script.md)  
📎 [API Contract](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/contracts/api_contract.md)

---

### 3 — Repo Walkthrough (5 min)

Quick screen share of repo structure:

| Folder | What's there |
|---|---|
| `backend/app/` | FastAPI app, reconciliation logic, models |
| `frontend/src/` | React UI |
| `data/` | Alias JSON files + benchmark CSV |
| `docs/` | MVP, architecture, team tasks |
| `contracts/` | API contract + examples |

📎 [Repository](https://github.com/justin-mbca/oncoreconcile-ai)  
📎 [Architecture Docs](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/architecture.md)

---

### 4 — Task Assignments (10 min)

Each person has a dedicated section. Walk through together:

| Person | Task Section |
|---|---|
| Nikola | [Nikola: Reconciliation Methods](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#nikola-reconciliation-methods--real-example-data) |
| Rin | [Rin: Data Expansion](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#rin-data-expansion-instructions-mvp) |
| Michael | [Michael: Backend Explainability + QA](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#michael-backend-explainability--quality-tasks) |
| Anne | [Anne: Frontend UI](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#anne-frontend-ui-tasks) |
| Eric | [Eric: Platform Support](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#eric-full-stack-platform-support-tasks-focused) |

📎 [Full Task Plan](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md)  
📎 [Blocker Guidance (Do Now vs. Wait For)](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md#dependency-blockers--what-to-do-now-vs-wait-for)

---

### 5 — Confirm Jun 6 Deliverables (10 min)

Go around the room — each person says:

> "I will deliver **[X]** by **[date]**."

| Person | By Jun 6 |
|---|---|
| Nikola | Expanded test suite (20 benchmark cases); embedding function stub |
| Rin | P0 alias JSON updates (`E545K`, `METex14`, `ALK rearrangement`, etc.) |
| Michael | `backend/app/explain.py` with renderer; explainability eval CSV started |
| Anne | Evidence list rendering in UI; CSV upload UI with mock data |
| Eric | CI workflow file; `frontend/.env.local` config |

---

### 6 — Vibe Coding Session (45 min)

Everyone picks their task and starts building **live during the meeting** using AI-assisted coding (GitHub Copilot, Cursor, ChatGPT, Claude — whatever they prefer).

**Rules:**
- Use AI to generate code — that is expected and encouraged
- Share screen if you want feedback from the group
- Justin and Eric are available to unblock anyone live

**Suggested tasks to start during this session:**

| Person | Start this now |
|---|---|
| Nikola | Open `backend/tests/test_reconcile.py` — add 5 more benchmark test cases using AI |
| Rin | Open `data/variant_aliases.json` — add `E545K`, `METex14`, `ALK rearrangement` entries |
| Michael | Create `backend/app/explain.py` — ask AI to scaffold a `build_explanation()` function |
| Anne | Open `frontend/src/main.jsx` — ask AI to add evidence list rendering below the results table |
| Eric | Ask AI to generate `.github/workflows/backend-ci.yml` for pytest on pull requests |

**Debrief (last 5 min of this block):** Each person shares what they built or ran into.

---

### 7 — Communication + Next Steps (10 min)

- **Anne** sets up Discord server and shares invite tonight
- **Eric** confirms branch protections and project board are set up
- Next async check-in: **June 4 (Thu)** — drop status update in Discord
- If blocked: post in Discord, tag Justin or Eric

📎 [Onboarding Guide](https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/onboarding.md)

---

## What NOT to discuss tonight

- LLM fallback models (deferred to Jun 30)
- Embedding model selection (P1 — after Jun 6)
- Hard benchmark cases (Rin's P1 task — after P0 data is merged)
- Presentation polish or final submission (focus is Checkpoint 1 only)

---

## Quick Reference Links

| Resource | Link |
|---|---|
| Repository | https://github.com/justin-mbca/oncoreconcile-ai |
| Team Task Plan | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/team_tasks.md |
| MVP Definition | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/mvp.md |
| API Contract | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/contracts/api_contract.md |
| Architecture | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/docs/architecture.md |
| Benchmark Data | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/data/nsclc_benchmark.csv |
| Demo Script | https://github.com/justin-mbca/oncoreconcile-ai/blob/main/demo/demo_script.md |
| Swagger UI (local) | http://127.0.0.1:8000/docs |
| Frontend (local) | http://localhost:5173 |
