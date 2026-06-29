"""Command-line front end for onboard_kit.

Give it a starter's details and it prints (or writes) the checklist, the welcome
email and the Day-1 guide.

Examples:
    python -m onboard_kit.cli --name "Thabo Nkosi" --department "Retail / Store" \\
        --role "Sales Assistant" --start 2026-07-15 --manager "Lerato M"

    python -m onboard_kit.cli --name "Sara Daniels" --department "Design / Studio" \\
        --role "Design Lead" --start 2026-07-15 --out ./onboarding
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .planner import Starter, build_plan
from .generate import checklist_markdown, welcome_email, day_one_guide


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate an IT onboarding pack for a new starter.")
    p.add_argument("--name", required=True)
    p.add_argument("--department", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    p.add_argument("--manager", default="")
    p.add_argument("--domain", default="example.co.za")
    p.add_argument("--out", help="Directory to write the files to. If omitted, prints to screen.")
    args = p.parse_args(argv)

    try:
        start = date.fromisoformat(args.start)
    except ValueError:
        print("Start date must be YYYY-MM-DD, e.g. 2026-07-15", file=sys.stderr)
        return 2

    starter = Starter(name=args.name, department=args.department, role=args.role,
                      start_date=start, manager=args.manager, domain=args.domain)
    plan = build_plan(starter)

    checklist = checklist_markdown(plan)
    email = welcome_email(plan)
    guide = day_one_guide(plan)

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        stem = plan.username
        (out / f"{stem}_checklist.md").write_text(checklist, encoding="utf-8")
        (out / f"{stem}_welcome_email.txt").write_text(email, encoding="utf-8")
        (out / f"{stem}_day1_guide.md").write_text(guide, encoding="utf-8")
        print(f"Wrote 3 files to {out}/ for {plan.username}")
    else:
        print(checklist)
        print("\n" + "=" * 60 + "\n")
        print(email)
        print("\n" + "=" * 60 + "\n")
        print(guide)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
