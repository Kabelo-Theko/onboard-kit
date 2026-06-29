"""Tests for onboard_kit: username derivation, the plan a retail starter gets,
date maths, the manager case, and the unknown-department fallback.
"""
from datetime import date

from onboard_kit.planner import Starter, build_plan, username_for
from onboard_kit.generate import checklist_markdown, welcome_email


def _retail():
    return Starter(name="Thabo Nkosi", department="Retail / Store",
                   role="Sales Assistant", start_date=date(2026, 7, 15),
                   manager="Lerato M", domain="brand.co.za")


def test_username_first_dot_last_lowercased():
    assert username_for("Thabo Nkosi") == "thabo.nkosi"
    assert username_for("  SARA   DANIELS ") == "sara.daniels"
    assert username_for("Mononymous") == "mononymous"


def test_username_strips_accents():
    assert username_for("José Méndez") == "jose.mendez"


def test_email_built_from_username_and_domain():
    plan = build_plan(_retail())
    assert plan.email == "thabo.nkosi@brand.co.za"


def test_retail_plan_has_core_account_and_dept_items():
    plan = build_plan(_retail())
    descs = [t.description for t in plan.tasks]
    assert any("Active Directory account" in d for d in descs)
    assert any("mailbox" in d.lower() and "Microsoft 365" in d for d in descs)
    assert any("Point-of-sale app" in d for d in descs)
    assert any("POS-Users" in d for d in descs)


def test_account_tasks_are_due_before_start():
    plan = build_plan(_retail())
    account = [t for t in plan.tasks if t.category == "Account"]
    assert account and all(t.due < plan.starter.start_date for t in account)


def test_senior_role_gets_manager_group_and_approver_access():
    s = Starter(name="Sara Daniels", department="Design / Studio",
                role="Design Lead", start_date=date(2026, 7, 15))
    plan = build_plan(s)
    text = " ".join(t.description for t in plan.tasks)
    assert "Managers" in text
    assert "approver" in text.lower()


def test_unknown_department_uses_default_and_flags_it():
    s = Starter(name="Jay Patel", department="Underwater Basket Weaving",
                role="Specialist", start_date=date(2026, 7, 15))
    plan = build_plan(s)
    assert plan.department_matched is False
    assert "default" in checklist_markdown(plan).lower()


def test_welcome_email_contains_name_and_date():
    email = welcome_email(build_plan(_retail()))
    assert "Thabo" in email
    assert "15 Jul 2026" in email
