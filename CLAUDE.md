# GHL SuperSpeed v3

## Project Context
- Programmatic GHL workflow builder via Firebase-authenticated internal API
- Zero dependencies — pure Python stdlib
- Config via .env file (see .env.example)
- Token server: Cloudflare Worker in token-server/
- Multi-account support via per-account env files (.env.aisimple, .env.leveragedva, etc.)

## Quick Start
1. Copy .env.example to .env (or .env.<account-name>) and fill in your GHL credentials
2. Deploy token-server/ to Cloudflare Workers (or use a refresh token directly)
3. Run: `export $(grep -v '^#' .env.<account> | xargs) && python3 campaigns/my-campaign.py`

## Origin
This repo was forked from https://github.com/drleadflow/ghl-superspeed-v3 (Emeka Ajufo / Dr. Lead Flow).
That upstream is kept here as historical reference only — it is no longer pulled from.
This repo (Vibe-Marketer/ghl-superspeed-v3) is the active AI Simple version and diverges intentionally.
