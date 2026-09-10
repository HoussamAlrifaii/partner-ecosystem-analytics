# Phase 01 validated data foundation

Engineering: implemented and tested. Houssam walkthrough: pending. Power BI native execution and deployment: later phases.

Read EXPLANATION.md before executing the files listed in the root README. This phase implements a repeatable source-to-SQL pipeline and prepares typed Power BI imports. The business contract is in ../METRIC_CONTRACTS.md and actual evidence in ../VALIDATION.md.

## Exit checklist

- [x] Generator, validation, SQL warehouse and exports run successfully.
- [x] Thirteen tests pass; source counts reconcile.
- [x] Separate explanation, interview answers and validation evidence supplied.
- [ ] Houssam runs the pipeline and explains the revision-selection rule.
- [ ] Houssam changes one validation rule and verifies the consequences.
- [ ] Remote phase commit verified on GitHub.

## What recruiters will actually ask

**What is the grain?** One accepted latest CRM record per opportunity as of 2026-08-31. Source revisions are not multiple sales.

**Why select the latest record before filtering invalid amounts?** Filtering first can revive an outdated stage or value and produce an apparently clean but incorrect fact. I quarantine the invalid latest record and disclose the exclusion.

**What happens when two latest revisions conflict?** The pipeline stops because there is no trustworthy ordering key. Choosing whichever row happens to appear last would depend on export order.

**Why store cents?** USD amounts are parsed with Decimal and stored as integer cents so sums are exact at the declared precision. Rates and displayed dollars are converted only after aggregation.

**Why is win rate sometimes blank?** With no closed deals, the ratio is undefined. Zero would imply actual losses and mislead the reader.

**What happens on a failed refresh?** A new version is prepared separately, and CURRENT.txt changes only after a successful build. A test confirms a reference-data failure preserves the last successful pointer. The phase is designed for one batch writer.

**What engineering issue did you fix?** During code review I caught that a sqlite3 connection context commits or rolls back but does not close the connection. I added contextlib.closing before moving the version directory. The final tests ran on Linux; Windows locking behavior has not been directly tested.
