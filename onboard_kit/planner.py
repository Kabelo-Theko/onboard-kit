"""Build the onboarding plan from a new starter's details.

The plan is a list of tasks. Each task has a category, a short description, an
owner (the system or person responsible) and a due date worked out relative to
the start date, so IT can see what must happen before day one.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, timedelta

from .catalog import is_senior, profile_for


@dataclass
class Starter:
    name: str
    department: str
    role: str
    start_date: date
    manager: str = ""
    domain: str = "example.co.za"


@dataclass
class Task:
    category: str          # Account, Hardware, Software, Access, Comms
    description: str
    owner: str
    due: date

    def to_dict(self) -> dict:
        return {"category": self.category, "description": self.description,
                "owner": self.owner, "due": self.due.isoformat()}


@dataclass
class Plan:
    starter: Starter
    username: str
    email: str
    license: str
    department_matched: bool
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.starter.name, "department": self.starter.department,
            "role": self.starter.role, "start_date": self.starter.start_date.isoformat(),
            "username": self.username, "email": self.email, "license": self.license,
            "department_matched": self.department_matched,
            "tasks": [t.to_dict() for t in self.tasks],
        }


def username_for(name: str) -> str:
    """first.last, lowercased, accents stripped, spaces collapsed."""
    cleaned = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    parts = [p for p in re.split(r"\s+", cleaned.strip().lower()) if p]
    if not parts:
        return "new.starter"
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}.{parts[-1]}"


def build_plan(starter: Starter) -> Plan:
    prof, matched = profile_for(starter.department)
    username = username_for(starter.name)
    email = f"{username}@{starter.domain}"
    start = starter.start_date

    def due(offset_days: int) -> date:
        return start + timedelta(days=offset_days)

    tasks: list[Task] = []

    # --- Account (before start) ---
    tasks.append(Task("Account", f"Create Active Directory account '{username}'", "IT / AD", due(-3)))
    tasks.append(Task("Account", f"Create mailbox {email} and assign {prof.m365_license}", "IT / M365", due(-3)))
    groups = list(prof.access_groups)
    if is_senior(starter.role):
        groups.append("Managers")
    tasks.append(Task("Account", "Add to security groups: " + ", ".join(groups), "IT / AD", due(-2)))
    tasks.append(Task("Account", "Enrol multi-factor authentication (MFA)", "IT", due(-1)))

    # --- Hardware (before start) ---
    for item in prof.hardware:
        tasks.append(Task("Hardware", f"Allocate and image: {item}", "IT / Asset", due(-2)))
    if prof.hardware:
        tasks.append(Task("Hardware", "Asset-tag all kit and record in the inventory", "IT / Asset", due(-1)))

    # --- Software (before start) ---
    tasks.append(Task("Software", "Install standard build: Windows, Microsoft 365, antivirus", "IT", due(-1)))
    for sw in prof.software:
        tasks.append(Task("Software", f"Install / assign licence: {sw}", "IT", due(-1)))

    # --- Access (before start) ---
    if is_senior(starter.role):
        tasks.append(Task("Access", "Grant approver / reporting access for the team", "IT / System owner", due(-1)))
    tasks.append(Task("Access", "Confirm shared drive and team folder permissions", "IT", due(-1)))

    # --- Comms (day one) ---
    mgr = starter.manager or "the line manager"
    tasks.append(Task("Comms", f"Send welcome email to {email}", f"{mgr} / IT", due(0)))
    tasks.append(Task("Comms", "Run Day-1 IT orientation (login, Wi-Fi, printing, security basics)", "IT", due(0)))

    return Plan(
        starter=starter, username=username, email=email,
        license=prof.m365_license, department_matched=matched, tasks=tasks,
    )
