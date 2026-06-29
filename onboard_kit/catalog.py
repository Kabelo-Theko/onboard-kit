"""What each department needs.

This is the part a real IT team keeps in its head or a spreadsheet: which
software, access groups and hardware a new person needs depending on where they
work. Keeping it as data means onboarding a new department is a small edit here,
not a code change. Tuned for a multi-store retail brand.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DeptProfile:
    software: list[str] = field(default_factory=list)
    access_groups: list[str] = field(default_factory=list)
    hardware: list[str] = field(default_factory=list)
    m365_license: str = "Microsoft 365 Business Basic"


DEPARTMENTS: dict[str, DeptProfile] = {
    "Retail / Store": DeptProfile(
        software=["Point-of-sale app", "Time and attendance"],
        access_groups=["Store-Staff", "POS-Users"],
        hardware=["Store PC login", "POS terminal access"],
        m365_license="Microsoft 365 Business Basic",
    ),
    "Design / Studio": DeptProfile(
        software=["Adobe Creative Cloud", "Asset library client"],
        access_groups=["Design-Team", "Brand-Assets"],
        hardware=["High-spec laptop", "Colour-calibrated monitor"],
        m365_license="Microsoft 365 Business Standard",
    ),
    "Warehouse / Distribution": DeptProfile(
        software=["Warehouse / inventory system"],
        access_groups=["Warehouse-Staff", "Inventory"],
        hardware=["Shared warehouse terminal", "Handheld barcode scanner"],
        m365_license="Microsoft 365 Business Basic",
    ),
    "Marketing / Ecommerce": DeptProfile(
        software=["Adobe Creative Cloud", "Ecommerce admin", "Social scheduler"],
        access_groups=["Marketing", "Ecommerce-Admin"],
        hardware=["Laptop", "Docking station"],
        m365_license="Microsoft 365 Business Standard",
    ),
    "Head Office / Admin": DeptProfile(
        software=["Finance/HR portal (as required)"],
        access_groups=["Head-Office-Staff"],
        hardware=["Laptop", "Docking station", "External monitor"],
        m365_license="Microsoft 365 Business Standard",
    ),
}

# Used when the given department is not in the catalog.
DEFAULT_PROFILE = DeptProfile(
    software=[],
    access_groups=["All-Staff"],
    hardware=["Laptop"],
    m365_license="Microsoft 365 Business Basic",
)


def profile_for(department: str) -> tuple[DeptProfile, bool]:
    """Return (profile, matched). matched is False when the default was used."""
    if department in DEPARTMENTS:
        return DEPARTMENTS[department], True
    # try a forgiving match on the first word (e.g. "Retail")
    head = department.strip().lower().split()[0] if department.strip() else ""
    for name, prof in DEPARTMENTS.items():
        if name.lower().startswith(head) and head:
            return prof, True
    return DEFAULT_PROFILE, False


def is_senior(role: str) -> bool:
    r = role.lower()
    return any(word in r for word in ("manager", "lead", "head", "supervisor", "director"))
