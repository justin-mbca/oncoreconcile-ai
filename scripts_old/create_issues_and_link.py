#!/usr/bin/env python3
import csv
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List

# ========= CONFIG =========
OWNER = "oncoreconcile-ai"
REPO = "oncoreconcile-ai"
PROJECT_NUMBER = 1  # <-- set your shared vanguard project number
CSV_FILE = "issues.csv"
AUTO_CREATE_MISSING_LABELS = True
# ==========================

# CSV columns:
# title,body,labels,assignees,milestone
# labels/assignees use semicolon separators, e.g. "task;backend"

LABEL_COLORS = {
    "task": "0e8a16",
    "backend": "5319e7",
    "frontend": "1d76db",
    "platform": "0052cc",
    "data": "fbca04",
}


def run(cmd: List[str], check: bool = True) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and p.returncode != 0:
        raise RuntimeError(
            f"ERROR running:\n  {' '.join(shlex.quote(c) for c in cmd)}\n{p.stderr.strip()}"
        )
    return p.stdout.strip()


def ensure_tools():
    run(["gh", "--version"])
    auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
    if auth.returncode != 0:
        print("GitHub CLI not authenticated. Run: gh auth login", file=sys.stderr)
        sys.exit(1)


def split_semicolon(value: str) -> List[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(";") if x.strip()]


def get_existing_labels() -> set[str]:
    output = run([
        "gh", "label", "list",
        "--repo", f"{OWNER}/{REPO}",
        "--json", "name",
        "--limit", "1000",
    ])
    labels = json.loads(output)
    return {item["name"] for item in labels}


def ensure_labels_exist(labels: set[str]):
    if not labels:
        return

    existing = get_existing_labels()
    missing = sorted(labels - existing)

    if not missing:
        return

    if not AUTO_CREATE_MISSING_LABELS:
        raise RuntimeError(
            "Missing labels in repository: " + ", ".join(missing)
        )

    for label in missing:
        color = LABEL_COLORS.get(label.lower(), "d4c5f9")
        run([
            "gh", "label", "create", label,
            "--repo", f"{OWNER}/{REPO}",
            "--color", color,
            "--description", f"Auto-created by issue automation script ({label})",
        ])
        print(f"[INFO] Created missing label: {label}")


def collect_all_labels(csv_path: Path) -> set[str]:
    labels: set[str] = set()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for label in split_semicolon(row.get("labels", "")):
                labels.add(label)
    return labels


def create_issue(row: dict) -> str:
    title = (row.get("title") or "").strip()
    if not title:
        raise ValueError("Missing required 'title' field in CSV row.")

    body = (row.get("body") or "").strip()
    labels = split_semicolon(row.get("labels", ""))
    assignees = split_semicolon(row.get("assignees", ""))
    milestone = (row.get("milestone") or "").strip()

    cmd = [
        "gh", "issue", "create",
        "--repo", f"{OWNER}/{REPO}",
        "--title", title,
        "--body", body if body else "No description provided."
    ]

    for label in labels:
        cmd += ["--label", label]

    for assignee in assignees:
        cmd += ["--assignee", assignee]

    if milestone:
        cmd += ["--milestone", milestone]

    issue_url = run(cmd)
    return issue_url


def link_to_project(issue_url: str):
    run([
        "gh", "project", "item-add",
        str(PROJECT_NUMBER),
        "--owner", OWNER,
        "--url", issue_url
    ])


def main():
    try:
        ensure_tools()

        csv_path = Path(CSV_FILE)
        if not csv_path.exists():
            print(f"CSV file not found: {CSV_FILE}", file=sys.stderr)
            sys.exit(1)

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            required_cols = {"title", "body", "labels", "assignees", "milestone"}
            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                print(f"Missing CSV columns: {', '.join(sorted(missing))}", file=sys.stderr)
                sys.exit(1)

        ensure_labels_exist(collect_all_labels(csv_path))

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            count = 0
            for i, row in enumerate(reader, start=2):  # line 1 is header
                try:
                    issue_url = create_issue(row)
                    link_to_project(issue_url)
                    print(f"[OK] Row {i}: {issue_url}")
                    count += 1
                except (RuntimeError, ValueError) as e:
                    print(f"[FAIL] Row {i}: {e}", file=sys.stderr)

        print(f"\nDone. Created+linked {count} issue(s).")
    except (RuntimeError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()