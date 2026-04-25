#!/usr/bin/env python3
"""
My Campaign — Template that reads all config from environment variables.

Usage:
    1. Copy .env.example to .env and fill in your GHL credentials
    2. Source your env:  export $(grep -v '^#' .env | xargs)
    3. Run:  python3 campaigns/my-campaign.py

Or set variables directly:
    export GHL_LOCATION_ID="your-location-id"
    export GHL_COMPANY_ID="your-company-id"
    export GHL_USER_ID="your-user-id"
    export GHL_FIREBASE_TOKEN="eyJhbG..."
    python3 campaigns/my-campaign.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.engine import (
    TokenManager, GHLClient, CampaignBuilder,
    sms_step, email_step, wait_step, tag_step, link_steps,
)

# ── CONFIG (from environment) ───────────────────────────────────────────────

LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")
COMPANY_ID = os.environ.get("GHL_COMPANY_ID", "")
USER_ID = os.environ.get("GHL_USER_ID", "")
PARENT_FOLDER = os.environ.get("GHL_PARENT_FOLDER", "")

if not LOCATION_ID:
    print("ERROR: GHL_LOCATION_ID is not set.")
    print("Copy .env.example to .env, fill in your credentials, then run:")
    print('  export $(grep -v "^#" .env | xargs)')
    print("  python3 campaigns/my-campaign.py")
    sys.exit(1)

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
    print(f"My Campaign — {len(CAMPAIGN)} workflows, {total_steps} steps\n")

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
        folder_name="My Campaign",
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
