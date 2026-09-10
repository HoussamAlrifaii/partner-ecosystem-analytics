# Partner Ecosystem Performance Analytics

A Data Analyst portfolio project by Houssam Alrifaii, built in guided phases with AI assistance. **Foundation release; Power BI report and deployment are still in progress.**

A fictional technology distributor needs to understand which vendors drive bookings, where partner conversion deserves review, and which open opportunities have stalled. This project connects Python/pandas cleanup, a SQL star schema and a native Power BI build. All data is synthetic. The project demonstrates implementation and analytical judgment; it makes no claim of impact at Houssam's employer.

## Evidence available today

- Reproducible generator: 1,350 CRM export rows, including revisions and deliberate defects.
- Validated pipeline: 30 exact duplicates removed, 120 superseded revisions, 5 quarantined latest records, 1,195 accepted opportunities.
- SQL: constrained relational tables, joins, conditional aggregation, CTEs, window functions, safe ratios, zero-month handling and partner review outputs.
- Thirteen passing tests against independently specified examples and failure cases. See docs/VALIDATION.md.
- Commented M/DAX starter files and a detailed Power BI build guide. Native execution remains pending.
- Local phase commits; remote repository/push and GitHub Actions execution remain pending.

## Start here

Open START_HERE.md, then docs/phase01/EXPLANATION.md. The downloadable guide expands the walkthrough. Read the first three explanation sections before running the supplied implementation.

Windows PowerShell, from this project folder, with Python 3.12 installed:

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m partner_analytics.generate
.\.venv\Scripts\python.exe -m partner_analytics.pipeline
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

macOS/Linux, with Python 3.11 or 3.12 installed:

~~~bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m partner_analytics.generate
.venv/bin/python -m partner_analytics.pipeline
.venv/bin/python -m unittest discover -s tests -v
~~~

Power BI Desktop authoring requires a supported Windows environment; the Python/SQL phase can run on macOS/Linux. An operating-system-specific Power BI installation walkthrough is deferred until Houssam's machine is confirmed. The CI/Docker configuration targets Python 3.12; see the recorded local version in docs/VALIDATION.md.

Copy the version-directory path printed by the pipeline into the Power Query DataFolder parameter. It contains warehouse.sqlite, four model CSVs, three SQL analysis CSVs, quarantine.csv, quality_report.json and manifest.json. CURRENT.txt points to the last successfully published local version. Re-running identical inputs/code/environment reuses the same version. Do not edit version files; regenerate from source.

## How everything connects

Python reads and validates the CRM exports. SQLite persists the dimensions and opportunity fact and executes the SQL analysis. The pipeline exports those four model tables to CSV. Power Query loads and types them; Power BI relationships and DAX provide interactive measures. SQL summary exports are reconciliation evidence, not extra facts to join into the model. Power BI Service sharing and refresh are completed in the deployment phase.

## Repository map

| Location | Purpose |
|---|---|
| partner_analytics/generate.py | Synthetic CRM and reference exports |
| partner_analytics/quality.py | Schema, revision and row-quality contracts |
| partner_analytics/pipeline.py | Warehouse, SQL outputs, audit and immutable versions |
| sql/01_schema.sql, sql/02_metrics.sql | Relational model and business analysis |
| tests/test_pipeline.py | Thirteen meaningful tests |
| powerbi/ | Editable M, DAX and theme starters |
| docs/phase01/ | Guided explanation and interview preparation |
| docs/METRIC_CONTRACTS.md | Definitions, grain, exclusions and dates |
| research/JOB_REQUIREMENTS.md | Seven sourced job descriptions and scope decisions |
| PROJECT_RUNBOOK.md | Phase status and completion gates |

## Deployment status

Dockerfile and CI workflow are scaffolds, not execution evidence. In phase 04 run:

~~~bash
docker build -t partner-analytics:phase01 .
docker run --rm -v partner-analytics-output:/app/outputs partner-analytics:phase01
~~~

The named Docker volume retains the generated warehouse; a host bind mount can be used when a local Power BI process needs the CSVs. The container runs a batch job, not an HTTP dashboard. Power BI publication is a separate deliverable. Do not call this project fully deployed until the container and native report have been executed and verified.

## Limits

One fixed current snapshot; no historical pipeline, sales targets, forecasts, causal claims, real partner records or multi-currency conversions. SQLite/file exports suit this learning-sized batch; concurrent writers and enterprise refresh are outside phase 01. Negative gross margin is possible and is not removed as an error. All money is synthetic net deal value, not accounting revenue. Missing/invalid latest opportunities are visible in quarantine and can bias reported KPIs.

## What recruiters will actually ask

**What business decision does this support?** It gives a channel manager a vendor/partner breakdown of closed bookings and conversion plus a current stale-opportunity review queue. A flag initiates investigation; it does not prove the reason for a lost deal.

**How did you stop duplicate totals?** I separate exact duplicate exports from older revisions, select one unambiguous latest record per opportunity, enforce unique dimension keys and verify the joined count equals the fact count.

**Why Python and SQL together?** Python handles reproducible file ingestion, precise validation, quarantine and orchestration. SQL expresses auditable relational transformations and business aggregations. Power BI provides interactive exploration over the same clean grain.

**Why not call bookings revenue?** Won deal value is not a schedule of recognized revenue or cash receipts. This source cannot establish either, so the report labels the quantity as bookings.

**What did you empirically validate?** Thirteen tests cover known KPI arithmetic, revision conflicts, invalid latest records, referential quality, exact decimal parsing, empty denominators, missing months, stage-age boundaries and repeat runs. DAX and deployment still need their own execution evidence.

**Did this improve sales?** No real business outcome has been measured. This is a synthetic portfolio case. I can demonstrate the workflow and describe the validation design without attributing fictional results to my employer.

**Did you write everything independently?** The assistant generated the initial implementation with explanations. My learning checkpoints require me to explain the design, modify it and reproduce key logic. I will claim only the parts I can demonstrate and defend.
