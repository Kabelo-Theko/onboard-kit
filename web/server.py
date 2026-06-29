"""FastAPI server for onboard-kit: serves the web UI and exposes the Python engine.

  POST /api/plan -> build a plan with the real onboard_kit module and return the
                    checklist tasks, welcome email and Day-1 guide.
The web UI works on its own, but this lets the same logic run server-side.

Run:
    pip install -r requirements.txt
    uvicorn web.server:app --reload
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from onboard_kit.planner import Starter, build_plan
from onboard_kit.generate import welcome_email, day_one_guide

DOCS = Path(__file__).resolve().parent.parent / "docs"
app = FastAPI(title="onboard-kit", version="0.1.0")


class PlanRequest(BaseModel):
    name: str
    department: str
    role: str
    start: str          # YYYY-MM-DD
    manager: str = ""
    domain: str = "example.co.za"


@app.post("/api/plan")
def plan(req: PlanRequest):
    starter = Starter(name=req.name, department=req.department, role=req.role,
                      start_date=date.fromisoformat(req.start),
                      manager=req.manager, domain=req.domain)
    p = build_plan(starter)
    data = p.to_dict()
    data["welcome_email"] = welcome_email(p)
    data["day_one_guide"] = day_one_guide(p)
    return data


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse(DOCS / "index.html")


app.mount("/", StaticFiles(directory=DOCS, html=True), name="static")
