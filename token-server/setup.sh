#!/usr/bin/env bash
set -euo pipefail

# ─── GHL Token Server Setup ─────────────────────────────────────
# Creates the KV namespace, sets secrets, and updates wrangler.toml

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOML="$SCRIPT_DIR/wrangler.toml"

echo "=== GHL Token Server Setup ==="
echo

# 1. ADMIN_PIN
read -rp "Enter an ADMIN_PIN (leave blank to auto-generate): " PIN
if [[ -z "$PIN" ]]; then
  PIN=$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 8 || true)
  echo "Generated PIN: $PIN"
fi
echo

# 2. Create KV namespace
echo "Creating KV namespace TOKEN_STORE..."
KV_OUTPUT=$(wrangler kv namespace create TOKEN_STORE 2>&1)
echo "$KV_OUTPUT"

# Extract the namespace ID from output like: id = "abc123..."
KV_ID=$(echo "$KV_OUTPUT" | grep -oE 'id = "[^"]+"' | head -1 | sed 's/id = "//;s/"//')

if [[ -z "$KV_ID" ]]; then
  echo "ERROR: Could not parse KV namespace ID from wrangler output."
  echo "Create it manually: wrangler kv namespace create TOKEN_STORE"
  echo "Then replace REPLACE_WITH_KV_NAMESPACE_ID in wrangler.toml"
  exit 1
fi

echo
echo "KV namespace ID: $KV_ID"

# 3. Update wrangler.toml
if [[ "$(uname)" == "Darwin" ]]; then
  sed -i '' "s/REPLACE_WITH_KV_NAMESPACE_ID/$KV_ID/" "$TOML"
else
  sed -i "s/REPLACE_WITH_KV_NAMESPACE_ID/$KV_ID/" "$TOML"
fi
echo "Updated wrangler.toml with KV namespace ID."

# 4. Set ADMIN_PIN as a secret
echo
echo "Setting ADMIN_PIN secret..."
echo "$PIN" | wrangler secret put ADMIN_PIN

echo
echo "=== Setup Complete ==="
echo
echo "Your ADMIN_PIN: $PIN"
echo "Save this — you need it for every API call."
echo
echo "Next steps:"
echo "  1. Deploy:  cd token-server && npm run deploy"
echo "  2. Store your Firebase refresh token:"
echo "     curl -X POST 'https://ghl-token-server.<your-subdomain>.workers.dev/setup?pin=$PIN' \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"refresh_token\": \"YOUR_FIREBASE_REFRESH_TOKEN\"}'"
echo "  3. Get a token:"
echo "     curl 'https://ghl-token-server.<your-subdomain>.workers.dev/cli/token?pin=$PIN'"
