# GHL Token Server

Cloudflare Worker that manages Firebase JWT tokens for the GoHighLevel internal API. Auto-refreshes tokens and caches them in KV with a 50-minute TTL.

## Setup

```bash
# 1. Install wrangler if needed
npm i -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Run setup (creates KV namespace, sets ADMIN_PIN secret)
chmod +x setup.sh
./setup.sh

# 4. Deploy
npm run deploy
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check |
| GET | `/cli/token?pin=PIN` | PIN | Get a fresh Firebase ID token |
| POST | `/setup?pin=PIN` | PIN | Store refresh token and config |
| GET | `/config?pin=PIN` | PIN | View stored config (no secrets) |

## Store your refresh token

```bash
curl -X POST 'https://ghl-token-server.YOUR.workers.dev/setup?pin=YOUR_PIN' \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token": "...", "location_id": "...", "company_id": "...", "user_id": "..."}'
```

## Get a token

```bash
curl 'https://ghl-token-server.YOUR.workers.dev/cli/token?pin=YOUR_PIN'
# {"token": "eyJhbG...", "expires_in": 3000}
```

## Local dev

```bash
npm run dev
```
