"""onboard_kit: turn a new starter's details into a complete IT onboarding plan.

Give it a name, department, role and start date. It produces the checklist of
everything IT needs to do before day one (accounts, licences, hardware, access),
each task with an owner and a due date, plus a welcome email and a Day-1
orientation guide. It is deterministic and template-driven on purpose: the same
input always gives the same plan, and every line can be explained.
"""
from .planner import build_plan, username_for
from .generate import checklist_markdown, welcome_email, day_one_guide

__all__ = ["build_plan", "username_for", "checklist_markdown", "welcome_email", "day_one_guide"]
__version__ = "0.1.0"
