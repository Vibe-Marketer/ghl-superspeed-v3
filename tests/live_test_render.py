#!/usr/bin/env python3
"""
Live render test — creates a workflow via the full engine pipeline
(create → tag → trigger → PUT steps → auto-save) and prints the
GHL URLs for manual visual verification.

Requires: GHL_FIREBASE_TOKEN or GHL_FIREBASE_REFRESH_TOKEN env var.

Usage: python3 tests/live_test_render.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.engine import (
    TokenManager, GHLClient, CampaignBuilder,
    wait_step, tag_step, sms_step, link_steps,
)

LOC = os.environ.get("GHL_LOCATION_ID", "")
COMPANY = os.environ.get("GHL_COMPANY_ID", "")
USER = os.environ.get("GHL_USER_ID", "")
TEST_FOLDER = os.environ.get("GHL_TEST_FOLDER", "")

if not all([LOC, COMPANY, USER, TEST_FOLDER]):
    sys.exit("ERROR: Missing env vars. Run: python3 scripts/setup-account.py <account> "
             "then: export $(grep -v '^#' .env.<account> | xargs)")

def main():
    # Auth
    tm = TokenManager(LOC)
    refresh = os.environ.get("GHL_FIREBASE_REFRESH_TOKEN", "")
    if refresh:
        tm.set_refresh_token(refresh)

    client = GHLClient(tm, LOC)

    # Quick auth test
    print("Testing auth...")
    token = tm.get_token()
    if not token:
        print("FATAL: No token available")
        sys.exit(1)
    print(f"  Token: ...{token[-20:]}")

    # Build a test campaign with all 3 wait units + trigger
    campaign = {
        "render_test": {
            "name": "__RENDER TEST: Min+Hours+Days",
            "tag": "render-test-tag",
            "templates": link_steps([
                wait_step("5 min", 5, "minutes"),
                wait_step("2 hours", 2, "hours"),
                wait_step("3 days", 3, "days"),
                sms_step("Done", "Render test complete"),
            ]),
        }
    }

    # Build using full pipeline (includes auto-save)
    builder = CampaignBuilder(client, LOC)
    stats = builder.build(
        campaign,
        folder_name="__Render Test",
        parent_folder=TEST_FOLDER,
        company_id=COMPANY,
        user_id=USER,
    )

    # Print verification URLs
    print("\n" + "=" * 60)
    print("VERIFY THESE IN YOUR BROWSER:")
    print("=" * 60)
    for key, wf_def in campaign.items():
        # Get workflow ID from stats
        pass

    # The build() method prints URLs already, but let's also print the advanced canvas URLs
    print("\nCheck the ++ Agent Testing > __Render Test folder in GHL")
    print(f"Location: https://app.gohighlevel.com/location/{LOC}/automation")
    print(f"\nExpected rendering:")
    print(f"  1. Trigger: 'Render Test Tag' with tag 'render-test-tag'")
    print(f"  2. Wait: '5 Minutes'")
    print(f"  3. Wait: '2 Hours'")
    print(f"  4. Wait: '3 Days'")
    print(f"  5. SMS: 'Done'")
    print(f"\nAPI calls: {stats.get('api_calls', '?')}")
    print(f"Errors: {stats.get('errors', [])}")

if __name__ == "__main__":
    main()
