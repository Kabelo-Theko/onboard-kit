# onboard-kit

**Live demo: https://onboard-kit-eta.vercel.app/**

Turn a new starter's details into a complete IT onboarding pack.

Give it a name, department, role and start date. It produces three things every
IT team puts together by hand for each new person:

1. **A checklist** of everything to do before day one (accounts, licences,
   hardware, access), each task with an owner and a due date worked out from the
   start date.
2. **A welcome email** ready to send.
3. **A Day-1 IT orientation guide** in plain language for the new starter.

It is deterministic and template-driven on purpose. The same input always gives
the same plan, there are no surprises, and every line can be explained. The
department profiles (what software, access and hardware each team needs) live in
one file, so adding a department is a small edit, not a rewrite.

## Why I built it

Onboarding is the workflow IT repeats every few weeks, and it is easy to forget
a step when you are busy: the licence that was never assigned, the access group
that was missed. Encoding it once means a new starter is set up the same careful
way every time.

## How to run it

Standard library only. Python 3.10+.

```bash
# print the full pack to the screen
python -m onboard_kit.cli --name "Thabo Nkosi" --department "Retail / Store" \
    --role "Sales Assistant" --start 2026-07-15 --manager "Lerato M"

# write the three files to a folder
python -m onboard_kit.cli --name "Sara Daniels" --department "Design / Studio" \
    --role "Design Lead" --start 2026-07-15 --out ./onboarding
```

Departments understood out of the box: Retail / Store, Design / Studio,
Warehouse / Distribution, Marketing / Ecommerce, Head Office / Admin. Anything
else falls back to a sensible default set and is clearly flagged for review.

## The web UI

**Live: https://onboard-kit-eta.vercel.app/**

A multi-view web app. Fill in the starter's details and it builds the pack:

- **Department manifest** — the exact software and hardware for that team
  (a Design starter gets Adobe + a calibrated monitor; Retail gets the POS
  client + scanner; Warehouse gets the WMS client + handheld), not a generic
  placeholder.
- **D-minus checklist with owners** — every task shows when it is due (`D-3`,
  `D-1`, `Day 1`), who owns it (IT, IT / Asset, HR, Facilities, Manager) and the
  real calendar date, counting back from the start day.
- **Countdown timeline** — how many tasks fall on each day before the start.
- **Welcome email and Day-1 guide** — ready to copy.
- **Equipment register** — a pre-filled issue sheet (per-department hardware +
  access card) that doubles as the offboarding return checklist.
- **Print / Save PDF** — a print stylesheet renders a clean checklist or
  register straight to paper or PDF.
- A **Reference** tab shows every department manifest and the owner key.

Navigation collapses to a hamburger menu on small screens. It runs as a static
page (host `docs/` on Vercel or GitHub Pages), or behind the Python engine:

```bash
pip install -r requirements.txt
uvicorn web.server:app --reload
# open http://127.0.0.1:8000
```

With the server running, `POST /api/plan` builds the pack with the real
`onboard_kit` module. A `Dockerfile` and `render.yaml` are included for a free
deploy.

## Optional AI personalization

The deterministic pack is the default. A **Personalise with AI** button calls a
tiny serverless function (`api/ai.js`) to add a short role/department-specific
welcome paragraph to the email and a Day-1 tip to the guide. The key lives only
in the `NVIDIA_API_KEY` environment variable (Vercel project settings); without
it the pack generates exactly as before.

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## How it is put together

```
onboard_kit/
    catalog.py    what each department needs (software, access, hardware)
    planner.py    builds the task list with owners and due dates
    generate.py   renders the checklist, welcome email and Day-1 guide
    cli.py        the command-line front end
web/
    server.py     FastAPI: serves the UI and exposes the engine at /api/plan
docs/
    index.html    the pack-builder web UI (also the static demo)
tests/
    test_planner.py
Dockerfile, render.yaml   free one-click deploy
```

## Honest limitations

- The department profiles are a starting set modelled on a retail brand; a real
  deployment would tune them to the actual licences and systems in use.
- It plans and documents the work; it does not create accounts itself. That is
  deliberate, account creation should stay a reviewed action. The output is
  designed to drop straight into a ticket or a script later.

## Licence

MIT. See [LICENSE](LICENSE).
