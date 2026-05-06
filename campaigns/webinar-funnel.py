#!/usr/bin/env python3
"""
Reusable webinar funnel campaign.

This template keeps account credentials and campaign copy configurable so it can
be reused across clients without inheriting another business's names, claims, or
offer details.

Usage:
    python3 campaigns/webinar-funnel.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.engine import (
    CampaignBuilder,
    GHLClient,
    TokenManager,
    email_step,
    link_steps,
    sms_step,
    wait_step,
)


def env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip() or default


# Account config. These should come from .env.<account> via setup-account.py.
LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")
COMPANY_ID = os.environ.get("GHL_COMPANY_ID", "")
USER_ID = os.environ.get("GHL_USER_ID", "")
PARENT_FOLDER = os.environ.get("GHL_PARENT_FOLDER", "")

if not all([LOCATION_ID, COMPANY_ID, USER_ID]):
    sys.exit(
        "ERROR: Missing env vars. Run: python3 scripts/setup-account.py <account> "
        "then: set -a && source .env.<account> && set +a"
    )


# Campaign config. Override any of these in .env.<account> or the shell.
BUSINESS_NAME = env("CAMPAIGN_BUSINESS_NAME", "Your Business")
SENDER_NAME = env("CAMPAIGN_SENDER_NAME", "Your Team")
AUDIENCE_LABEL = env("CAMPAIGN_AUDIENCE_LABEL", "business owners")
INDUSTRY_LABEL = env("CAMPAIGN_INDUSTRY_LABEL", "business")
SERVICE_CATEGORY = env("CAMPAIGN_SERVICE_CATEGORY", "your services")

WEBINAR_TITLE = env("CAMPAIGN_WEBINAR_TITLE", "The Growth System Workshop")
WEBINAR_DAY = env("CAMPAIGN_WEBINAR_DAY", "Thursday")
WEBINAR_TIME = env("CAMPAIGN_WEBINAR_TIME", "7 PM ET")
WEBINAR_DURATION = env("CAMPAIGN_WEBINAR_DURATION", "60 minutes")
WEBINAR_LINK = env("CAMPAIGN_WEBINAR_LINK", "{{custom_values.webinar_link}}")
REPLAY_WINDOW = env("CAMPAIGN_REPLAY_WINDOW", "72 hours")
REGISTRATION_KEYWORD = env("CAMPAIGN_REGISTRATION_KEYWORD", "WEBINAR")

OFFER_NAME = env("CAMPAIGN_OFFER_NAME", "Implementation Program")
OFFER_OUTCOME = env(
    "CAMPAIGN_OFFER_OUTCOME",
    "turn new inquiries into booked conversations with a clear follow-up system",
)
BONUS_NAME = env("CAMPAIGN_BONUS_NAME", "Implementation Blueprint")
BONUS_COPY = env(
    "CAMPAIGN_BONUS_COPY",
    "a practical checklist for launching the system after the workshop",
)
PRICE_TEXT = env("CAMPAIGN_PRICE_TEXT", "your enrollment option")
DEADLINE_TEXT = env("CAMPAIGN_DEADLINE_TEXT", "Sunday at midnight")

CASE_STUDY_LABEL = env("CAMPAIGN_CASE_STUDY_LABEL", "a recent client")
CASE_STUDY_BEFORE = env("CAMPAIGN_CASE_STUDY_BEFORE", "had leads coming in inconsistently")
CASE_STUDY_AFTER = env(
    "CAMPAIGN_CASE_STUDY_AFTER",
    "created a repeatable follow-up process and booked more qualified conversations",
)
CASE_STUDY_LESSON = env(
    "CAMPAIGN_CASE_STUDY_LESSON",
    "growth came from improving the process behind the marketing, not from adding more busywork",
)

TAG_PREFIX = env("CAMPAIGN_TAG_PREFIX", "webinar")
CAMPAIGN_NAME = env("CAMPAIGN_NAME", f"{WEBINAR_TITLE} Funnel")

TAGS = {
    "nurture": f"{TAG_PREFIX}-nurture-start",
    "registered": f"{TAG_PREFIX}-registered",
    "attended": f"{TAG_PREFIX}-attended",
    "no_show": f"{TAG_PREFIX}-no-show",
    "cart_open": f"{TAG_PREFIX}-cart-open",
    "no_buy": f"{TAG_PREFIX}-no-buy",
    "purchased": f"{TAG_PREFIX}-purchased",
}


def signature() -> str:
    return f"- {SENDER_NAME}\n{BUSINESS_NAME}"


CAMPAIGN = {
    "01": {
        "name": "01. List Nurture",
        "tag": TAGS["nurture"],
        "templates": link_steps(
            [
                email_step(
                    "Nurture 1 - The Common Bottleneck",
                    "the common bottleneck",
                    f"""Hey {{{{contact.first_name}}}},

Most {AUDIENCE_LABEL} do not have a traffic problem first.

They have a follow-up problem.

Someone raises their hand, asks a question, downloads a resource, or books a call. Then the next step depends on manual reminders, a busy inbox, or someone remembering to check a spreadsheet.

That is where good opportunities get lost.

Over the next few messages, I will walk you through a simple system for turning more interest into real conversations about {SERVICE_CATEGORY}.

Talk soon.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("1 day", 1, "days"),
                email_step(
                    "Nurture 2 - Client Example",
                    "what changed for a recent client",
                    f"""Hey {{{{contact.first_name}}}},

Here is the pattern we see with {CASE_STUDY_LABEL}.

Before: {CASE_STUDY_BEFORE}.

After: {CASE_STUDY_AFTER}.

The lesson was simple: {CASE_STUDY_LESSON}.

That is the system I will break down in {WEBINAR_TITLE}.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("1 day", 1, "days"),
                email_step(
                    "Nurture 3 - System Behind The Marketing",
                    "the system behind the marketing",
                    f"""Hey {{{{contact.first_name}}}},

When marketing feels unpredictable, the issue is usually not one single message or one single channel.

It is the missing operating system behind the campaign:

- Fast response when someone shows interest
- Clear next steps for qualified leads
- Follow-up that does not depend on memory
- A simple way to track what is working

That is what {WEBINAR_TITLE} is about.

Join us {WEBINAR_DAY} at {WEBINAR_TIME}.

Reply "{REGISTRATION_KEYWORD}" and we will send the link, or use this link:
{WEBINAR_LINK}

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("1 day", 1, "days"),
                email_step(
                    "Nurture 4 - Final Invite",
                    f"{WEBINAR_DAY} at {WEBINAR_TIME}",
                    f"""Hey {{{{contact.first_name}}}},

Last reminder before {WEBINAR_TITLE}.

If you want a clearer path for {OFFER_OUTCOME}, this is worth attending live.

We will cover the core system, the follow-up structure, and the next steps to apply it inside a real {INDUSTRY_LABEL}.

Time: {WEBINAR_DAY} at {WEBINAR_TIME}
Length: {WEBINAR_DURATION}
Link: {WEBINAR_LINK}

Reply "{REGISTRATION_KEYWORD}" if you want help getting registered.

{signature()}""",
                    SENDER_NAME,
                ),
            ]
        ),
    },
    "02": {
        "name": "02. Webinar Confirmation",
        "tag": TAGS["registered"],
        "templates": link_steps(
            [
                sms_step(
                    "Registration Confirmed",
                    f"Hey {{{{contact.first_name}}}}, you are registered for {WEBINAR_TITLE} on {WEBINAR_DAY} at {WEBINAR_TIME}.\n\nLink: {WEBINAR_LINK}\n\n{signature()}",
                ),
                email_step(
                    "Registration Confirmed",
                    "you are registered",
                    f"""Hey {{{{contact.first_name}}}},

You are registered for {WEBINAR_TITLE}.

Time: {WEBINAR_DAY} at {WEBINAR_TIME}
Link: {WEBINAR_LINK}

We will show you how to build a practical system to {OFFER_OUTCOME}.

See you there.

{signature()}""",
                    SENDER_NAME,
                ),
            ]
        ),
    },
    "03": {
        "name": "03. Day-Of Reminders",
        "tag": TAGS["registered"],
        "templates": link_steps(
            [
                sms_step(
                    "Morning Reminder",
                    f"Today is the day, {{{{contact.first_name}}}}. {WEBINAR_TITLE} is at {WEBINAR_TIME}.\n\nLink: {WEBINAR_LINK}",
                ),
                wait_step("9 hours", 9, "hours"),
                sms_step(
                    "1 Hour Reminder",
                    f"We start in about 1 hour.\n\nBring one question about improving your follow-up or sales process.\n\nLink: {WEBINAR_LINK}",
                ),
                wait_step("30 min", 30, "minutes"),
                email_step(
                    "30 Minute Reminder",
                    "starting soon",
                    f"""Hey {{{{contact.first_name}}}},

We start in 30 minutes.

Topic: {WEBINAR_TITLE}
Link: {WEBINAR_LINK}

Everyone who attends live gets {BONUS_NAME}: {BONUS_COPY}.

See you soon.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("30 min", 30, "minutes"),
                sms_step(
                    "Live Now",
                    f"We are live now.\n\nJoin here: {WEBINAR_LINK}",
                ),
            ]
        ),
    },
    "04": {
        "name": "04. Attendee Follow-Up",
        "tag": TAGS["attended"],
        "templates": link_steps(
            [
                sms_step(
                    "Thanks For Attending",
                    f"Hey {{{{contact.first_name}}}}, thanks for attending {WEBINAR_TITLE}.\n\nIf you have questions about {OFFER_NAME}, reply here.",
                ),
                email_step(
                    "Attendee Recap",
                    "thanks for attending",
                    f"""Hey {{{{contact.first_name}}}},

Thank you for attending {WEBINAR_TITLE}.

Quick recap:

- Where leads or prospects typically fall through the cracks
- How to respond faster without adding manual work
- How to structure follow-up so more people take the next step
- How {OFFER_NAME} helps you apply the system

Enrollment detail: {PRICE_TEXT}
Deadline: {DEADLINE_TEXT}

If you have questions, reply to this email.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("14 hours", 14, "hours"),
                sms_step(
                    "Case Study Follow-Up",
                    f"One useful takeaway from the workshop: {CASE_STUDY_LABEL} changed the process first, then the results improved.\n\nDeadline: {DEADLINE_TEXT}.",
                ),
                email_step(
                    "Case Study Follow-Up",
                    "what changed after the system was installed",
                    f"""Hey {{{{contact.first_name}}}},

I wanted to underline one point from the workshop.

For {CASE_STUDY_LABEL}, the real change was not a single tactic.

Before: {CASE_STUDY_BEFORE}.

After: {CASE_STUDY_AFTER}.

That is why {OFFER_NAME} focuses on implementation, not just ideas.

Deadline: {DEADLINE_TEXT}
Enrollment detail: {PRICE_TEXT}

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("24 hours", 24, "hours"),
                sms_step(
                    "Proof Point",
                    f"Quick reminder, {{{{contact.first_name}}}}: the goal is not more busywork. The goal is a cleaner system for turning interest into action.\n\nDeadline: {DEADLINE_TEXT}.",
                ),
                email_step(
                    "Proof Point",
                    "why this works",
                    f"""Hey {{{{contact.first_name}}}},

The reason this system works is that it removes avoidable delays.

People get a faster response.
They know the next step.
You get a clearer view of what is happening.
Follow-up keeps moving even when the team is busy.

That is what {OFFER_NAME} is built to help you install.

Deadline: {DEADLINE_TEXT}

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("24 hours", 24, "hours"),
                sms_step(
                    "Deadline Day",
                    f"Last day to use the live-attendee offer for {OFFER_NAME}.\n\nDeadline: {DEADLINE_TEXT}. Reply with questions.",
                ),
                email_step(
                    "Deadline Day",
                    "deadline today",
                    f"""Hey {{{{contact.first_name}}}},

Final reminder for the live-attendee offer.

Offer: {OFFER_NAME}
Outcome: {OFFER_OUTCOME}
Enrollment detail: {PRICE_TEXT}
Deadline: {DEADLINE_TEXT}

If it is a fit, reply and we will help with the next step.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("11 hours", 11, "hours"),
                email_step(
                    "Final Hours",
                    "final hours",
                    f"""Hey {{{{contact.first_name}}}},

Final hours before the {OFFER_NAME} deadline.

Reply if you want help deciding whether it is a fit.

{signature()}""",
                    SENDER_NAME,
                ),
            ]
        ),
    },
    "05": {
        "name": "05. No-Show Replay",
        "tag": TAGS["no_show"],
        "templates": link_steps(
            [
                sms_step(
                    "Replay Available",
                    f"Hey {{{{contact.first_name}}}}, sorry we missed you live. The {WEBINAR_TITLE} replay is available for {REPLAY_WINDOW}.\n\nLink: {WEBINAR_LINK}",
                ),
                email_step(
                    "Replay Available",
                    "the replay is available",
                    f"""Hey {{{{contact.first_name}}}},

No problem if you missed the live workshop.

The replay for {WEBINAR_TITLE} is available for {REPLAY_WINDOW}.

Watch here:
{WEBINAR_LINK}

The most useful section is the framework for turning interest into a clear next step.

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("16 hours", 16, "hours"),
                sms_step(
                    "Replay Nudge",
                    f"Did you get a chance to watch the replay yet?\n\nIt is available for {REPLAY_WINDOW}: {WEBINAR_LINK}",
                ),
                wait_step("22 hours", 22, "hours"),
                sms_step(
                    "Replay Reminder",
                    f"Reminder: the {WEBINAR_TITLE} replay is still available.\n\nWatch here: {WEBINAR_LINK}",
                ),
                email_step(
                    "Replay Deadline",
                    "replay reminder",
                    f"""Hey {{{{contact.first_name}}}},

Quick reminder that the replay for {WEBINAR_TITLE} is available for {REPLAY_WINDOW}.

If you want a practical way to {OFFER_OUTCOME}, it is worth watching.

Replay link:
{WEBINAR_LINK}

{signature()}""",
                    SENDER_NAME,
                ),
                wait_step("26 hours", 26, "hours"),
                sms_step(
                    "Final Replay Reminder",
                    f"Last replay reminder from us. If you still want to watch {WEBINAR_TITLE}, use this link: {WEBINAR_LINK}",
                ),
            ]
        ),
    },
    "06": {
        "name": "06. Cart Close Deadline",
        "tag": TAGS["cart_open"],
        "templates": link_steps(
            [
                sms_step(
                    "6 Hours Left",
                    f"About 6 hours left before the {OFFER_NAME} deadline.\n\nDeadline: {DEADLINE_TEXT}.",
                ),
                wait_step("5 hours", 5, "hours"),
                sms_step(
                    "1 Hour Left",
                    f"1 hour left, {{{{contact.first_name}}}}.\n\nIf {OFFER_NAME} is the right next step, reply now and we will help.",
                ),
            ]
        ),
    },
    "07": {
        "name": "07. Post-Cart Nurture",
        "tag": TAGS["no_buy"],
        "templates": link_steps(
            [
                sms_step(
                    "Thanks",
                    f"Hey {{{{contact.first_name}}}}, thanks for checking out {WEBINAR_TITLE}. We will keep sharing useful ideas. Reply anytime.\n\n{signature()}",
                ),
                wait_step("3 days", 3, "days"),
                email_step(
                    "Quick Win",
                    "a quick win you can use today",
                    f"""Hey {{{{contact.first_name}}}},

One useful thing you can improve this week:

Write down the exact next step after someone shows interest in {SERVICE_CATEGORY}.

Then make sure every person gets that next step quickly and consistently.

That one change alone can make your follow-up feel more reliable.

{signature()}""",
                    SENDER_NAME,
                ),
            ]
        ),
    },
    "08": {
        "name": "08. Purchase Exit",
        "tag": TAGS["purchased"],
        "templates": link_steps(
            [
                sms_step(
                    "Welcome",
                    f"Welcome to {OFFER_NAME}, {{{{contact.first_name}}}}. We are glad to have you. Watch for next-step details soon.\n\n{signature()}",
                ),
            ]
        ),
    },
}


def main():
    total_steps = sum(len(wf["templates"]) for wf in CAMPAIGN.values())
    print(f"{CAMPAIGN_NAME} - {len(CAMPAIGN)} workflows, {total_steps} steps\n")

    token_mgr = TokenManager(LOCATION_ID)
    if os.environ.get("GHL_FIREBASE_REFRESH_TOKEN"):
        token_mgr.set_refresh_token(os.environ["GHL_FIREBASE_REFRESH_TOKEN"])

    client = GHLClient(token_mgr, LOCATION_ID)

    print("Testing auth...")
    test = client.request("GET", f"/workflow/{LOCATION_ID}/list?parentId=root&limit=1")
    if not test:
        print("Auth failed!")
        sys.exit(1)
    print("Auth OK\n")

    builder = CampaignBuilder(client, LOCATION_ID)
    stats = builder.build(
        CAMPAIGN,
        folder_name=CAMPAIGN_NAME,
        parent_folder=PARENT_FOLDER or None,
        company_id=COMPANY_ID,
        user_id=USER_ID,
    )

    if stats["steps_saved"] == total_steps:
        print(f"\nVERIFICATION: All {total_steps} steps saved successfully!")
    else:
        print(f"\nWARNING: Expected {total_steps} steps, saved {stats['steps_saved']}")


if __name__ == "__main__":
    main()
