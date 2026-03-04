"""
Smartlead Campaign Setup Script
Creates campaigns with A/B variants, imports leads from prospect CSVs.
"""

import requests
import csv
import time
import json

API_KEY = "b8b7caf3-b1a3-4bc9-b324-79f0b68d7b3a_mm53xw7"
BASE_URL = "https://server.smartlead.ai/api/v1"


def api(method, path, body=None):
    url = f"{BASE_URL}{path}"
    params = {"api_key": API_KEY}
    if method == "POST":
        resp = requests.post(url, params=params, json=body)
    else:
        resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def create_campaign(name):
    data = api("POST", "/campaigns/create", {"name": name})
    print(f"  Created campaign: {data.get('name')} (ID: {data.get('id')})")
    return data["id"]


def add_sequences(campaign_id, sequences):
    data = api("POST", f"/campaigns/{campaign_id}/sequences", {"sequences": sequences})
    print(f"  Added {len(sequences)} sequence steps")
    return data


def add_leads(campaign_id, leads, batch_size=100):
    total = 0
    for i in range(0, len(leads), batch_size):
        batch = leads[i : i + batch_size]
        body = {
            "lead_list": batch,
            "settings": {
                "ignore_global_block_list": False,
                "ignore_unsubscribe_list": False,
                "ignore_duplicate_leads_in_other_campaign": True,
            },
        }
        data = api("POST", f"/campaigns/{campaign_id}/leads", body)
        total += len(batch)
        time.sleep(0.5)
    print(f"  Imported {total} leads")
    return total


def load_leads_from_csv(filepath):
    leads = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip()
            if not email:
                continue
            # Try to extract first name from email (before @, before dots/numbers)
            name_part = email.split("@")[0].replace(".", " ").replace("_", " ")
            first_name = name_part.split()[0].capitalize() if name_part else ""
            leads.append({
                "email": email,
                "first_name": first_name,
                "company_name": row.get("company", ""),
                "custom_fields": {
                    "Title": row.get("title", ""),
                    "Segment": row.get("profile", ""),
                },
            })
    return leads


# ============================================================
# CAMPAIGN DEFINITIONS — 3 variants per step
# ============================================================

CAMPAIGNS = [
    {
        "name": "LFG — Toronto Startups Actively Hiring Devs",
        "csv": "prospects/toronto_companies_actively_hiring_devs.csv",
        "sequences": [
            {
                "seq_number": 1,
                "seq_delay_details": {"delay_in_days": 0},
                "seq_variants": [
                    {
                        "subject": "stop hiring, start shipping",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Saw {{company_name}} is growing — hiring engineers is expensive and slow right now.</p>"
                            "<p>We're a dev agency that built an <b>agentic AI platform</b> that automates most of the engineering work. "
                            "That's how we build products at 80% of the cost and 5x the speed — not by cutting corners, but by removing the manual grind.</p>"
                            "<p>We've used it to ship full SaaS platforms in 6 weeks, MVPs that raised seed rounds, and internal tools that replaced entire teams.</p>"
                            "<p>Worth a quick chat to see if it makes sense for {{company_name}}?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "{{company_name}} — what if you didn't need to hire?",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Hiring devs right now: 3+ months, $150K+ fully loaded, plus ramp time. Painful.</p>"
                            "<p>We built an agentic AI platform that lets us ship production-grade software at <b>5x the speed and 80% of the cost</b> "
                            "of a traditional dev team. It's not offshore bodies — it's AI-augmented engineering.</p>"
                            "<p>Would it be worth 15 minutes to show you how it works?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "a faster way to build at {{company_name}}",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Quick question — if you could get production-ready software built at 80% of the cost of hiring, would that change your roadmap?</p>"
                            "<p>We're an AI-first dev agency. We built an agentic platform that automates the heavy lifting, "
                            "so we ship in weeks what normally takes months.</p>"
                            "<p>Happy to do a quick 15-min demo if you're curious.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
            {
                "seq_number": 2,
                "seq_delay_details": {"delay_in_days": 3},
                "seq_variants": [
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Following up. I know you're busy building.</p>"
                            "<p>Easiest way to see if we can help — I can do a <b>15-min live demo</b> of our agentic platform "
                            "and show you exactly how we'd approach {{company_name}}'s product. No pitch deck, just the real thing.</p>"
                            "<p>Want me to send over a few time slots?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Quick follow-up — one thing I didn't mention.</p>"
                            "<p>We work in weekly sprints with full transparency. You get <b>working demos every week</b>, not a black box "
                            "that surfaces 3 months later.</p>"
                            "<p>If you're spending $30K+/month on engineering and still not shipping fast enough, that's exactly the problem we solve. "
                            "Happy to show you a live demo.</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Not trying to flood your inbox — just wanted to share one thing.</p>"
                            "<p>Our agentic platform isn't vaporware. I can show you a <b>live demo in 15 min</b> — "
                            "you'll see exactly how we automate the engineering workflow and why it's faster than hiring.</p>"
                            "<p>Worth a look?</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
        ],
    },
    {
        "name": "LFG — Startup Founders (Seed/Series A)",
        "csv": "prospects/startup_founders_seed_series_a.csv",
        "sequences": [
            {
                "seq_number": 1,
                "seq_delay_details": {"delay_in_days": 0},
                "seq_variants": [
                    {
                        "subject": "ship your product 5x faster",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Congrats on the raise at {{company_name}}. Now the hard part — building fast enough before the runway gets tight.</p>"
                            "<p>We're an AI-first dev agency with an <b>agentic platform</b> that automates most of the engineering work. "
                            "We build products at 80% of the cost and 5x the speed of traditional dev teams.</p>"
                            "<p>We've shipped full SaaS platforms in 6 weeks and MVPs that went on to raise seed rounds.</p>"
                            "<p>Worth a 15-min demo to see how it works?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "{{company_name}} — build faster, burn less",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Post-raise is all about speed. Every month spent hiring and onboarding engineers is a month you're not shipping.</p>"
                            "<p>We built an agentic AI platform that lets us deliver production-ready software at <b>5x speed and 80% cost</b>. "
                            "No offshore teams, no junior devs — AI-augmented engineering.</p>"
                            "<p>Can I show you a quick demo?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "what if {{company_name}} could ship in weeks, not months?",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Early stage = every dollar and every week matters.</p>"
                            "<p>We're a dev agency that built an AI agentic platform to automate the engineering grind. "
                            "The result: we ship in weeks what takes most teams months, at a fraction of the cost.</p>"
                            "<p>Happy to do a 15-min live demo — no slides, just the real platform in action.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
            {
                "seq_number": 2,
                "seq_delay_details": {"delay_in_days": 4},
                "seq_variants": [
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Following up — I know early-stage founders live in their inbox.</p>"
                            "<p>The fastest way to evaluate us: a <b>15-min live demo</b> where I show you our agentic platform "
                            "and how we'd approach building for {{company_name}}. No fluff.</p>"
                            "<p>Want me to send a few time slots?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Bumping this up. One thing that might help —</p>"
                            "<p>We work in <b>weekly sprints with working demos every week</b>. You see progress in real time, not after 3 months. "
                            "And our agentic platform means we move faster than any traditional team.</p>"
                            "<p>15 min to show you how it works?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Last one from me. If timing isn't right, totally get it.</p>"
                            "<p>But if you're thinking about how to build faster without burning through your raise on full-time hires, "
                            "our agentic platform is built exactly for that. <b>15-min demo</b> — happy to show you the real thing.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
        ],
    },
    {
        "name": "LFG — Toronto Startups (Wellfound)",
        "csv": "prospects/toronto_startups_hiring_from_wellfound.csv",
        "sequences": [
            {
                "seq_number": 1,
                "seq_delay_details": {"delay_in_days": 0},
                "seq_variants": [
                    {
                        "subject": "stop hiring, start shipping",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Saw {{company_name}} is growing — hiring engineers is expensive and slow right now.</p>"
                            "<p>We're a dev agency that built an <b>agentic AI platform</b> that automates most of the engineering work. "
                            "That's how we build products at 80% of the cost and 5x the speed.</p>"
                            "<p>We've shipped full SaaS platforms in 6 weeks and internal tools that replaced entire teams.</p>"
                            "<p>Worth a quick chat to see if it makes sense for {{company_name}}?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "{{company_name}} — what if you didn't need to hire?",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Hiring devs: 3+ months, $150K+ loaded, plus ramp time.</p>"
                            "<p>We built an agentic AI platform that ships production-grade software at <b>5x speed and 80% cost</b>. "
                            "Not offshore bodies — AI-augmented engineering.</p>"
                            "<p>15 minutes to show you how it works?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "a faster way to build at {{company_name}}",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Quick question — if you could get production-ready software at 80% of hiring cost, would that change your roadmap?</p>"
                            "<p>We built an agentic platform that automates the heavy lifting. We ship in weeks what normally takes months.</p>"
                            "<p>Happy to do a 15-min demo if you're curious.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
            {
                "seq_number": 2,
                "seq_delay_details": {"delay_in_days": 3},
                "seq_variants": [
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Following up — easiest way to evaluate us is a <b>15-min live demo</b> of our agentic platform. "
                            "I'll show you exactly how we'd approach {{company_name}}'s product. No pitch deck.</p>"
                            "<p>Want me to send a few time slots?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>One thing I didn't mention — we work in weekly sprints. <b>Working demos every week</b>, "
                            "not a black box that surfaces months later.</p>"
                            "<p>If you're spending $30K+/month on eng and still not shipping fast enough, happy to show you a live demo of how we solve that.</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Not trying to flood your inbox. Our agentic platform isn't vaporware — "
                            "I can show you a <b>live demo in 15 min</b> so you see exactly how we automate engineering workflows.</p>"
                            "<p>Worth a look?</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
        ],
    },
    {
        "name": "LFG — Solo Founders & Small Tech CEOs",
        "csv": "prospects/solo_founders_small_tech.csv",
        "sequences": [
            {
                "seq_number": 1,
                "seq_delay_details": {"delay_in_days": 0},
                "seq_variants": [
                    {
                        "subject": "build {{company_name}} faster without hiring",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Running a small team means every dollar and every week counts. Hiring devs is a 3-month, $150K+ bet.</p>"
                            "<p>We built an <b>agentic AI platform</b> that lets us ship production-grade software at 80% of the cost and 5x the speed. "
                            "No offshore teams — AI-augmented engineering.</p>"
                            "<p>Can I show you a 15-min demo of how it works?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "what if {{company_name}} could ship in weeks?",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Small teams shouldn't have to wait months to ship. We built an agentic platform that automates "
                            "the engineering grind — <b>full products in weeks, not quarters</b>.</p>"
                            "<p>We've built SaaS platforms, mobile apps, and internal tools this way. All production-grade.</p>"
                            "<p>Worth a quick look?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "{{company_name}} — your dev team, without the overhead",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>What if you had a dev team that cost 80% less and shipped 5x faster?</p>"
                            "<p>That's what our agentic AI platform does. We automate the manual engineering work "
                            "so we deliver production-ready software in weeks.</p>"
                            "<p>Happy to do a 15-min live demo — no slides, just the real platform.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
            {
                "seq_number": 2,
                "seq_delay_details": {"delay_in_days": 4},
                "seq_variants": [
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Quick follow-up. The fastest way to evaluate us: a <b>15-min live demo</b> "
                            "where I show you our agentic platform in action on a real project.</p>"
                            "<p>Want me to send a couple time slots?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Bumping this — we work in <b>weekly sprints with working demos every week</b>. "
                            "Full transparency, no black boxes.</p>"
                            "<p>If you've been burned by agencies before, this is a different model. Happy to show you in 15 min.</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Last note from me. If the timing isn't right, no worries.</p>"
                            "<p>But if you're looking to build faster without the overhead of full-time hires, "
                            "our agentic platform was built for exactly that. <b>15-min demo</b> — happy to show you.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
        ],
    },
    {
        "name": "LFG — Toronto General Startup Founders",
        "csv": "prospects/toronto_startups_hiring_devs.csv",
        "sequences": [
            {
                "seq_number": 1,
                "seq_delay_details": {"delay_in_days": 0},
                "seq_variants": [
                    {
                        "subject": "stop hiring, start shipping",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Saw {{company_name}} is building in Toronto — hiring engineers is brutal right now.</p>"
                            "<p>We're a dev agency that built an <b>agentic AI platform</b> that automates most of the engineering work. "
                            "80% of the cost, 5x the speed. Not by cutting corners — by removing the manual grind.</p>"
                            "<p>Worth a quick chat?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "{{company_name}} — build faster, spend less",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Hiring devs: months of searching, $150K+ per head, plus onboarding.</p>"
                            "<p>We built an agentic AI platform that ships production software at <b>5x speed, 80% cost</b>. "
                            "AI-augmented engineering, not offshore bodies.</p>"
                            "<p>15 min to show you how?</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "a faster way to build {{company_name}}",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>If you could get production-ready software at 80% of hiring cost, would that change your plans?</p>"
                            "<p>We built an agentic platform that automates engineering. We ship in weeks what takes months.</p>"
                            "<p>Happy to do a 15-min demo.</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
            {
                "seq_number": 2,
                "seq_delay_details": {"delay_in_days": 3},
                "seq_variants": [
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Following up — <b>15-min live demo</b> of our agentic platform, "
                            "showing exactly how we'd approach building for {{company_name}}. No pitch deck.</p>"
                            "<p>Want me to send time slots?</p>"
                        ),
                        "variant_label": "A",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>One thing I didn't mention — <b>working demos every week</b>, not a 3-month black box. "
                            "Full transparency from day one.</p>"
                            "<p>If you're spending big on eng and still not shipping fast enough, happy to show you a live demo.</p>"
                        ),
                        "variant_label": "B",
                    },
                    {
                        "subject": "",
                        "email_body": (
                            "<p>Hey {{first_name}},</p>"
                            "<p>Not trying to spam you. Our platform isn't vaporware — "
                            "<b>15-min live demo</b> and you'll see exactly how we automate engineering workflows.</p>"
                            "<p>Worth a look?</p>"
                        ),
                        "variant_label": "C",
                    },
                ],
            },
        ],
    },
]


def main():
    print("=" * 60)
    print("SMARTLEAD CAMPAIGN SETUP")
    print("=" * 60)

    for campaign_def in CAMPAIGNS:
        print(f"\n--- {campaign_def['name']} ---")

        # 1. Create campaign
        campaign_id = create_campaign(campaign_def["name"])

        # 2. Add sequences with variants
        add_sequences(campaign_id, campaign_def["sequences"])

        # 3. Load and import leads
        leads = load_leads_from_csv(campaign_def["csv"])
        if leads:
            add_leads(campaign_id, leads)
        else:
            print(f"  WARNING: No leads found in {campaign_def['csv']}")

        time.sleep(1)

    print(f"\n{'=' * 60}")
    print("ALL CAMPAIGNS CREATED SUCCESSFULLY")
    print("Go to Smartlead dashboard to connect sender accounts and launch.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
