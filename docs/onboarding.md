# Team Onboarding Guide

Welcome to OncoReconcile AI.

This guide helps every team member start contributing quickly.

---

## Step 1: Understand the MVP

Read:

1. `README.md`
2. `docs/mvp.md`
3. `docs/architecture.md`
4. `contracts/api_contract.md`

---

## Step 2: Pick a Task

Use GitHub Issues.

Good first tasks:

- Add benchmark cases
- Add gene aliases
- Improve API contract examples
- Build upload page
- Build reconcile endpoint
- Add explanation examples
- Write tests

---

## Step 3: Create a Branch

Use task-based branch names:

```bash
git checkout -b feature/nsclc-dataset
git checkout -b feature/reconcile-api
git checkout -b feature/upload-ui
```

Do not commit directly to `main`.

---

## Step 4: Use Vibe Coding Carefully

AI tools can help generate code, but always check:

- Does it match the API contract?
- Does it run?
- Is it small enough to review?
- Did you test it?

Backend setup note:

Use Python 3.10, 3.11, or 3.12 for the backend virtual environment.
Do not use Python 3.14 with the current pinned dependencies; it can fail while
building `pydantic-core` because the bundled PyO3 version supports Python only
through 3.13.

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Step 5: Submit a Pull Request

Every PR should include:

```text
What changed?
How did you test it?
Screenshot or sample output if applicable.
What issue does it close?
```

---

## Step 6: Ask for Help Early

If blocked for more than 48 hours, post:

```text
Blocked by:
What I tried:
What I need:
```

---

## Team Rule

Do not wait for Justin to make every decision.

If the decision is small, make it, document it in `docs/decisions.md`, and keep moving.
