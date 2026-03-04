"""
Apollo.io Prospecting Script for LFG.run
Searches for founders & small business owners, then enriches to get emails.
"""

from typing import Optional
import requests
import json
import time
import csv
from datetime import datetime

API_KEY = "0yOvt8uylPgwfbFu-dmTRw"
SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
ENRICH_URL = "https://api.apollo.io/api/v1/people/match"

HEADERS = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "x-api-key": API_KEY,
}

# --- Ideal Customer Profiles ---
SEARCH_PROFILES = [
    {
        "name": "Non-Technical Startup Founders (Seed/Series A)",
        "params": {
            "person_titles": ["founder", "co-founder", "ceo"],
            "organization_num_employees_ranges": ["1,10", "11,50"],
            "person_locations": ["United States"],
            "organization_latest_funding_stage_cd": ["seed", "pre_seed", "angel", "series_a"],
            "per_page": 25,
            "page": 1,
        },
    },
    {
        "name": "Solo Founders & CEOs - Small Tech Companies",
        "params": {
            "person_titles": ["founder", "ceo", "owner"],
            "organization_num_employees_ranges": ["1,10"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": ["saas", "software", "technology", "app", "platform"],
            "per_page": 25,
            "page": 1,
        },
    },
    {
        "name": "Founders in Vertical SaaS (Healthcare, Legal, Real Estate, Fintech)",
        "params": {
            "person_titles": ["founder", "co-founder", "ceo"],
            "organization_num_employees_ranges": ["1,10", "11,50"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": [
                "healthtech", "healthcare", "legaltech", "legal",
                "proptech", "real estate", "fintech", "finance",
            ],
            "per_page": 25,
            "page": 1,
        },
    },
    {
        "name": "Small Business Owners Going Digital (E-commerce, Services, Marketplaces)",
        "params": {
            "person_titles": ["founder", "owner", "ceo", "managing director"],
            "organization_num_employees_ranges": ["1,10", "11,50"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": [
                "ecommerce", "marketplace", "services", "agency",
                "consulting", "small business",
            ],
            "per_page": 25,
            "page": 1,
        },
    },
    {
        "name": "Heads of Product at Early-Stage Startups",
        "params": {
            "person_titles": ["head of product", "vp product", "director of product", "cpo"],
            "organization_num_employees_ranges": ["1,10", "11,50", "51,100"],
            "person_locations": ["United States"],
            "organization_latest_funding_stage_cd": ["seed", "pre_seed", "angel", "series_a"],
            "per_page": 25,
            "page": 1,
        },
    },
]


def search_people(params: dict) -> list:
    """Search Apollo for people matching the given filters."""
    resp = requests.post(SEARCH_URL, headers=HEADERS, json=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("people", [])


def enrich_person(person: dict) -> Optional[dict]:
    """Enrich a person record to get their email address."""
    payload = {
        "id": person.get("id"),
        "first_name": person.get("first_name"),
        "last_name": person.get("last_name"),
        "organization_name": person.get("organization", {}).get("name") if person.get("organization") else None,
        "reveal_personal_emails": True,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    resp = requests.post(ENRICH_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get("person")


def main():
    all_prospects = []
    seen_ids = set()

    for profile in SEARCH_PROFILES:
        print(f"\n{'='*60}")
        print(f"Searching: {profile['name']}")
        print(f"{'='*60}")

        try:
            people = search_people(profile["params"])
            print(f"  Found {len(people)} people")

            for person in people:
                pid = person.get("id")
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)

                name = person.get("name", "N/A")
                title = person.get("title", "N/A")
                org = person.get("organization", {})
                org_name = org.get("name", "N/A") if org else "N/A"

                # Check if email came back in search results directly
                email = person.get("email")

                if not email:
                    # Enrich to get email
                    try:
                        enriched = enrich_person(person)
                        if enriched:
                            email = enriched.get("email")
                        time.sleep(0.3)  # rate limit
                    except Exception as e:
                        print(f"    Enrich failed for {name}: {e}")

                if email:
                    prospect = {
                        "name": name,
                        "email": email,
                        "title": title,
                        "company": org_name,
                        "profile": profile["name"],
                    }
                    all_prospects.append(prospect)
                    print(f"    ✓ {name} ({title} @ {org_name}) — {email}")
                else:
                    print(f"    ✗ {name} — no email found")

        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(1)  # pause between profile searches

    # --- Write results to CSV ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prospects_{timestamp}.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "title", "company", "profile"])
        writer.writeheader()
        writer.writerows(all_prospects)

    print(f"\n{'='*60}")
    print(f"DONE — {len(all_prospects)} emails collected")
    print(f"Saved to: {filename}")
    print(f"{'='*60}")

    # Also print just the emails
    print("\n--- Emails Only ---")
    for p in all_prospects:
        print(p["email"])


if __name__ == "__main__":
    main()
