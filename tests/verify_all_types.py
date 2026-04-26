#!/usr/bin/env python3
"""
FULL VERIFICATION: Creates 6 workflows covering all 56 action types and 44 trigger types.
Each workflow has ~10 actions + ~8 triggers, none repeating.
Designed for visual inspection in GHL UI.

Usage:
    export GHL_FIREBASE_TOKEN=$(curl -s "$GHL_TOKEN_SERVER/cli/token?pin=$GHL_ADMIN_PIN" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    python3 tests/verify_all_types.py
"""

import json, sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.engine import TokenManager, GHLClient

LOC = os.environ.get("GHL_LOCATION_ID", "")
COMPANY = os.environ.get("GHL_COMPANY_ID", "")
USER = os.environ.get("GHL_USER_ID", "")
PARENT_FOLDER = os.environ.get("GHL_TEST_FOLDER", "")  # Tests land in TEST WORKFLOWS folder

if not all([LOC, COMPANY, USER, PARENT_FOLDER]):
    sys.exit("ERROR: Missing env vars. Run: python3 scripts/setup-account.py <account> "
             "then: export $(grep -v '^#' .env.<account> | xargs)")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'ghl-automation-builder', 'templates', 'actions')

# ── All 56 verified action types ──────────────────────────────────────────
# Grouped into 6 batches of ~10, ordered by complexity (simple first)

ACTION_BATCHES = [
    # Batch 1: Communication basics
    [
        ("sms", "Send SMS", {"body": "Verification test SMS", "attachments": []}),
        ("email", "Send Email", {"subject": "Verification Test", "html": "<p>Test email body</p>", "body": "<p>Test email body</p>", "fromName": "Test", "attachments": [], "conditions": [], "trackingOptions": {"hasTrackingLinks": False, "hasUtmTracking": False, "hasTags": False}}),
        ("call", "Make Call", {}),
        ("voicemail", "Voicemail Drop", {}),
        ("messenger", "FB Messenger", {"body": "Test messenger", "attachments": []}),
        ("gmb", "Google Business", {"body": "Test GMB message"}),
        ("internal_notification", "Internal Notification", {"type": "email"}),
        ("instagram-dm", "Instagram DM", {"body": "Test IG DM"}),
        ("review_request", "Review Request", {}),
        ("respond_on_comment", "Respond On Comment", {"commentResponse": [{"comment": "Thanks!"}], "likeComment": True}),
    ],
    # Batch 2: Contact management
    [
        ("add_contact_tag", "Add Tag", {"tags": ["verify-test-1"]}),
        ("remove_contact_tag", "Remove Tag", {"tags": ["verify-test-1"]}),
        ("update_contact_field", "Update Field", {"fields": [{"field": "first_name", "value": "Test", "title": "First Name", "type": "TEXT"}]}),
        ("create_update_contact", "Create/Update Contact", {"fields": [{"field": "email", "value": "test@example.com", "title": "Email", "type": "TEXT"}]}),
        ("assign_user", "Assign User", {"userId": USER}),
        ("remove_assigned_user", "Remove User", {}),
        ("edit_conversation", "Edit Conversation", {"action": "mark_read"}),
        ("dnd_contact", "DND Contact", {"dnd_contact": "enable"}),
        ("add_notes", "Add Note", {"body": "Verification test note"}),
        ("task-notification", "Add Task", {"title": "Verify Task", "body": "Verification test task"}),
    ],
    # Batch 3: Workflow control
    [
        ("wait", "Wait 5 Min", {"type": "time", "startAfter": {"type": "minutes", "value": 5, "when": "after"}, "name": "Wait 5 Minutes", "cat": "", "isHybridAction": True, "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}),
        ("wait", "Wait 2 Hour", {"type": "time", "startAfter": {"type": "hour", "value": 2, "when": "after"}, "name": "Wait 2 Hour", "cat": "", "isHybridAction": True, "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}),
        ("wait", "Wait 3 Days", {"type": "time", "startAfter": {"type": "days", "value": 3, "when": "after"}, "name": "Wait 3 Days", "cat": "", "isHybridAction": True, "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}),
        ("add_to_workflow", "Add To Workflow", {"workflowId": ""}),
        ("remove_from_workflow", "Remove From Workflow", {"workflowId": ""}),
        ("remove_from_all_workflows", "Remove From All", {}),
        ("find_contact", "Find Contact", {}),
        ("drip", "Drip Mode", {"type": "specific_time", "days": ["monday"], "time": "09:00", "timezone": "account"}),
        ("update_custom_value", "Update Custom Value", {}),
        ("goto", "Go To", {"targetNodeId": "", "type": "goto"}),
    ],
    # Batch 4: AI + Integrations
    [
        ("chatgpt", "AI Prompt", {"type": "chatgpt", "event": "simple-prompt", "model": "gpt-4o", "promptText": "Say hello", "actionType": "custom", "temperature": "0.2", "memoryKey": "action"}),
        ("conversation_ai", "Conversation AI", {"type": "conversation_ai"}),
        ("webhook", "Webhook", {"method": "POST", "url": "https://httpbin.org/post", "customData": [], "headers": []}),
        ("custom_webhook", "Custom Webhook", {"method": "POST", "url": "https://httpbin.org/post", "customData": [], "headers": []}),
        ("google_sheets", "Google Sheets", {"spreadsheetId": "", "sheetName": "", "action": "create_row"}),
        ("slack_message", "Slack Message", {"channel": "", "message": "Verification test"}),
        ("custom_code", "Custom Code", {"code": "return { success: true };", "language": "javascript"}),
        ("facebook_conversion_api", "FB Conversion API", {"eventName": "Lead"}),
        ("stripe_one_time_charge", "Stripe Charge", {"amount": "100", "currency": "usd", "description": "Verify test"}),
        ("update_appointment_status", "Update Appointment", {"status": "confirmed"}),
    ],
    # Batch 5: Formatters + Interactive
    [
        ("math_operation", "Math Operation", {"expression": "1+1", "resultKey": "math_result"}),
        ("text_formatter", "Text Formatter", {"action": "uppercase", "input": "test"}),
        ("number_formatter", "Number Formatter", {"action": "format", "input": "1234.5"}),
        ("datetime_formatter", "DateTime Formatter", {"action": "format", "input": "now"}),
        ("array_functions", "Array Functions", {"action": "length", "input": "[]"}),
        ("fb_interactive_messenger", "FB Interactive", {"message": "Choose:", "actionType": "quick_reply", "timeout": 60, "transitions": []}),
        ("ig_interactive_messenger", "IG Interactive", {"message": "Choose:", "actionType": "quick_reply", "timeout": 60, "transitions": []}),
        ("ivr_gather", "IVR Gather", {}),
        ("ivr_connect_call", "IVR Connect", {}),
        ("membership_grant_offer", "Grant Membership", {}),
    ],
    # Batch 6: Remaining
    [
        ("membership_revoke_offer", "Revoke Membership", {}),
        ("create_opportunity", "Create Opportunity", {}),
        ("find_opportunity", "Find Opportunity", {}),
        ("remove_opportunity", "Remove Opportunity", {}),
        ("workflow_split", "Workflow Split", {"type": "workflow_split", "condition": "random-split"}),
        ("workflow_goal", "Workflow Goal", {"action": "end", "segments": [{"operator": "and", "conditions": []}]}),
    ],
]

# ── All 44 trigger types ──────────────────────────────────────────────────
# Spread across 6 workflows (~7-8 each)

TRIGGER_BATCHES = [
    # Batch 1
    [
        ("contact_tag", "Tag Added", [{"operator": "index-of-true", "field": "tagsAdded", "value": "verify-trigger-1", "title": "Tag Added", "type": "select", "id": "tag-added"}]),
        ("contact_created", "Contact Created", []),
        ("contact_changed", "Contact Changed", []),
        ("contact_dnd", "Contact DND", []),
        ("customer_replied", "Customer Replied", []),
        ("form_submitted", "Form Submitted", []),
        ("survey_submitted", "Survey Submitted", []),
        ("appointment", "Appointment", []),
    ],
    # Batch 2
    [
        ("appointment_status", "Appt Status", []),
        ("opportunity_status_changed", "Opp Status Changed", []),
        ("opportunity_created", "Opp Created", []),
        ("opportunity_changed", "Opp Changed", []),
        ("opportunity_stage_changed", "Opp Stage Changed", []),
        ("pipeline_stage_changed", "Pipeline Stage Changed", []),
        ("stale_opportunity", "Stale Opportunity", []),
        ("payment_received", "Payment Received", []),
    ],
    # Batch 3
    [
        ("invoice_created", "Invoice Created", []),
        ("order_submitted", "Order Submitted", []),
        ("order_status_changed", "Order Status Changed", []),
        ("birthday_reminder", "Birthday Reminder", []),
        ("task_reminder", "Task Reminder", []),
        ("note_added", "Note Added", []),
        ("note_changed", "Note Changed", []),
    ],
    # Batch 4
    [
        ("call_status", "Call Status", []),
        ("email_event", "Email Event", []),
        ("facebook_lead_form", "FB Lead Form", []),
        ("facebook_messenger", "FB Messenger Trigger", []),
        ("instagram_dm", "IG DM Trigger", []),
        ("membership_signup", "Membership Signup", []),
        ("membership_new_signup", "Membership New Signup", []),
    ],
    # Batch 5
    [
        ("membership_category_completed", "Category Complete", []),
        ("membership_lesson_completed", "Lesson Complete", []),
        ("membership_login", "Membership Login", []),
        ("community_member_joined", "Community Joined", []),
        ("review_received", "Review Received", []),
        ("custom_webhook_trigger", "Custom Webhook Trigger", []),
        ("manual_trigger", "Manual Trigger", []),
    ],
    # Batch 6
    [
        ("affiliate_created", "Affiliate Created", []),
        ("affiliate_sale", "Affiliate Sale", []),
        ("twilio_event", "Twilio Event", []),
        ("fb_comment_on_post", "FB Comment", []),
        ("ig_comment_on_post", "IG Comment", []),
        ("google_ad_lead_form", "Google Ad Lead", []),
    ],
]


def uid():
    return str(uuid.uuid4())


def build_steps(batch):
    """Build linked steps from an action batch."""
    steps = []
    for i, (type_str, name, attrs) in enumerate(batch):
        step = {
            "id": uid(),
            "type": type_str,
            "name": f"[{type_str}] {name}",
            "order": i,
            "cat": "",
            "attributes": {**attrs},
        }
        if i > 0:
            step["parentKey"] = steps[i - 1]["id"]
        steps.append(step)
    return steps


def build_triggers(wf_id, batch):
    """Build trigger payloads from a trigger batch."""
    triggers = []
    for type_str, name, conditions in batch:
        triggers.append({
            "status": "draft",
            "workflowId": wf_id,
            "schedule_config": {},
            "conditions": conditions,
            "type": type_str,
            "masterType": "highlevel",
            "name": f"[{type_str}] {name}",
            "actions": [{"workflow_id": wf_id, "type": "add_to_workflow"}],
            "active": True,
            "triggersChanged": True,
            "location_id": LOC,
            "company_id": COMPANY,
            "company_age": 47,
        })
    return triggers


def main():
    start = time.time()

    # Auth
    tm = TokenManager(LOC)
    if os.environ.get("GHL_FIREBASE_REFRESH_TOKEN"):
        tm.set_refresh_token(os.environ["GHL_FIREBASE_REFRESH_TOKEN"])
    client = GHLClient(tm, LOC)

    print("Testing auth...")
    token = tm.get_token()
    if not token:
        print("FATAL: No token")
        sys.exit(1)
    print("Auth OK\n")

    # Create verification folder
    folder_name = f"__ VERIFY ALL ({time.strftime('%H:%M')})"
    folder = client.request("POST", f"/workflow/{LOC}", {"name": folder_name, "type": "directory", "parentId": PARENT_FOLDER})
    folder_id = folder.get("id") if folder else None
    if not folder_id:
        print("FATAL: Couldn't create folder")
        sys.exit(1)
    print(f"Folder: {folder_name} ({folder_id})\n")

    results = {"workflows": 0, "actions_saved": 0, "actions_failed": 0, "triggers_created": 0, "triggers_failed": 0}

    for batch_idx in range(6):
        actions = ACTION_BATCHES[batch_idx]
        triggers = TRIGGER_BATCHES[batch_idx]
        wf_name = f"Verify {batch_idx + 1}/6 — {len(actions)} actions + {len(triggers)} triggers"

        print(f"{'='*60}")
        print(f"Workflow {batch_idx + 1}: {wf_name}")
        print(f"  Actions: {', '.join(a[0] for a in actions)}")
        print(f"  Triggers: {', '.join(t[0] for t in triggers)}")

        # Create workflow
        wf = client.request("POST", f"/workflow/{LOC}", {"name": wf_name, "parentId": folder_id})
        wf_id = wf.get("id") if wf else None
        if not wf_id:
            print(f"  FAILED to create workflow!")
            continue
        results["workflows"] += 1

        # Create tags for tag-based triggers
        for type_str, name, conditions in triggers:
            if type_str == "contact_tag" and conditions:
                tag_val = conditions[0].get("value", "")
                if tag_val:
                    client.request("POST", f"/workflow/{LOC}/tags/create", {"tag": tag_val})

        # Create triggers
        trigger_ids = []
        for trig_body in build_triggers(wf_id, triggers):
            tr = client.request("POST", f"/workflow/{LOC}/trigger", trig_body)
            if tr and tr.get("id"):
                trigger_ids.append(tr["id"])
                results["triggers_created"] += 1
                print(f"  Trigger OK: [{trig_body['type']}] {trig_body['name']}")
            else:
                results["triggers_failed"] += 1
                print(f"  Trigger FAIL: [{trig_body['type']}] {trig_body['name']}")

        # Build and save steps
        steps = build_steps(actions)

        # Update first trigger with targetActionId
        if trigger_ids and steps:
            client.request("PUT", f"/workflow/{LOC}/trigger/{trigger_ids[0]}", {
                "targetActionId": steps[0]["id"],
                "advanceCanvasMeta": {"position": {"x": 57.5, "y": -73}},
                "status": "draft", "workflowId": wf_id,
                "type": triggers[0][0], "masterType": "highlevel",
                "name": f"[{triggers[0][0]}] {triggers[0][1]}",
                "actions": [{"workflow_id": wf_id, "type": "add_to_workflow"}],
                "active": True, "triggersChanged": True,
            })

        # Save steps
        put_body = {"name": wf_name, "version": 1, "workflowData": {"templates": steps}}
        put_result = client.request("PUT", f"/workflow/{LOC}/{wf_id}", put_body)
        if put_result and not put_result.get("_error"):
            results["actions_saved"] += len(steps)
            print(f"  Steps saved: {len(steps)}")
        else:
            results["actions_failed"] += len(steps)
            err_msg = put_result.get("message", "unknown") if put_result else "no response"
            print(f"  Steps FAILED: {err_msg}")

        # Second PUT with trigger sync + canvas meta
        current = client.request("GET", f"/workflow/{LOC}/{wf_id}")
        if current and not current.get("_error"):
            now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            meta = current.get("meta") or {}
            meta["advanceCanvasMeta"] = {"enabled": True, "enabledAt": now}

            # Add canvas positions to steps
            steps_meta = []
            for idx, s in enumerate(steps):
                sm = {**s}
                sm["advanceCanvasMeta"] = {"position": {"x": 400 + idx * 250, "y": 0}}
                steps_meta.append(sm)

            # Build trigger list for Firebase sync
            trigger_list = []
            for i, tid in enumerate(trigger_ids):
                t = triggers[i]
                trigger_list.append({
                    "id": tid,
                    "type": t[0], "masterType": "highlevel",
                    "name": f"[{t[0]}] {t[1]}",
                    "workflow_id": wf_id, "location_id": LOC,
                    "belongs_to": "workflow",
                    "deleted": False, "active": True,
                    "date_added": now, "date_updated": now,
                    "schedule_config": {},
                    "conditions": t[2],
                    "actions": [{"workflow_id": wf_id, "type": "add_to_workflow"}],
                    "advanceCanvasMeta": {"position": {"x": 50 + i * 150, "y": -100}},
                    "status": "draft",
                })
                if i == 0 and steps:
                    trigger_list[-1]["targetActionId"] = steps[0]["id"]

            sync_body = {
                "name": wf_name,
                "version": current.get("version", 2),
                "meta": meta,
                "workflowData": {"templates": steps_meta},
                "triggersChanged": bool(trigger_list),
                "oldTriggers": trigger_list,
                "newTriggers": trigger_list,
            }
            client.request("PUT", f"/workflow/{LOC}/{wf_id}", sync_body)

        print(f"  URL: https://app.gohighlevel.com/location/{LOC}/workflow/{wf_id}/advanced-canvas")
        print()

    elapsed = time.time() - start
    print(f"{'='*60}")
    print(f"VERIFICATION COMPLETE in {elapsed:.1f}s")
    print(f"  Workflows: {results['workflows']}/6")
    print(f"  Actions saved: {results['actions_saved']}/56")
    print(f"  Actions failed: {results['actions_failed']}")
    print(f"  Triggers created: {results['triggers_created']}/44")
    print(f"  Triggers failed: {results['triggers_failed']}")
    print(f"  API calls: {client.call_count}")
    print(f"{'='*60}")
    print(f"\nFolder: {folder_name}")
    print(f"Location: https://app.gohighlevel.com/location/{LOC}/automation")


if __name__ == "__main__":
    main()
