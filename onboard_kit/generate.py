"""Render a plan into the three things a manager and a new starter actually see:
a checklist, a welcome email, and a Day-1 orientation guide. All Markdown or
plain text, so they paste straight into a ticket, an email, or a wiki.
"""
from __future__ import annotations

from datetime import date

from .planner import Plan

CATEGORY_ORDER = ["Account", "Hardware", "Software", "Access", "Comms"]


def _fmt(d: date) -> str:
    return d.strftime("%a %d %b %Y")


def checklist_markdown(plan: Plan) -> str:
    s = plan.starter
    lines = [
        f"# IT onboarding checklist — {s.name}",
        "",
        f"- **Role:** {s.role}",
        f"- **Department:** {s.department}" + ("" if plan.department_matched else "  _(no department profile matched; used the default set, please review)_"),
        f"- **Start date:** {_fmt(s.start_date)}",
        f"- **Username:** `{plan.username}`  ·  **Email:** {plan.email}",
        f"- **Licence:** {plan.license}",
        "",
    ]
    for cat in CATEGORY_ORDER:
        items = [t for t in plan.tasks if t.category == cat]
        if not items:
            continue
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| Done | Task | Owner | Due |")
        lines.append("| --- | --- | --- | --- |")
        for t in items:
            lines.append(f"| [ ] | {t.description} | {t.owner} | {_fmt(t.due)} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def welcome_email(plan: Plan) -> str:
    s = plan.starter
    first = s.name.split()[0] if s.name.strip() else "there"
    return (
        f"Subject: Welcome to the team, {first} — your first day\n\n"
        f"Hi {first},\n\n"
        f"We are looking forward to having you join as {s.role} on {_fmt(s.start_date)}.\n\n"
        "Your accounts will be ready before you arrive. On your first morning, IT will\n"
        "walk you through logging in, connecting to Wi-Fi, your email and the systems\n"
        "you will use day to day.\n\n"
        "What to bring on day one:\n"
        "  - A photo ID for your access setup.\n"
        "  - Any device details if you are bringing your own peripherals.\n\n"
        f"Your sign-in name will be {plan.email}. You will set your password and\n"
        "multi-factor authentication with IT when you arrive, so there is nothing to\n"
        "prepare in advance.\n\n"
        "If anything comes up before your start date, just reply to this email.\n\n"
        "See you soon,\n"
        f"{plan.starter.manager or 'The team'}\n"
    )


def day_one_guide(plan: Plan) -> str:
    s = plan.starter
    return f"""# Day 1 IT orientation — {s.name}

Welcome. This is the short version of everything you need to get working today.

## 1. Signing in
- Your username is `{plan.username}` and your email is {plan.email}.
- IT will help you set your password and multi-factor authentication (MFA) now.
  MFA means you confirm a prompt on your phone when you log in, so your account
  stays yours even if someone learns the password.

## 2. Wi-Fi and network
- Connect to the staff Wi-Fi (IT will give you the name and password).
- If the internet does not work, tell IT what you see rather than guessing; it
  helps us fix it faster.

## 3. Email and Microsoft 365
- Your mailbox is {plan.email}, on {plan.license}.
- Teams, Outlook, SharePoint and OneDrive are where messages, mail and files
  live. Save work to OneDrive or the team folder, not the desktop.

## 4. Printing and saving files
- IT will add the right printer for your area.
- Shared files go in the team folder so other people can find them. Personal
  drafts go in OneDrive.

## 5. Staying safe
- Never share your password. IT will never ask for it.
- If an email looks off (unexpected link, urgent money request), do not click;
  forward it to IT.
- Lock your screen when you step away (Windows key + L).

## 6. Who to contact
- For anything that is not working, log it with IT. Tell us what you were doing,
  what happened, and whether it affects other people too.

You are set up and ready. Welcome aboard.
"""
