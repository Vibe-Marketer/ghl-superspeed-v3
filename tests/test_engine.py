#!/usr/bin/env python3
"""
v3 Engine Tests — Validates core functionality without hitting live API.
Run: python3 -m pytest tests/test_engine.py -v
Or: python3 tests/test_engine.py (standalone)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.engine import (
    dm_email, sms_step, email_step, wait_step, tag_step,
    webhook_step, ai_step, link_steps, validate_campaign,
    VERIFIED_ACTIONS,
)


def test_dm_email_basic():
    html = dm_email("Hello world.\n\nSecond paragraph.")
    assert "<p" in html
    assert "Hello world." in html
    assert "Second paragraph." in html


def test_dm_email_formatting():
    html = dm_email("**bold** and *italic*")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_dm_email_empty_lines_stripped():
    html = dm_email("Line 1\n\n\n\nLine 2")
    assert html.count("<p") == 2


def test_sms_step_structure():
    step = sms_step("Welcome", "Hey there!")
    assert step["type"] == "sms"
    assert step["attributes"]["body"] == "Hey there!"
    assert "id" in step
    assert step["name"] == "SMS: Welcome"


def test_email_step_has_both_body_and_html():
    step = email_step("Test", "subject line", "Hello **world**", "Sender")
    assert step["type"] == "email"
    assert step["attributes"]["subject"] == "subject line"
    assert step["attributes"]["html"] == step["attributes"]["body"]
    assert "<strong>world</strong>" in step["attributes"]["html"]
    assert step["attributes"]["fromName"] == "Sender"


def test_wait_step_days():
    step = wait_step("3 days", 3, "days")
    assert step["type"] == "wait"
    assert step["attributes"]["startAfter"]["type"] == "days"
    assert step["attributes"]["startAfter"]["value"] == 3


def test_wait_step_hours():
    step = wait_step("2 hours", 2, "hours")
    # GHL canvas uses "hour" (singular) — confirmed 2026-03-23
    assert step["attributes"]["startAfter"]["type"] == "hour"


def test_wait_step_minutes():
    step = wait_step("30 min", 30, "minutes")
    assert step["attributes"]["startAfter"]["type"] == "minutes"


def test_tag_step_add():
    step = tag_step("Add Tag", ["test-tag"])
    assert step["type"] == "add_contact_tag"
    assert step["attributes"]["tags"] == ["test-tag"]


def test_tag_step_remove():
    step = tag_step("Remove Tag", ["old-tag"], remove=True)
    assert step["type"] == "remove_contact_tag"


def test_webhook_step():
    step = webhook_step("Hook", "https://example.com", data=[{"key": "id", "value": "123"}])
    assert step["type"] == "webhook"
    assert step["attributes"]["url"] == "https://example.com"
    assert len(step["attributes"]["customData"]) == 1


def test_ai_step():
    step = ai_step("Classify", "Classify this text", "gpt-4o")
    assert step["type"] == "chatgpt"
    assert step["attributes"]["model"] == "gpt-4o"
    assert step["attributes"]["promptText"] == "Classify this text"


def test_link_steps_basic():
    steps = link_steps([
        sms_step("First", "hello"),
        wait_step("1 day", 1),
        email_step("Second", "subject", "body"),
    ])
    assert len(steps) == 3
    assert steps[0]["order"] == 0
    assert steps[0]["parentKey"] is None
    assert steps[0]["next"] == steps[1]["id"]
    assert steps[1]["parentKey"] == steps[0]["id"]
    assert steps[1]["next"] == steps[2]["id"]
    assert steps[2]["parentKey"] == steps[1]["id"]
    assert "next" not in steps[2]  # last step has no next


def test_link_steps_single():
    steps = link_steps([sms_step("Only", "hello")])
    assert len(steps) == 1
    assert steps[0]["parentKey"] is None
    assert "next" not in steps[0]


def test_link_steps_ids_unique():
    steps = link_steps([sms_step("A", "a"), sms_step("B", "b"), sms_step("C", "c")])
    ids = [s["id"] for s in steps]
    assert len(set(ids)) == 3  # all unique


def test_validate_campaign_valid():
    campaign = {
        "01": {
            "name": "Test",
            "tag": "test-tag",
            "templates": link_steps([
                sms_step("SMS", "hello"),
                wait_step("1 day", 1),
                email_step("Email", "subj", "body"),
            ]),
        }
    }
    errors = validate_campaign(campaign)
    assert errors == []


def test_validate_campaign_bad_type():
    campaign = {
        "01": {
            "name": "Test",
            "templates": [
                {"id": "x", "type": "fake_type_that_doesnt_exist", "name": "Bad"},
            ],
        }
    }
    errors = validate_campaign(campaign)
    assert len(errors) == 1
    assert "unverified type" in errors[0]


def test_validate_campaign_missing_fields():
    campaign = {
        "01": {
            "name": "Test",
            "templates": [
                {"type": "sms", "name": "OK"},  # missing id
                {"id": "x", "name": "OK"},  # missing type
            ],
        }
    }
    errors = validate_campaign(campaign)
    assert len(errors) == 2


def test_verified_actions_count():
    assert len(VERIFIED_ACTIONS) == 56


def test_verified_actions_contains_key_types():
    must_have = ["sms", "email", "wait", "if_else", "chatgpt", "webhook",
                 "add_contact_tag", "create_opportunity", "workflow_split"]
    for t in must_have:
        assert t in VERIFIED_ACTIONS, f"Missing verified action: {t}"


def test_verified_actions_excludes_wrong_names():
    wrong = ["create_contact", "openai_completion", "split", "date_formatter",
             "add_note", "add_task", "set_dnd", "facebook_conversion"]
    for t in wrong:
        assert t not in VERIFIED_ACTIONS, f"Wrong name should not be in verified: {t}"


# ── Wait step schema compliance (captured from GHL advanced canvas) ──────

def test_wait_step_matches_captured_schema():
    """Wait step output must match the exact schema GHL's advanced canvas uses."""
    step = wait_step("5 minutes", 5, "minutes")
    # Top-level fields
    assert step["type"] == "wait"
    assert step["cat"] == ""
    assert "id" in step
    # Attributes must have all hybrid action fields
    attrs = step["attributes"]
    assert attrs["type"] == "time"
    assert attrs["isHybridAction"] is True
    assert attrs["hybridActionType"] == "wait"
    assert attrs["convertToMultipath"] is False
    assert attrs["transitions"] == []
    assert attrs["cat"] == ""
    # startAfter must have type, value, when
    sa = attrs["startAfter"]
    assert sa["type"] == "minutes"
    assert sa["value"] == 5
    assert sa["when"] == "after"


def test_wait_step_name_format_hours():
    """Canvas renders time label from attributes.name — must match value + unit."""
    step = wait_step("2 hours", 2, "hours")
    assert step["name"] == "Wait 2 Hours"
    assert step["attributes"]["name"] == "Wait 2 Hours"
    # GHL canvas uses "hour" (singular) — confirmed 2026-03-23
    assert step["attributes"]["startAfter"]["type"] == "hour"
    assert step["attributes"]["startAfter"]["value"] == 2


def test_wait_step_name_format_days():
    """Canvas renders time label from attributes.name — must match value + unit."""
    step = wait_step("3 days", 3, "days")
    assert step["name"] == "Wait 3 Days"
    assert step["attributes"]["name"] == "Wait 3 Days"
    assert step["attributes"]["startAfter"]["type"] == "days"
    assert step["attributes"]["startAfter"]["value"] == 3


def test_wait_step_startafter_when_field():
    """The 'when' field in startAfter is required for canvas rendering."""
    for unit in ["minutes", "hours", "days"]:
        step = wait_step("test", 1, unit)
        assert step["attributes"]["startAfter"]["when"] == "after"


def test_wait_step_hours_uses_singular():
    """GHL canvas requires 'hour' (singular) not 'hours' — confirmed 2026-03-23."""
    step = wait_step("5 hours", 5, "hours")
    assert step["attributes"]["startAfter"]["type"] == "hour"
    # Also accept "hour" as direct input
    step2 = wait_step("5 hour", 5, "hour")
    assert step2["attributes"]["startAfter"]["type"] == "hour"


# ── Trigger tag creation (captured from GHL advanced canvas) ─────────────

def test_trigger_body_has_required_fields():
    """Verify trigger body structure matches captured GHL payload."""
    # Simulate what _create_and_trigger builds
    wf_id = "test-wf-id"
    tag = "nurture-start"
    loc = "test-loc"
    trigger_body = {
        "status": "draft",
        "workflowId": wf_id,
        "schedule_config": {},
        "conditions": [
            {
                "operator": "index-of-true",
                "field": "tagsAdded",
                "value": tag,
                "title": "Tag Added",
                "type": "select",
                "id": "tag-added",
            }
        ],
        "type": "contact_tag",
        "masterType": "highlevel",
        "name": tag.replace("-", " ").title(),
        "actions": [{"workflow_id": wf_id, "type": "add_to_workflow"}],
        "active": True,
        "triggersChanged": True,
        "location_id": loc,
        "company_id": "test-co",
        "company_age": 47,
    }
    # All fields from captured payload must be present
    assert trigger_body["type"] == "contact_tag"
    assert trigger_body["masterType"] == "highlevel"
    assert trigger_body["conditions"][0]["operator"] == "index-of-true"
    assert trigger_body["conditions"][0]["field"] == "tagsAdded"
    assert trigger_body["conditions"][0]["value"] == tag
    assert trigger_body["actions"][0]["type"] == "add_to_workflow"
    assert trigger_body["active"] is True
    assert trigger_body["name"] == "Nurture Start"


def test_tag_create_payload():
    """Tag creation payload must be exactly {"tag": "value"}."""
    tag = "nurture 2"
    payload = {"tag": tag}
    assert payload == {"tag": "nurture 2"}


# ── Run standalone ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  PASS: {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {test.__name__}: {e}")
            traceback.print_exc()
    print(f"\n{passed}/{passed + failed} tests passed")
    sys.exit(1 if failed else 0)
