# GHL SuperSpeed v3

The fastest programmatic GHL workflow builder. Creates complete campaigns (workflows + steps + triggers) via GHL's internal API in seconds.

**Benchmark: 8 workflows, 45 action steps, 8 triggers in 3.6 seconds.**

## Prerequisites

### 1. MCP Server Access (Required for auto-auth)

This system uses the DLF Agency MCP Server for Firebase JWT token management. The server handles token refresh automatically.

**MCP Server:** `https://dlf-agency.skool-203.workers.dev`

To get access, email **info@doctorleadflow.com** with subject "MCP Server Access Request".

Once granted, you'll receive:
- An ADMIN_PIN for the CLI token endpoint
- Access to 18 workflow builder MCP tools via Claude Code

### 2. Firebase JWT Token (Alternative -- no MCP needed)

If you don't use the MCP server, you need a Firebase JWT manually:

1. Log into `app.gohighlevel.com`
2. Open DevTools > Application > IndexedDB > `firebaseLocalStorageDb`
3. Copy the `idToken` from the stored user object
4. Export: `export GHL_FIREBASE_TOKEN='your_token_here'`

Tokens expire in 1 hour. For long-running use, set `GHL_FIREBASE_REFRESH_TOKEN` (extract the `refreshToken` from the same IndexedDB entry -- refresh tokens never expire).

### 3. Python 3.9+

No pip dependencies. The engine uses only stdlib (`urllib`, `json`, `uuid`, `ssl`, `concurrent.futures`).

## Quick Start

```bash
# Clone
git clone https://github.com/drleadflow/ghl-superspeed-v3.git
cd ghl-superspeed-v3

# Option A: Token from MCP server (recommended)
export GHL_FIREBASE_TOKEN=$(curl -s "https://dlf-agency.skool-203.workers.dev/cli/token?pin=YOUR_PIN" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Option B: Token from environment
export GHL_FIREBASE_TOKEN='eyJhbG...'

# Run the PPP webinar campaign (8 workflows, 45 steps)
python3 campaigns/ppp-webinar.py

# Run tests (28 tests)
python3 tests/test_engine.py
```

## Architecture

### Pipeline (per workflow, all run in parallel)

```
1. POST /workflow/{loc}                    -- Create workflow
2. POST /workflow/{loc}/tags/create        -- Create location tag
3. POST /workflow/{loc}/trigger            -- Create trigger with tag condition
4. PUT  /workflow/{loc}/trigger/{id}       -- Link trigger to first step (targetActionId)
5. PUT  /workflow/{loc}/{wfId}             -- Save action steps (templates array)
6. PUT  /workflow/{loc}/{wfId}/auto-save   -- Enable advanced canvas + sync to Firebase
```

All 8 workflows run their full 6-step pipeline simultaneously via `ThreadPoolExecutor`.

### Auth Flow

```
MCP Server (Cloudflare Worker)
  --> KV-cached Firebase JWT (55-min TTL)
      --> Auto-refreshes via Firebase securetoken API
          --> Refresh token stored as Cloudflare secret (never expires)
```

The engine tries sources in order:
1. MCP server `/cli/token` endpoint (if `GHL_ADMIN_PIN` set)
2. Firebase refresh (if `GHL_FIREBASE_REFRESH_TOKEN` set)
3. `GHL_FIREBASE_TOKEN` environment variable
4. CLI argument

## Project Structure

```
ghl-superspeed-v3/
  lib/engine.py              -- Core engine: TokenManager, GHLClient, CampaignBuilder, step builders
  campaigns/ppp-webinar.py   -- Example: 8-workflow webinar campaign (45 steps, 8 triggers)
  tests/test_engine.py       -- 28 tests, all passing
  tests/live_test_render.py  -- Live API render verification test
  templates/blueprints.json  -- Campaign blueprints (webinar, nurture, appointment, onboarding)
  chrome-extension/          -- Chrome extension for passive token capture
```

## Step Builders

```python
from lib.engine import sms_step, email_step, wait_step, tag_step, webhook_step, ai_step, link_steps

steps = link_steps([
    sms_step("Welcome", "Hey {{contact.first_name}}!"),
    wait_step("1 day", 1, "days"),
    email_step("Follow Up", "subject line", "Email body text"),
    wait_step("2 hours", 2, "hours"),    # Automatically sends "hour" (singular) to API
    tag_step("Mark Complete", ["campaign-done"]),
    webhook_step("Notify", "https://your-webhook.com"),
    ai_step("Classify", "Classify this lead", "gpt-4o"),
])
```

`link_steps()` auto-generates UUIDs, sets `order`, and links `parentKey`/`next` for the chain.

## Critical GHL Gotchas

These are hard-won discoveries from reverse-engineering the internal API. **Read before building.**

### Wait Step Unit Strings (INCONSISTENT)

GHL's advanced canvas uses **inconsistent** unit strings:

| Unit | API String | Notes |
|------|-----------|-------|
| Minutes | `"minutes"` | Plural |
| Hours | `"hour"` | **SINGULAR** -- `"hours"` renders the number but NOT the label |
| Days | `"days"` | Plural |

The engine handles this automatically -- `wait_step("2 hours", 2, "hours")` sends `"hour"` to the API.

### Triggers Require 3 Steps

1. **Create location tag first** -- `POST /workflow/{loc}/tags/create` with `{"tag": "name"}`. Without this, the trigger tag condition renders blank in the UI.
2. **Create trigger** -- `POST /workflow/{loc}/trigger` with conditions, actions, etc.
3. **Update trigger with `targetActionId`** -- `PUT /workflow/{loc}/trigger/{id}` linking to the first step's ID. Without this, the trigger floats disconnected on the advanced canvas.

### Auto-Save Required for Advanced Canvas

The regular `PUT /workflow/{loc}/{wfId}` saves steps but the advanced canvas reads from Firebase/Firestore. You must also call `PUT /workflow/{loc}/{wfId}/auto-save` which:

- Sets `meta.advanceCanvasMeta.enabled = true`
- Adds `advanceCanvasMeta.position` to each step and trigger
- Syncs trigger data to Firebase Storage (`triggersFilePath`)
- Creates an `autoSaveSession` for version tracking

### Version Field

- `version` is **mandatory** on PUT -- must match current version or the request is rejected
- GHL increments version on each save
- `autoSaveSession.version` = the version when the session **started** (not the current version)

### Type String Corrections

Many documented type strings are wrong. Verified corrections:

| Documentation Says | Actually Use |
|-------------------|-------------|
| `create_contact` | `create_update_contact` |
| `openai_completion` | `chatgpt` |
| `date_formatter` | `datetime_formatter` |
| `split` | `workflow_split` |
| `internal_create_opportunity` | `create_opportunity` |
| `facebook_message` | `fb_interactive_messenger` |
| `instagram_message` | `instagram-dm` |

56 action types verified. Full list in `lib/engine.py:VERIFIED_ACTIONS`.

### Dual Storage Model

GHL workflows are split across two storage systems:

- **MongoDB** -- workflow metadata (name, status, version). Accessed via REST API.
- **Firebase Storage** -- actual workflow logic (templates array, triggers). Accessed via signed URLs.
- **Firestore** -- real-time database used by the advanced canvas builder for live editing.

The auto-save endpoint bridges all three.

## MCP Tools (Claude Code Integration)

With MCP server access, these 18 tools are available in Claude Code:

| Tool | Purpose |
|------|---------|
| `ghl_workflow_builder_list` | List workflows/folders |
| `ghl_workflow_builder_create` | Create workflow |
| `ghl_workflow_builder_get` | Get workflow metadata |
| `ghl_workflow_builder_get_steps` | Get steps from Firebase |
| `ghl_workflow_builder_get_triggers` | Get triggers from Firebase |
| `ghl_workflow_builder_update` | Update workflow settings |
| `ghl_workflow_builder_save_steps` | Save action steps |
| `ghl_workflow_builder_create_trigger` | Create trigger |
| `ghl_workflow_builder_update_trigger` | Update trigger (targetActionId) |
| `ghl_workflow_builder_delete_trigger` | Delete trigger |
| `ghl_workflow_builder_auto_save` | Sync to advanced canvas |
| `ghl_workflow_builder_create_tag` | Create location tag |
| `ghl_workflow_builder_publish` | Publish workflow |
| `ghl_workflow_builder_draft` | Set to draft |
| `ghl_workflow_builder_delete` | Delete workflow |
| `ghl_workflow_builder_create_folder` | Create folder |
| `ghl_workflow_builder_clone` | Clone workflow |
| `ghl_workflow_builder_error_count` | Get error count |

Add the MCP server to your Claude Code config (`.mcp.json`):
```json
{
  "mcpServers": {
    "dlf-agency": {
      "type": "url",
      "url": "https://dlf-agency.skool-203.workers.dev/mcp"
    }
  }
}
```

## GHL URLs

- **Classic builder:** `https://app.gohighlevel.com/location/{locationId}/workflow/{workflowId}`
- **Advanced canvas:** `https://app.gohighlevel.com/location/{locationId}/workflow/{workflowId}/advanced-canvas`

## Test Account

| Field | Value |
|-------|-------|
| Location | `2hP6rCb3COd2HUjD25w2` (Christians Testing) |
| Company | `R1HWQKyMMoj4PJ5mAYed` |
| User | `YewkebOufK3hmeP1gx4B` |
| Test Folder | `ca2666ec-84af-4155-9d0a-1774430c98b7` (++ Agent Testing) |

## License

Private. Contact info@doctorleadflow.com for access.
