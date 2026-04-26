# GHL SuperSpeed v3

## Project Context
- Programmatic GHL workflow builder via Firebase-authenticated internal API
- Zero dependencies — pure Python stdlib
- Config via .env file (see .env.example)
- Token server: Cloudflare Worker in token-server/
- Multi-account support via per-account env files (.env.aisimple, .env.leveragedva, .env.test-brokerage)

## Quick Start
1. Copy .env.example to .env (or .env.<account-name>) and fill in your GHL credentials
2. Deploy token-server/ to Cloudflare Workers (or use a refresh token directly)
3. Run: `set -a && source .env.<account> && set +a && python3 campaigns/your-campaign.py`

## Canonical Types (synced from ghl-automation-builder)

`lib/verified-types.json` is a **synced copy — DO NOT EDIT.** The master lives at
`/Users/Naegele/dev/ghl-automation-builder/verified/types.json`.

`lib/engine.py` loads this at import time into:
- `VERIFIED_ACTIONS` (frozenset, 56 entries) — used in `CampaignBuilder.validate()` to fail-fast on bad action type strings before any API call.
- `VERIFIED_TRIGGERS` (frozenset, 57 entries) — available for trigger validation.

When you discover a new working type:
1. Edit the MASTER (`ghl-automation-builder/verified/types.json`) and bump the count.
2. Run `ghl-automation-builder/scripts/sync-types.sh` — copies to this repo + ghl-mcp.
3. Commit both repos.

## Auth Paths (priority order in TokenManager)
1. Cached token if < 50 min old (in-memory)
2. MCP token server (`GHL_TOKEN_SERVER` + `GHL_ADMIN_PIN`) — issues fresh Firebase JWT
3. Direct Firebase refresh (`GHL_FIREBASE_REFRESH_TOKEN`) → calls `securetoken.googleapis.com`

The test-brokerage env uses path 3 (refresh token only). Aisimple env uses path 2.

## Verified — End-to-End Test (2026-04-25)
Ran `python3 campaigns/example-simple.py` against test-brokerage location `6KFX17XItaklbgvQZjEP` →
2 workflows, 7 steps, 2 triggers deployed in 3.8s with 0 errors.

## Origin
This repo was forked from https://github.com/drleadflow/ghl-superspeed-v3 (Emeka Ajufo / Dr. Lead Flow).
That upstream is kept here as historical reference only — it is no longer pulled from.
This repo (Vibe-Marketer/ghl-superspeed-v3) is the active AI Simple version and diverges intentionally.
