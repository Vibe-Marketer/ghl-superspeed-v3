---
name: ai-simple-ghl-workflows
description: Create, preview, customize, validate, and deploy GoHighLevel workflows for AI Simple clients using the bundled GHL workflow reference, verified action/trigger types, and the local AI Simple SuperSpeed deployment engine. Use when a user wants to build any GHL workflow, see workflow examples, turn a plain-English automation request into deployable workflows, or deploy campaigns to GHL staging.
---

# AI Simple GHL Workflows

Use this skill to help an AI assistant create and deploy GHL workflows from the packaged AI Simple workflow folder.

## Default Workflow

1. Inspect available examples:
   - Run `python3 ai-simple.py examples`
   - Run `python3 ai-simple.py preview webinar-funnel`
2. For custom workflow authoring, read only the reference files needed:
   - `references/verified-types.json` for valid action and trigger type strings.
   - `references/action-schemas.md` for action attributes.
   - `references/trigger-schemas.md` for trigger attributes.
   - `references/data-schemas.md` for step linking and workflow envelope.
   - `references/save-modes.md` for GHL save/publish gotchas.
3. Create or edit a campaign file under `campaigns/`.
4. Validate locally:
   - `python3 -m py_compile campaigns/<campaign>.py`
   - `python3 tests/test_engine.py`
5. Preview before deploy:
   - `python3 ai-simple.py preview <template-or-campaign>`
6. Deploy only to staging:
   - `python3 ai-simple.py deploy <template-or-campaign> --env .env.<client>`
7. After deploy, inspect the log manifest in `logs/campaigns/`.

## Guardrails

- Never ask a non-technical client to edit Python unless explicitly requested.
- Never deploy directly to production folders; use `AI GENERATED - STAGING`.
- Never commit `.env`, `.env.*`, token values, user keys, or campaign logs.
- Do not invent action or trigger type strings. Use `verified-types.json`.
- For wait steps, use `hour` internally for hours; the engine handles `hours` normalization for helper-built waits.
- Keep workflow names, tags, sender names, offers, links, and copy configurable through `CAMPAIGN_*` environment variables whenever possible.

## Useful Commands

```bash
python3 ai-simple.py examples
python3 ai-simple.py preview webinar-funnel
python3 ai-simple.py configure phill
python3 ai-simple.py deploy webinar-funnel --env .env.phill
python3 ai-simple.py logs
```
