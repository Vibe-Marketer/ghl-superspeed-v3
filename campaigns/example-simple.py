#!/usr/bin/env python3
"""
Simple Example Campaign — Copy this to build your own.

Creates 2 workflows:
  1. Welcome sequence (SMS → Wait 1 day → Email → Tag)
  2. Follow-up sequence (SMS → Wait 2 hours → Email)

Usage:
    # Option A: MCP token (recommended)
    export GHL_ADMIN_PIN="your-pin"
    export GHL_FIREBASE_TOKEN=$(curl -s "https://dlf-agency.skool-203.workers.dev/cli/token?pin=$GHL_ADMIN_PIN" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    python3 campaigns/example-simple.py

    # Option B: Manual token
    export GHL_FIREBASE_TOKEN="eyJhbG..."
    python3 campaigns/example-simple.py

    # Option C: Refresh token (auto-refreshes)
    export GHL_FIREBASE_REFRESH_TOKEN="your-refresh-token"
    python3 campaigns/example-simple.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.engine import (
    TokenManager, GHLClient, CampaignBuilder,
    sms_step, email_step, wait_step, tag_step, link_steps,
)

# ── EDIT THESE ───────────────────────────────────────────────────────────────

LOCATION_ID = "2hP6rCb3COd2HUjD25w2"  # Your GHL location ID
COMPANY_ID = "R1HWQKyMMoj4PJ5mAYed"   # Your company ID (from GHL URL)
USER_ID = "YewkebOufK3hmeP1gx4B"      # Your user ID (from GHL)
PARENT_FOLDER = ""                      # Leave empty for root, or set folder ID

# ── DEFINE YOUR CAMPAIGN ─────────────────────────────────────────────────────

CAMPAIGN = {
    "welcome": {
        "name": "Welcome Sequence",
        "tag": "new-lead",                # Fires when contact gets this tag
        "templates": link_steps([
            sms_step("Welcome SMS",
                "Hey {{contact.first_name}}, welcome! We'll be in touch soon."),
            wait_step("1 day", 1, "days"),
            email_step("Welcome Email",
                "welcome aboard",
                """Hey {{contact.first_name}},

Thanks for joining us!

Here's what to expect over the next few days:

We'll send you helpful info about our services.

If you have any questions, just reply to this email.

Talk soon!""",
                "Your Name"),
            tag_step("Mark Welcome Done", ["welcome-complete"]),
        ]),
    },
    "followup": {
        "name": "Follow-Up Sequence",
        "tag": "needs-followup",
        "templates": link_steps([
            sms_step("Check In",
                "Hey {{contact.first_name}}, just checking in — did you have any questions?"),
            wait_step("2 hours", 2, "hours"),
            email_step("Followup Email",
                "quick follow-up",
                """Hey {{contact.first_name}},

I wanted to follow up on my earlier message.

If you're interested in learning more, just reply and we'll get you started.

Thanks!""",
                "Your Name"),
        ]),
    },
}

# ── RUN (don't edit below) ───────────────────────────────────────────────────

def main():
    total_steps = sum(len(wf["templates"]) for wf in CAMPAIGN.values())
    print(f"Simple Example — {len(CAMPAIGN)} workflows, {total_steps} steps\n")

    token_mgr = TokenManager(LOCATION_ID)
    if os.environ.get("GHL_FIREBASE_REFRESH_TOKEN"):
        token_mgr.set_refresh_token(os.environ["GHL_FIREBASE_REFRESH_TOKEN"])

    client = GHLClient(token_mgr, LOCATION_ID)

    print("Testing auth...")
    test = client.request("GET", f"/workflow/{LOCATION_ID}/list?parentId=root&limit=1")
    if not test:
        print("Auth failed! Check your token.")
        sys.exit(1)
    print("Auth OK\n")

    builder = CampaignBuilder(client, LOCATION_ID)
    stats = builder.build(
        CAMPAIGN,
        folder_name="Example Campaign",
        parent_folder=PARENT_FOLDER or None,
        company_id=COMPANY_ID,
        user_id=USER_ID,
    )

    if stats["steps_saved"] == total_steps:
        print(f"\nAll {total_steps} steps saved!")
    else:
        print(f"\nWARNING: Expected {total_steps}, saved {stats['steps_saved']}")


if __name__ == "__main__":
    main()
