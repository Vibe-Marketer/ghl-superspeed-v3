#!/usr/bin/env python3
"""
PHASE 1: Individual verification of every action type and trigger type.
Tests each one in its own workflow so failures are isolated.

Usage:
    export GHL_FIREBASE_TOKEN=$(curl -s "https://dlf-agency.skool-203.workers.dev/cli/token?pin=YOUR_PIN" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    python3 tests/verify_individual.py
"""

import json, sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.engine import TokenManager, GHLClient
from concurrent.futures import ThreadPoolExecutor, as_completed

LOC = "2hP6rCb3COd2HUjD25w2"
PARENT_FOLDER = "ca2666ec-84af-4155-9d0a-1774430c98b7"
USER = "YewkebOufK3hmeP1gx4B"

def uid():
    return str(uuid.uuid4())

# ── ALL 56 ACTION TYPES with minimal valid attributes ──────────────────────
ACTIONS = [
    ("sms", {"body": "test", "attachments": []}),
    ("email", {"subject": "test", "html": "<p>test</p>", "body": "<p>test</p>", "fromName": "", "attachments": [], "conditions": [], "trackingOptions": {"hasTrackingLinks": False, "hasUtmTracking": False, "hasTags": False}}),
    ("call", {}),
    ("voicemail", {}),
    ("messenger", {"body": "test", "attachments": []}),
    ("gmb", {"body": "test"}),
    ("internal_notification", {"type": "email"}),
    ("instagram-dm", {"body": "test"}),
    ("review_request", {}),
    ("respond_on_comment", {"commentResponse": [{"comment": "Thanks!"}], "likeComment": True}),
    ("add_contact_tag", {"tags": ["verify-action"]}),
    ("remove_contact_tag", {"tags": ["verify-action"]}),
    ("update_contact_field", {"fields": [{"field": "first_name", "value": "Test", "title": "First Name", "type": "TEXT"}]}),
    ("create_update_contact", {"fields": [{"field": "email", "value": "test@test.com", "title": "Email", "type": "TEXT"}]}),
    ("assign_user", {"userId": USER}),
    ("remove_assigned_user", {}),
    ("edit_conversation", {"action": "mark_read"}),
    ("dnd_contact", {"dnd_contact": "enable"}),
    ("add_notes", {"body": "test note"}),
    ("task-notification", {"title": "Test Task", "body": "test task body"}),
    ("find_contact", {}),
    ("wait", {"type": "time", "startAfter": {"type": "minutes", "value": 5, "when": "after"}, "name": "Wait 5 Minutes", "cat": "", "isHybridAction": True, "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}),
    ("add_to_workflow", {"workflowId": ""}),
    ("remove_from_workflow", {"workflowId": ""}),
    ("remove_from_all_workflows", {}),
    ("drip", {"type": "specific_time", "days": ["monday"], "time": "09:00", "timezone": "account"}),
    ("update_custom_value", {}),
    ("if_else", {"if": True, "conditionName": "Condition", "operator": "and", "version": 2, "branches": [{"id": uid(), "name": "Branch A", "segments": [{"operator": "and", "conditions": []}]}]}),
    ("workflow_split", {"type": "workflow_split", "condition": "random-split"}),
    ("workflow_goal", {"action": "end", "segments": [{"operator": "and", "conditions": []}]}),
    ("chatgpt", {"type": "chatgpt", "event": "simple-prompt", "model": "gpt-4o", "promptText": "test", "actionType": "custom", "temperature": "0.2", "memoryKey": "action"}),
    ("conversation_ai", {"type": "conversation_ai"}),
    ("webhook", {"method": "POST", "url": "https://httpbin.org/post", "customData": [], "headers": []}),
    ("custom_webhook", {"method": "POST", "url": "https://httpbin.org/post", "customData": [], "headers": []}),
    ("google_sheets", {"spreadsheetId": "", "sheetName": "", "action": "create_row"}),
    ("slack_message", {"channel": "", "message": "test"}),
    ("custom_code", {"code": "return { success: true };", "language": "javascript"}),
    ("facebook_conversion_api", {"eventName": "Lead"}),
    ("stripe_one_time_charge", {"amount": "100", "currency": "usd", "description": "test"}),
    ("update_appointment_status", {"status": "confirmed"}),
    ("math_operation", {"expression": "1+1", "resultKey": "math_result"}),
    ("text_formatter", {"action": "uppercase", "input": "test"}),
    ("number_formatter", {"action": "format", "input": "1234.5"}),
    ("datetime_formatter", {"action": "format", "input": "now"}),
    ("array_functions", {"action": "length", "input": "[]"}),
    ("fb_interactive_messenger", {"message": "Choose:", "actionType": "quick_reply", "timeout": 60, "transitions": []}),
    ("ig_interactive_messenger", {"message": "Choose:", "actionType": "quick_reply", "timeout": 60, "transitions": []}),
    ("ivr_gather", {}),
    ("ivr_connect_call", {}),
    ("membership_grant_offer", {}),
    ("membership_revoke_offer", {}),
    ("create_opportunity", {}),
    ("find_opportunity", {"pipeline_id": ""}),
    ("remove_opportunity", {}),
    # Structural types (need parent, tested separately)
    ("goto", {"targetNodeId": "", "type": "goto"}),
    ("transition", {}),
]

# ── ALL 54 TRIGGER TYPES with corrected API values ──────────────────────────
TRIGGERS = [
    # (api_value, display_name, conditions)
    ("contact_tag", "Contact Tag", [{"operator": "index-of-true", "field": "tagsAdded", "value": "verify-trigger", "title": "Tag Added", "type": "select", "id": "tag-added"}]),
    ("contact_created", "Contact Created", []),
    ("contact_changed", "Contact Changed", []),
    ("dnd_contact", "Contact DND", []),
    ("birthday_reminder", "Birthday Reminder", []),
    ("customer_reply", "Customer Reply", []),
    ("call_status", "Call Status", []),
    ("mailgun_email_event", "Email Event", []),
    ("form_submission", "Form Submitted", []),
    ("survey_submission", "Survey Submitted", []),
    ("appointment", "Appointment Status", []),
    ("customer_appointment", "Customer Booked Appt", []),
    ("opportunity_status_changed", "Opp Status Changed", []),
    ("opportunity_created", "Opp Created", []),
    ("opportunity_changed", "Opp Changed", []),
    ("pipeline_stage_updated", "Pipeline Stage", []),
    ("opportunity_decay", "Stale Opp", []),
    ("payment_received", "Payment Received", []),
    ("invoice", "Invoice", []),
    ("order_submission", "Order Submitted", []),
    ("two_step_form_submission", "Order Form", []),
    ("note_add", "Note Added", []),
    ("note_changed", "Note Changed", []),
    ("task_added", "Task Added", []),
    ("task_due_date_reminder", "Task Reminder", []),
    ("trigger_link", "Link Clicked", []),
    ("video_event", "Video Tracking", []),
    ("facebook_lead_gen", "FB Lead Form", []),
    ("tik_tok_form_submitted", "TikTok Form", []),
    ("facebook_comment_on_post", "FB Comment", []),
    ("ig_comment_on_post", "IG Comment", []),
    ("membership_contact_created", "Membership Signup", []),
    ("category_started", "Category Started", []),
    ("category_completed", "Category Completed", []),
    ("lesson_started", "Lesson Started", []),
    ("lesson_completed", "Lesson Completed", []),
    ("offer_access_granted", "Offer Granted", []),
    ("offer_access_removed", "Offer Removed", []),
    ("product_access_granted", "Product Granted", []),
    ("product_access_removed", "Product Removed", []),
    ("product_started", "Product Started", []),
    ("product_completed", "Product Completed", []),
    ("user_log_in", "User Login", []),
    ("affiliate_created", "Affiliate Created", []),
    ("inbound_webhook", "Inbound Webhook", []),
    ("custom_date_reminder", "Custom Date Reminder", []),
    ("scheduler_trigger", "Scheduler", []),
    ("validation_error", "Number Validation", []),
    ("ivr_incoming_call", "Start IVR", []),
    ("custom_object_created", "Object Created", []),
    ("custom_object_changed", "Object Changed", []),
    ("shopify_abandoned_cart", "Abandoned Checkout", []),
    ("shopify_order_placed", "Order Placed", []),
    ("shopify_order_fulfilled", "Order Fulfilled", []),
]


def test_action(client, folder_id, type_str, attrs):
    """Test a single action type. Returns (type_str, pass/fail, error_msg)."""
    step = {
        "id": uid(), "type": type_str,
        "name": f"[{type_str}]", "order": 0, "cat": "",
        "attributes": attrs,
    }
    # Create workflow
    wf = client.request("POST", f"/workflow/{LOC}", {"name": f"ACT: {type_str}", "parentId": folder_id})
    if not wf or not wf.get("id"):
        return type_str, "FAIL", "create failed"
    wf_id = wf["id"]

    # Save step
    result = client.request("PUT", f"/workflow/{LOC}/{wf_id}", {
        "name": f"ACT: {type_str}", "version": 1,
        "workflowData": {"templates": [step]}
    })
    if result and not result.get("_error"):
        return type_str, "PASS", wf_id
    else:
        msg = result.get("message", "unknown error")[:120] if result else "no response"
        # Delete failed workflow
        client.request("DELETE", f"/workflow/{LOC}/{wf_id}")
        return type_str, "FAIL", msg


def test_trigger(client, folder_id, api_value, display_name, conditions):
    """Test a single trigger type. Returns (api_value, pass/fail, error_msg)."""
    # Create workflow with a simple SMS step
    wf = client.request("POST", f"/workflow/{LOC}", {"name": f"TRG: {api_value}", "parentId": folder_id})
    if not wf or not wf.get("id"):
        return api_value, "FAIL", "create failed"
    wf_id = wf["id"]

    # Save a step first
    step_id = uid()
    client.request("PUT", f"/workflow/{LOC}/{wf_id}", {
        "name": f"TRG: {api_value}", "version": 1,
        "workflowData": {"templates": [{"id": step_id, "type": "sms", "name": "placeholder", "order": 0, "cat": "", "attributes": {"body": "test", "attachments": []}}]}
    })

    # Create trigger with corrected API value
    trigger_body = {
        "status": "draft", "workflowId": wf_id,
        "schedule_config": {}, "conditions": conditions,
        "type": api_value, "masterType": "highlevel",
        "name": f"[{api_value}] {display_name}",
        "actions": [{"workflow_id": wf_id, "type": "add_to_workflow"}],
        "active": True, "triggersChanged": True,
        "location_id": LOC,
    }
    tr = client.request("POST", f"/workflow/{LOC}/trigger", trigger_body)
    if tr and tr.get("id"):
        # Update with targetActionId
        client.request("PUT", f"/workflow/{LOC}/trigger/{tr['id']}", {
            **trigger_body,
            "targetActionId": step_id,
            "advanceCanvasMeta": {"position": {"x": 57.5, "y": -73}},
        })
        return api_value, "PASS", f"wf={wf_id} tr={tr['id']}"
    else:
        msg = tr.get("message", "unknown")[:120] if tr else "no response"
        return api_value, "FAIL", msg


def main():
    start = time.time()
    tm = TokenManager(LOC)
    if os.environ.get("GHL_FIREBASE_REFRESH_TOKEN"):
        tm.set_refresh_token(os.environ["GHL_FIREBASE_REFRESH_TOKEN"])
    client = GHLClient(tm, LOC)

    print("Auth check...")
    token = tm.get_token()
    if not token:
        print("FATAL: No token"); sys.exit(1)
    print("OK\n")

    # Create test folders
    act_folder = client.request("POST", f"/workflow/{LOC}", {"name": "__ VERIFY ACTIONS", "type": "directory", "parentId": PARENT_FOLDER})
    trg_folder = client.request("POST", f"/workflow/{LOC}", {"name": "__ VERIFY TRIGGERS", "type": "directory", "parentId": PARENT_FOLDER})
    act_fid = act_folder.get("id") if act_folder else None
    trg_fid = trg_folder.get("id") if trg_folder else None

    if not act_fid or not trg_fid:
        print("FATAL: Can't create folders"); sys.exit(1)

    # Create verify tag
    client.request("POST", f"/workflow/{LOC}/tags/create", {"tag": "verify-trigger"})
    client.request("POST", f"/workflow/{LOC}/tags/create", {"tag": "verify-action"})

    # ── TEST ACTIONS (parallel, 5 at a time) ────────────────────────────
    print(f"{'='*70}")
    print(f"TESTING {len(ACTIONS)} ACTION TYPES")
    print(f"{'='*70}\n")

    action_results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {
            pool.submit(test_action, client, act_fid, t, a): t
            for t, a in ACTIONS
        }
        for future in as_completed(futures):
            type_str, status, detail = future.result()
            action_results.append((type_str, status, detail))
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"  {icon}: {type_str:35s} {detail[:60]}")

    # ── TEST TRIGGERS (parallel, 5 at a time) ───────────────────────────
    print(f"\n{'='*70}")
    print(f"TESTING {len(TRIGGERS)} TRIGGER TYPES (corrected API values)")
    print(f"{'='*70}\n")

    trigger_results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {
            pool.submit(test_trigger, client, trg_fid, v, n, c): v
            for v, n, c in TRIGGERS
        }
        for future in as_completed(futures):
            api_val, status, detail = future.result()
            trigger_results.append((api_val, status, detail))
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"  {icon}: {api_val:35s} {detail[:60]}")

    # ── SUMMARY ─────────────────────────────────────────────────────────
    elapsed = time.time() - start
    act_pass = sum(1 for _, s, _ in action_results if s == "PASS")
    act_fail = sum(1 for _, s, _ in action_results if s == "FAIL")
    trg_pass = sum(1 for _, s, _ in trigger_results if s == "PASS")
    trg_fail = sum(1 for _, s, _ in trigger_results if s == "FAIL")

    print(f"\n{'='*70}")
    print(f"RESULTS — {elapsed:.1f}s")
    print(f"{'='*70}")
    print(f"  Actions:  {act_pass} PASS / {act_fail} FAIL (of {len(ACTIONS)})")
    print(f"  Triggers: {trg_pass} PASS / {trg_fail} FAIL (of {len(TRIGGERS)})")
    print(f"  API calls: {client.call_count}")

    if act_fail:
        print(f"\n  FAILED ACTIONS:")
        for t, s, d in sorted(action_results):
            if s == "FAIL":
                print(f"    {t}: {d}")

    if trg_fail:
        print(f"\n  FAILED TRIGGERS:")
        for t, s, d in sorted(trigger_results):
            if s == "FAIL":
                print(f"    {t}: {d}")

    print(f"\n  Folders in GHL:")
    print(f"    Actions: https://app.gohighlevel.com/location/{LOC}/automation")
    print(f"    Look in ++ Agent Testing > __ VERIFY ACTIONS / __ VERIFY TRIGGERS")

    # Save results to JSON
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(elapsed, 1),
        "actions": {t: {"status": s, "detail": d} for t, s, d in action_results},
        "triggers": {t: {"status": s, "detail": d} for t, s, d in trigger_results},
        "summary": {
            "actions_pass": act_pass, "actions_fail": act_fail,
            "triggers_pass": trg_pass, "triggers_fail": trg_fail,
        }
    }
    outpath = os.path.join(os.path.dirname(__file__), '..', 'results', 'verify_individual.json')
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {outpath}")


if __name__ == "__main__":
    main()
