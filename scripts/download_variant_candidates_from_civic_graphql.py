import csv
import os
import time
from pathlib import Path

import requests


DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = RAW_DIR / "civic_variant_candidates.csv"

CIVIC_GRAPHQL_URL = "https://civicdb.org/api/graphql"

TARGET_GENES = [
    "EGFR", "ERBB2", "TP53", "KRAS", "BRAF", "MET",
    "ALK", "ROS1", "RET", "NTRK1", "NTRK2", "NTRK3"
]

MAX_PAGES = 20
PAGE_SIZE = 100

QUERY = """
query AcceptedEvidence($first: Int!, $after: String) {
  evidenceItems(status: ACCEPTED, first: $first, after: $after) {
    totalCount
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      id
      evidenceType
      evidenceLevel
      evidenceRating
      evidenceDirection
      disease {
        name
      }
      molecularProfile {
        id
        name
        link
        variants {
          id
          name
          link
        }
      }
    }
  }
}
"""


def headers() -> dict:
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    api_key = os.environ.get("CIVIC_API_KEY")
    if api_key:
        h["Authorization"] = f"Bearer {api_key}"
    return h


def civic_query(after=None) -> dict:
    response = requests.post(
        CIVIC_GRAPHQL_URL,
        headers=headers(),
        json={
            "query": QUERY,
            "variables": {
                "first": PAGE_SIZE,
                "after": after,
            },
        },
        timeout=60,
    )

    print(f"HTTP {response.status_code}")
    response.raise_for_status()
    data = response.json()

    if data.get("errors"):
        print("[WARN] GraphQL errors:")
        for err in data["errors"]:
            print(err)

    return data


def infer_gene_from_text(text: str) -> str:
    text_upper = text.upper()
    for gene in TARGET_GENES:
        if gene in text_upper:
            return gene
    return ""


def rows_from_response(data: dict) -> tuple[list[dict], str, bool]:
    rows = []

    evidence_items = data.get("data", {}).get("evidenceItems", {})
    nodes = evidence_items.get("nodes", [])
    page_info = evidence_items.get("pageInfo", {}) or {}

    for item in nodes:
        disease = item.get("disease") or {}
        molecular_profile = item.get("molecularProfile") or {}

        mp_name = molecular_profile.get("name", "") or ""
        mp_link = molecular_profile.get("link", "") or ""
        variants = molecular_profile.get("variants") or []

        gene = infer_gene_from_text(mp_name)
        if not gene:
            continue

        if not variants:
            rows.append({
                "source": "CIViC GraphQL",
                "query_gene": gene,
                "disease": disease.get("name", ""),
                "molecular_profile": mp_name,
                "variant_name": "",
                "variant_link": "",
                "evidence_item_id": item.get("id", ""),
                "evidence_type": item.get("evidenceType", ""),
                "evidence_level": item.get("evidenceLevel", ""),
                "evidence_rating": item.get("evidenceRating", ""),
                "evidence_direction": item.get("evidenceDirection", ""),
                "molecular_profile_link": mp_link,
                "curation_status": "CANDIDATE_REVIEW_REQUIRED",
                "notes": "Downloaded candidate; review before adding to curated catalog."
            })
        else:
            for variant in variants:
                rows.append({
                    "source": "CIViC GraphQL",
                    "query_gene": gene,
                    "disease": disease.get("name", ""),
                    "molecular_profile": mp_name,
                    "variant_name": variant.get("name", ""),
                    "variant_link": variant.get("link", ""),
                    "evidence_item_id": item.get("id", ""),
                    "evidence_type": item.get("evidenceType", ""),
                    "evidence_level": item.get("evidenceLevel", ""),
                    "evidence_rating": item.get("evidenceRating", ""),
                    "evidence_direction": item.get("evidenceDirection", ""),
                    "molecular_profile_link": mp_link,
                    "curation_status": "CANDIDATE_REVIEW_REQUIRED",
                    "notes": "Downloaded candidate; review before adding to curated catalog."
                })

    return rows, page_info.get("endCursor"), bool(page_info.get("hasNextPage"))


def write_csv(rows: list[dict]) -> None:
    fieldnames = [
        "source",
        "query_gene",
        "disease",
        "molecular_profile",
        "variant_name",
        "variant_link",
        "evidence_item_id",
        "evidence_type",
        "evidence_level",
        "evidence_rating",
        "evidence_direction",
        "molecular_profile_link",
        "curation_status",
        "notes",
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("Downloading accepted CIViC evidence and filtering target genes...")
    print(f"Output: {OUT_CSV.resolve()}")

    all_rows = []
    after = None

    for page in range(1, MAX_PAGES + 1):
        print(f"Page {page}")

        data = civic_query(after=after)
        rows, after, has_next = rows_from_response(data)

        print(f"Rows matched this page: {len(rows)}")
        all_rows.extend(rows)

        if not has_next:
            break

        time.sleep(0.5)

    write_csv(all_rows)

    print("Done.")
    print(f"Rows written: {len(all_rows)}")
    print(f"File: {OUT_CSV}")


if __name__ == "__main__":
    main()