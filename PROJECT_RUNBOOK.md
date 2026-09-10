# Project runbook

Owner: Houssam Alrifaii. Project: Partner Ecosystem Performance Analytics.
Updated: 2026-09-10. Overall status: BUILD IN PROGRESS; no live Power BI report yet.

## Working agreement

Build one phase at a time. Read the phase explanation before running its code. Houssam should be able to explain the interview-focus decisions and change them independently. READ ONLY means recognize the purpose; it does not mean ignore behavior. The assistant provides implementation and validation; Houssam practices and owns the explanation. Credentials and familiarity with Python/ML are assumed.

Each delivered phase contains code, a separate explanation, a README with 'What recruiters will actually ask' and answers, validation evidence, a runbook update, a separate Git commit, and a downloadable ZIP. Never convert a planned capability into a CV achievement. Keep real employer data and private CV/contact details outside this repository.

## Phases and exit criteria

| Phase | Scope | Engineering status | Houssam's checkpoint / exit gate |
|---|---|---|---|
| 00 | Research and business/metric contracts | Prepared | Explain the decision, grain, denominator and synthetic-data limits |
| 01 | Reproducible CRM cleanup, SQL warehouse, quality checks, Power BI starter queries | Implemented; 13 tests passed | Run locally; change one validation rule; reconcile known example by hand |
| 02 | Deeper SQL analysis and analyst recommendation memo | Planned | Quantify drivers with denominators and uncertainty; distinguish association from causation |
| 03 | Native Power BI semantic model and dashboard | Starter M/DAX supplied; not executed in Power BI | Create/save .pbix (or validated .pbip), check relationships, DAX/filter behavior, drill-through, performance and accessibility |
| 04 | Deployment and refresh | Docker configuration supplied; not executed | Run container; publish report; verify viewer access and refresh; capture actual evidence |
| 05 | Recruiter release and CV evidence | Planned | README links/screenshots/video, rehearsed answers, measured claims, final ZIP and phase commit |

All phases are required for the final project. The current ZIP is a foundation release, not a completed portfolio project. Future phase implementation will be explained before delivery.

## Scope

Python/pandas cleans synthetic CRM exports. SQLite stores a relational star schema and executes SQL. CSV extracts carry typed tables to Power Query. DAX defines report measures. Power BI presents the business narrative. GitHub keeps source and validation history. SQLite avoids a database server for the first learning phase; SQL is executed by a real engine. A server database is a later option only if deployment needs it.

The model describes a fictional technology distributor with four fictional vendors and 48 fictional partners. It uses no Redington, Fortinet, Microsoft, Huawei or Pure Storage commercial data. Snapshot date is fixed at 2026-08-31 for reproducibility. This is descriptive analytics; there is no ML model, forecast, causal claim or historical pipeline reconstruction.

## First session

1. Read START_HERE.md and docs/phase01/EXPLANATION.md, sections 1-3.
2. Before running anything, say why latest-record selection comes before amount/date validation.
3. Run the generator, pipeline and tests using the commands in README.md.
4. Open the quality report, reconcile source rows and inspect the SQL KPI export.
5. Explain one test, then complete the exercises before advancing to native Power BI.

## Status and evidence

See docs/VALIDATION.md for commands actually executed. No Docker, Power BI Desktop, Power BI Service or GitHub Actions execution is implied by the presence of configuration files.

GitHub connection: HoussamAlrifaii was identified. Connected actions do not expose repository creation. This release keeps local phase commits and a Git bundle so history can be pushed when an empty destination repository is available. A remote push must be verified before this status changes.

## Change control

Add scope only when it answers a business question or proves an advertised skill. No chatbot, forecasting model, scraped partner emails, Kubernetes or unrelated AI subscriptions in this analyst project. Record real implementation bugs in docs/BUG_LOG.md; deliberate bad input examples are test cases, not discoveries.
