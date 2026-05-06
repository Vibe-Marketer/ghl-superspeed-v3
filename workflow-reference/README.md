# AI Simple Workflow Reference

This directory is the local workflow authoring reference for AI assistants and the `ai-simple.py` launcher.

Source of truth: `/Users/Naegele/dev/ghl-automation-builder`

Synced files:
- `verified-types.json` — verified action and trigger type strings.
- `action-schemas.md` — action payload fields and examples.
- `trigger-schemas.md` — trigger payload fields and examples.
- `data-schemas.md` — workflow step envelope and linking model.
- `save-modes.md` — internal API save/publish behavior and gotchas.

When creating arbitrary workflows:
1. Use only action and trigger type strings from `verified-types.json`.
2. Use `action-schemas.md` and `trigger-schemas.md` for required attributes.
3. Use `data-schemas.md` for `templates`, `id`, `order`, `next`, and `parentKey`.
4. Deploy first to `AI GENERATED - STAGING`.
5. Check `logs/campaigns/` after deployment for the manifest.
