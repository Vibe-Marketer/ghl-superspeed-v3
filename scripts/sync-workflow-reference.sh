#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/Users/Naegele/dev/ghl-automation-builder}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF_DIR="$ROOT_DIR/workflow-reference"
SKILL_REF_DIR="$ROOT_DIR/skill/ai-simple-ghl-workflows/references"

mkdir -p "$REF_DIR" "$SKILL_REF_DIR"

cp "$SOURCE_DIR/verified/types.json" "$REF_DIR/verified-types.json"
cp "$SOURCE_DIR/schemas/action-schemas.md" "$REF_DIR/action-schemas.md"
cp "$SOURCE_DIR/schemas/trigger-schemas.md" "$REF_DIR/trigger-schemas.md"
cp "$SOURCE_DIR/docs/data-schemas.md" "$REF_DIR/data-schemas.md"
cp "$SOURCE_DIR/docs/save-modes.md" "$REF_DIR/save-modes.md"

cp "$REF_DIR/verified-types.json" "$SKILL_REF_DIR/verified-types.json"
cp "$REF_DIR/action-schemas.md" "$SKILL_REF_DIR/action-schemas.md"
cp "$REF_DIR/trigger-schemas.md" "$SKILL_REF_DIR/trigger-schemas.md"
cp "$REF_DIR/data-schemas.md" "$SKILL_REF_DIR/data-schemas.md"
cp "$REF_DIR/save-modes.md" "$SKILL_REF_DIR/save-modes.md"

echo "Synced workflow reference from $SOURCE_DIR"
