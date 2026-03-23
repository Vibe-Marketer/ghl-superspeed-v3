#!/usr/bin/env python3
"""
PPP Webinar Campaign — v3 SuperSpeed Engine
8 workflows, 45 steps, all triggers — built with parallel execution.

Usage:
    python3 campaigns/ppp-webinar.py [token]
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.engine import (
    TokenManager, GHLClient, CampaignBuilder,
    sms_step, email_step, wait_step, tag_step, link_steps,
)

# ── Config ────────────────────────────────────────────────────────────────────

LOCATION_ID = "2hP6rCb3COd2HUjD25w2"  # Christians Testing
PARENT_FOLDER = "ca2666ec-84af-4155-9d0a-1774430c98b7"  # ++ Agent Testing
COMPANY_ID = "R1HWQKyMMoj4PJ5mAYed"
USER_ID = "YewkebOufK3hmeP1gx4B"

# ── Campaign Definition ───────────────────────────────────────────────────────

CAMPAIGN = {
    "01": {
        "name": "01. List Nurture (Mon-Thu)",
        "tag": "nurture-start",
        "templates": link_steps([
            email_step("Mon - Practice Owner's Dilemma", "the practice owner's dilemma", """Hey {{contact.first_name}},

You got into healthcare to help people.

Not to spend your nights staring at ad dashboards wondering why nothing's working.

But here you are.

Running a practice. Managing staff. Seeing patients. AND trying to figure out marketing.

That's like asking a pilot to also build the plane while flying it.

I'm Dr. Emeka.

I've spent the last few years building AI systems that do the marketing part for you.

Not "set it and forget it" nonsense.

Real systems that respond to leads in under 60 seconds, book appointments automatically, and follow up without you lifting a finger.

I'll be sharing more over the next few days.

No fluff. No theory. Just what's working right now for practices like yours.

Talk soon.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("1 day (Tuesday)", 1, "days"),
            email_step("Tue - $20K to $131K", "$20K to $131K in 90 days", """Hey {{contact.first_name}},

Let me tell you about a med spa in Houston.

90 days ago they were doing $20K/month.

Good practice. Great reviews. Talented provider.

But their marketing was a mess.

Running Facebook ads with no follow-up system. Leads coming in and sitting in a spreadsheet. Front desk calling people back 2 days later.

Sound familiar?

We installed three things:

An AI chatbot that responds to every inquiry in under 60 seconds.

An ad system that tests 5 creatives every 3 days and kills the losers automatically.

An operations backend that sends reminders, reduces no-shows, and reactivates old patients.

90 days later: $131K/month. 21.7x return on ad spend.

890 AI conversations. 104 appointments booked. Automatically.

The provider didn't work more hours.

They installed a system.

That's the difference between a practice that grows and one that grinds.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("1 day (Wednesday)", 1, "days"),
            email_step("Wed - I've tried ads before", "\"I've tried ads before\"", """Hey {{contact.first_name}},

I hear this every week.

"I've tried Facebook ads. They don't work for my practice."

And every time I ask the same question:

"Did you have a system behind the ads?"

Silence.

Here's the truth.

The ads probably worked fine.

They generated clicks. Maybe even leads.

But leads without a system are just names on a list.

No instant follow-up. No automated booking. No nurture sequence. No reactivation.

You paid to fill a bucket with a hole in the bottom.

The ads aren't the problem.

The backend is the problem.

Fix the backend first. Then the ads become a money printer.

That's exactly what I teach in my free Thursday training.

Every Thursday at 7 PM ET.

The Predictable Patient Pipeline Method.

No pitch for the first 60 minutes. Just the system.

Reply "WEBINAR" and I'll send you the link.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("1 day (Thursday AM)", 1, "days"),
            email_step("Thu - This Thursday", "this Thursday", """Hey {{contact.first_name}},

I've been sending you emails this week.

Case studies. Frameworks. Results from real practices.

But I can't do the work for you through email.

At some point you have to decide.

Keep doing what you're doing and hope something changes.

Or show up tonight and see the system that's changing practices across the country.

The Predictable Patient Pipeline.

Tonight. 7 PM ET. Free.

90 minutes of my best stuff. No fluff.

Reply "WEBINAR" for the link.

Or don't. Either way, I respect your decision.

But if you've read this far, something's telling you it's time.

Listen to that.

— Dr. Emeka""", "Dr. Emeka"),
        ]),
    },
    "02": {
        "name": "02. Webinar Confirmation",
        "tag": "webinar-registered",
        "templates": link_steps([
            sms_step("Registration Confirmed", "Hey {{contact.first_name}}, you're registered for Thursday's LIVE training:\n\n\"The Predictable Patient Pipeline Method\" — 7 PM ET.\n\nI'm going to show you the exact AI system that helped a med spa go from $20K to $131K/month.\n\nSave the date: This Thursday at 7 PM ET\n\n— Dr. Emeka"),
            email_step("You're In", "you're in", """Hey {{contact.first_name}},

You just made a decision most practice owners never make.

You raised your hand.

This Thursday at 7 PM ET, I'm going live with something I normally only share with paying clients.

The Predictable Patient Pipeline.

It's the exact system behind a med spa that went from $20K to $131K/month.

Not theory. Real numbers. Real dashboards. Real results.

Show up on time. I start at 7 PM sharp.

See you Thursday.

— Dr. Emeka""", "Dr. Emeka"),
        ]),
    },
    "03": {
        "name": "03. Day-Of Reminders (Thu)",
        "tag": "webinar-registered",
        "templates": link_steps([
            sms_step("Thu 9 AM", "Today's the day, {{contact.first_name}}!\n\nThe Predictable Patient Pipeline LIVE training is tonight at 7 PM ET.\n\nSee you at 7!\n— Dr. Emeka"),
            wait_step("9 hours", 9, "hours"),
            sms_step("Thu 6 PM", "We start in 60 minutes!\n\nHave your questions ready — I'm doing live Q&A at the end."),
            wait_step("30 min", 30, "minutes"),
            email_step("Thu 6:30 PM", "starting in 30 minutes", """Hey {{contact.first_name}},

We go live in 30 minutes.

Grab a notebook. You'll want to write this down.

Close distractions for 90 minutes.

Have your questions ready for Q&A.

Everyone who attends live gets the Pipeline Blueprint free.

See you in 30.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("30 min", 30, "minutes"),
            sms_step("Thu 7 PM LIVE", "We're LIVE!\n\nI'm starting with the $131K med spa breakdown. Don't miss the first 10 minutes."),
        ]),
    },
    "04": {
        "name": "04. Attendee Follow-Up (Thu-Sun)",
        "tag": "webinar-attended",
        "templates": link_steps([
            sms_step("Thu Thanks", "Hey {{contact.first_name}}, thanks for showing up tonight!\n\nIf you want to lock in the live bonus, it expires Sunday at midnight.\n\nAny questions? Just text me back.\n— Dr. Emeka"),
            email_step("Thu Recap", "thanks for showing up tonight", """Hey {{contact.first_name}},

Thank you for spending your evening with me.

I don't take that lightly.

Quick recap of what we covered:

Why 90% of clinic marketing fails.

The Predictable Patient Pipeline — AI Acquisition, Content Engine, Operations Autopilot.

Real numbers. $131K/month med spa. $516K/quarter dental.

The live bonus expires Sunday at midnight.

$997. Or 3 payments of $397.

If you have questions, just reply.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("14 hours (Fri AM)", 14, "hours"),
            sms_step("Fri Case Study", "Hey {{contact.first_name}}, after last night I wanted to share something.\n\nThe Houston med spa got their first 12 appointments in the FIRST WEEK.\n\nWeek one. Not month one.\n\nLive bonus expires Sunday midnight."),
            email_step("Fri Deep Dive", "what happened in the first week", """Hey {{contact.first_name}},

I showed you the big numbers last night.

$131K/month. $516K/quarter. 21.7x ROAS.

But I didn't have time to share what happened in the first week.

Houston Med Spa: 12 appointments booked automatically. Week one.

The system works fast because you're not starting from scratch.

If the system books you just 2 extra patients this month, it's paid for itself.

The live bonus expires Sunday midnight.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("24 hours (Sat)", 24, "hours"),
            sms_step("Sat Social Proof", "{{contact.first_name}}, a practice owner from Thursday's webinar just sent me this:\n\n\"I was skeptical but I signed up Friday morning. The custom ads were in my inbox by Saturday afternoon.\"\n\nLive bonus expires TOMORROW at midnight."),
            email_step("Sat Proof", "\"I was skeptical, but...\"", """Hey {{contact.first_name}},

A recent Pipeline Program member sent me this:

"I was skeptical. But the custom ads from my website were ready in 48 hours, and I had my first campaign live by day 3."

This isn't "buy and figure it out."

It's "buy and we build it together."

The live bonus expires tomorrow at midnight.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("24 hours (Sun AM)", 24, "hours"),
            sms_step("Sun Last Day", "Last day, {{contact.first_name}}.\n\nThe Pipeline Program live bonus expires at midnight tonight.\n\nAfter tonight:\n- No private Slack with me\n- No done-for-you campaign setup"),
            email_step("Sun Closing", "closing tonight at midnight", """Hey {{contact.first_name}},

This is your final reminder.

The Predictable Patient Pipeline Program closes tonight at midnight ET.

After midnight, you lose:

Private Slack channel with me for 30 days.

Done-for-you Facebook campaign setup.

$997. Or 3 payments of $397.

This is the last email about Thursday's offer.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("11 hours (Sun 9 PM)", 11, "hours"),
            email_step("3 hours", "3 hours", """{{contact.first_name}},

3 hours.

— Dr. Emeka""", "Dr. Emeka"),
        ]),
    },
    "05": {
        "name": "05. No-Show Replay",
        "tag": "webinar-no-show",
        "templates": link_steps([
            sms_step("Thu Replay", "Hey {{contact.first_name}}, we missed you tonight!\n\nI recorded the whole thing — including the $20K to $131K/month case study.\n\nWatch the replay (72 hours).\n— Dr. Emeka"),
            email_step("Thu Replay", "you missed it — but I saved it for you", """Hey {{contact.first_name}},

I know life gets busy.

No worries about missing tonight's live training.

I recorded the whole thing for you.

The replay is 90 minutes. Most valuable section starts at the 30-minute mark.

Everyone who watches gets the Pipeline Blueprint.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("16 hours (Fri noon)", 16, "hours"),
            sms_step("Fri Nudge", "{{contact.first_name}}, did you catch the replay yet?\n\nThe SPY Method section alone is worth your time.\n\nReplay comes down Sunday."),
            wait_step("22 hours (Sat AM)", 22, "hours"),
            sms_step("Sat Reminder", "Hey {{contact.first_name}}, the webinar replay comes down tomorrow night.\n\n- The exact ad system behind $131K/month practices\n- Free Pipeline Blueprint\n- A special offer (replay only)"),
            email_step("Sat Replay Urgency", "replay comes down tomorrow", """Hey {{contact.first_name}},

The Predictable Patient Pipeline replay comes down tomorrow at midnight.

If you haven't watched yet, the most valuable section starts at the 30-minute mark.

— Dr. Emeka""", "Dr. Emeka"),
            wait_step("26 hours (Sun noon)", 26, "hours"),
            sms_step("Sun Final", "Last chance — the replay comes down at midnight tonight.\n\nAt minimum watch the 30-minute mark where I break down the 3 AI systems."),
        ]),
    },
    "06": {
        "name": "06. Cart Close Deadline (Sun)",
        "tag": "webinar-cart-open",
        "templates": link_steps([
            sms_step("Sun 6 PM", "6 hours left.\n\nThe Pipeline Program live bonus closes at midnight.\n\nEvery week without a system is patients choosing someone else."),
            wait_step("5 hours", 5, "hours"),
            sms_step("Sun 11 PM", "1 hour left, {{contact.first_name}}.\n\nThe Predictable Patient Pipeline live bonus is gone at midnight.\n\nThis is it."),
        ]),
    },
    "07": {
        "name": "07. Post-Cart Nurture",
        "tag": "webinar-no-buy",
        "templates": link_steps([
            sms_step("Thanks", "Hey {{contact.first_name}}, thanks for checking out the Predictable Patient Pipeline training.\n\nI'll keep sharing free content — reply anytime.\n— Dr. Emeka"),
            wait_step("3 days", 3, "days"),
            email_step("Quick Win", "a quick win you can use today", """Hey {{contact.first_name}},

One thing you can do today to get more patients.

The 60-Second Follow-Up Rule.

When a lead comes in, respond within 60 seconds.

Studies show responding in under 1 minute makes you 391% more likely to convert.

Most practices respond in 24-48 hours. By then, the patient booked with someone else.

Try it this week.

— Dr. Emeka""", "Dr. Emeka"),
        ]),
    },
    "08": {
        "name": "08. Purchase Exit (Remove All)",
        "tag": "pipeline-purchased",
        "templates": link_steps([
            sms_step("Welcome", "Welcome to the Predictable Patient Pipeline Program, {{contact.first_name}}!\n\nYou made a great decision. I'll be in touch within 24 hours.\n\n— Dr. Emeka"),
        ]),
    },
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Count steps
    total_steps = sum(len(wf["templates"]) for wf in CAMPAIGN.values())
    print(f"PPP Webinar Campaign — v3 SuperSpeed Engine")
    print(f"{len(CAMPAIGN)} workflows, {total_steps} steps\n")

    # Init
    token_mgr = TokenManager(LOCATION_ID)
    if os.environ.get("GHL_FIREBASE_REFRESH_TOKEN"):
        token_mgr.set_refresh_token(os.environ["GHL_FIREBASE_REFRESH_TOKEN"])

    client = GHLClient(token_mgr, LOCATION_ID)

    # Test auth
    print("Testing auth...")
    test = client.request("GET", f"/workflow/{LOCATION_ID}/list?parentId=root&limit=1")
    if not test:
        print("Auth failed!")
        sys.exit(1)
    print("Auth OK\n")

    # Build
    builder = CampaignBuilder(client, LOCATION_ID)
    stats = builder.build(
        CAMPAIGN,
        folder_name="PPP Campaign v3",
        parent_folder=PARENT_FOLDER,
        company_id=COMPANY_ID,
        user_id=USER_ID,
    )

    # Verify step count
    if stats["steps_saved"] == total_steps:
        print(f"\nVERIFICATION: All {total_steps} steps saved successfully!")
    else:
        print(f"\nWARNING: Expected {total_steps} steps, saved {stats['steps_saved']}")


if __name__ == "__main__":
    main()
