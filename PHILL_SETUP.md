# AI Simple Phill Setup Handoff

This is the short path for getting Phill running on his own GHL account under the AI Simple setup, without sharing your local `.env` files or tokens.

## What Phill Needs

- Access to the AI Simple private GitHub repo: `Vibe-Marketer/ghl-superspeed-v3`
- Python 3.10+ installed
- A GoHighLevel login for the target sub-account
- These GHL values:
  - `GHL_LOCATION_ID`
  - `GHL_COMPANY_ID`
  - `GHL_USER_ID`
- One auth method:
  - preferred: `GHL_FIREBASE_REFRESH_TOKEN`
  - alternate: `GHL_TOKEN_SERVER` plus `GHL_ADMIN_PIN`

## 1. Clone The Repo

```bash
git clone https://github.com/Vibe-Marketer/ghl-superspeed-v3.git
cd ghl-superspeed-v3
```

No Python package install is needed for the workflow builder. The core app uses only Python stdlib.

## 2. Create Phill's Local Account Config

Run:

```bash
python3 scripts/setup-account.py phill
```

The script will prompt for the GHL IDs and auth details, verify access to the target location, create these folders in GHL if needed, and write a local `.env.phill` file:

- `TEST WORKFLOWS`
- `AI GENERATED - STAGING`

The `.env.phill` file contains secrets and is intentionally gitignored.

## 3. Load Phill's Config

```bash
set -a
source .env.phill
set +a
```

Confirm the important values loaded:

```bash
python3 - <<'PY'
import os
for key in ["GHL_LOCATION_ID", "GHL_COMPANY_ID", "GHL_USER_ID", "GHL_PARENT_FOLDER", "GHL_TEST_FOLDER"]:
    print(f"{key}={'set' if os.environ.get(key) else 'missing'}")
PY
```

## 4. Run The Local Unit Test

```bash
python3 tests/test_engine.py
```

This test does not call GHL. It verifies the local workflow builder logic.

## 5. Run A Small Live Smoke Test

```bash
python3 ai-simple.py preview example-simple --env .env.phill
python3 ai-simple.py deploy example-simple --env .env.phill
```

Expected result: the script authenticates, creates a small example campaign under `AI GENERATED - STAGING`, and prints GHL workflow URLs. Open the URLs in GHL and confirm the trigger and action steps render.

## 6. Build Phill's First Campaign

For a simple follow-up campaign, copy the starter campaign:

```bash
cp campaigns/my-campaign.py campaigns/phill-campaign.py
```

For a full webinar funnel, copy the reusable webinar template:

```bash
cp campaigns/webinar-funnel.py campaigns/phill-webinar.py
```

Set campaign-specific values in `.env.phill` before running a real campaign:

```bash
CAMPAIGN_NAME=Phill Webinar Funnel
CAMPAIGN_BUSINESS_NAME=Phill Business
CAMPAIGN_SENDER_NAME=Phill Team
CAMPAIGN_SERVICE_CATEGORY=Phill's services
CAMPAIGN_WEBINAR_TITLE=The Growth System Workshop
CAMPAIGN_WEBINAR_LINK={{custom_values.webinar_link}}
CAMPAIGN_OFFER_NAME=Implementation Program
CAMPAIGN_TAG_PREFIX=phill-webinar
```

Edit the copied campaign if needed, then run:

```bash
python3 ai-simple.py preview phill-campaign --env .env.phill
python3 ai-simple.py deploy phill-campaign --env .env.phill

python3 ai-simple.py preview phill-webinar --env .env.phill
python3 ai-simple.py deploy phill-webinar --env .env.phill
```

Generated campaigns should land in `AI GENERATED - STAGING` first. Review them in GHL before moving or enabling them for production traffic.

Deployment logs are written under `logs/campaigns/`. To review recent logs:

```bash
python3 ai-simple.py logs
```

## AI Workflow Skill

The folder `skill/ai-simple-ghl-workflows/` can be installed or copied into an AI assistant's skill directory. It tells the assistant how to use this package, when to read `workflow-reference/`, how to validate campaigns, and how to deploy only to staging.

## Backup Status Checklist

Before handing this to Phill, confirm:

```bash
git status --short --branch
git log --oneline --decorate --max-count=5
git remote -v
```

Ready state means:

- working tree is clean
- local `main` is not ahead of `origin/main`
- remote points to `https://github.com/Vibe-Marketer/ghl-superspeed-v3.git`
- no `.env`, `.env.*`, token, or credential file appears in `git status`

## Notes

- Do not commit `.env.phill` or any refresh token.
- If Phill wants his own token server, deploy the AI Simple `token-server/` worker to his Cloudflare account and follow `token-server/README.md`.
- If auth fails, the first things to re-check are the refresh token, `GHL_LOCATION_ID`, and whether Phill's GHL user can access that location.
