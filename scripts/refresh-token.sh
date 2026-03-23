#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Firebase Token Refresher for GHL SuperSpeed v3
#
# Refreshes a Firebase ID token using a refresh token.
# The ID token is what you pass as GHL_FIREBASE_TOKEN.
#
# Usage:
#   export GHL_FIREBASE_REFRESH_TOKEN='your-refresh-token'
#   ./scripts/refresh-token.sh
#
# Where to get a refresh token:
#   1. Log into app.gohighlevel.com
#   2. Chrome DevTools > Application > IndexedDB > firebaseLocalStorageDb
#   3. Click the entry > stsTokenManager > refreshToken
#   4. Copy that value (it never expires)
# ─────────────────────────────────────────────────────────────

FIREBASE_API_KEY="AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"

if [ -z "$GHL_FIREBASE_REFRESH_TOKEN" ]; then
  echo "ERROR: GHL_FIREBASE_REFRESH_TOKEN not set"
  echo ""
  echo "To get a refresh token:"
  echo "  1. Open app.gohighlevel.com in Chrome"
  echo "  2. Log in to your location"
  echo "  3. DevTools > Application > IndexedDB > firebaseLocalStorageDb"
  echo "  4. Click the entry, find stsTokenManager.refreshToken"
  echo "  5. export GHL_FIREBASE_REFRESH_TOKEN='your_token'"
  exit 1
fi

echo "Refreshing Firebase ID token..."

RESPONSE=$(curl -s -X POST \
  "https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=${GHL_FIREBASE_REFRESH_TOKEN}")

ID_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id_token',''))" 2>/dev/null)
EXPIRES_IN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('expires_in',''))" 2>/dev/null)

if [ -z "$ID_TOKEN" ]; then
  echo "FAILED to refresh token:"
  echo "$RESPONSE"
  exit 1
fi

echo "SUCCESS — token refreshed (expires in ${EXPIRES_IN}s)"
echo ""

# Test the token
echo "Testing against GHL API..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://backend.leadconnectorhq.com/workflow/2hP6rCb3COd2HUjD25w2/list?parentId=root&limit=1" \
  -H "token-id: ${ID_TOKEN}" \
  -H "channel: APP")

if [ "$HTTP_STATUS" = "200" ]; then
  echo "TOKEN VALID — API returned 200"
else
  echo "TOKEN ISSUE — API returned ${HTTP_STATUS}"
fi

echo ""
echo "Set in your environment:"
echo "  export GHL_FIREBASE_TOKEN='${ID_TOKEN}'"
echo ""
echo "Or run your campaign directly:"
echo "  GHL_FIREBASE_TOKEN='${ID_TOKEN}' python3 campaigns/your-campaign.py"
