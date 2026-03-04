# Outreach — Apollo + Smartlead Campaign Manager

An AI-powered outbound sales pipeline that pulls targeted leads from Apollo.io and runs email campaigns through Smartlead — managed via a Claude Code skill.

## Setup

### 1. Add your API keys

Open `keys.txt` and fill in your keys:

```
APOLLO_KEY=your_apollo_api_key_here
SMARTLEAD_KEY=your_smartlead_api_key_here
```

- **Apollo key** — found in your Apollo.io account under API settings
- **Smartlead key** — found in your Smartlead account under API settings

### 2. Install dependencies (or let claude handle it)

```bash
python -m venv venv
source venv/bin/activate
pip install requests
```

### 3. Start the outreach

Open Claude Code and run:

```
/outreach
```

This loads your outbound co-pilot. Just describe what you want to do and it will guide you through the rest.

---

## What it does

- **Pull leads** from Apollo.io based on your ICP (titles, company size, industry, location, funding stage) — previews results before spending enrichment credits
- **Create Smartlead campaigns** with A/B/C email variants and multi-step sequences
- **Check campaign stats** — sent, opens, replies, bounces
- **Pause / resume / adjust** campaigns
- **Act as a daily outbound co-pilot** — just ask

---

## Files

| File | Purpose |
|------|---------|
| `outreach.md` | The skill prompt injected into Claude — a living doc that Claude updates as you provide company info, ICP segments, campaigns, and preferences. You can ask Claude to update it at any time. |
| `prospect.py` | Claude refers to this script when prospecting leads from Apollo |
| `smartlead_setup.py` | Claude refers to this script when creating and managing Smartlead campaigns |
| `keys.txt` | API keys (never commit this) |

---

## Typical workflow

1. `/outreach` → describe your product
2. Co-pilot asks about your ICP, then pulls and previews leads from Apollo
3. Approve leads → they get enriched and saved to `prospects/`
4. Co-pilot creates Smartlead campaigns with email copy
5. Go to Smartlead dashboard → connect sender email accounts → activate campaigns
