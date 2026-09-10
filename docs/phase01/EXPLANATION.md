# Phase 01 explanation

This is the companion to the code, written for Houssam's existing Python and data-science knowledge. Work through the sections in order with the named file open. Read the rationale first, attempt the small exercise, then inspect the supplied implementation. You do not need to memorize Python setup or every pandas/SQLite API call.

## 1 Choose the decision before the tables

A channel manager has limited time for partner follow-up. The report should connect closed bookings, deal conversion and stale opportunities to a concrete review queue. A beautiful chart that sums every CRM row would be less useful than a correctly defined table. Start by writing 'one latest opportunity as of 2026-08-31' at the top of your notes. That is the fact grain.

The chosen domain follows your CV's partner-database and vendor-business-development exposure. The source remains completely fictional. We have no permission, need or evidential basis to represent this as your employer's commercial performance. The generator's trends are not external facts. A distinctive business question is useful; global uniqueness or guaranteed interviews cannot be established.

First write the metric definitions in docs/METRIC_CONTRACTS.md. Net bookings counts only Won value. Closed win rate counts Won divided by Won plus Lost. Open pipeline has no close date and is measured at the snapshot date. If you cannot explain why these need different date treatment, do not begin DAX yet.

## 2 Recognize the two comment types

INTERVIEW FOCUS marks logic you should be able to reason through, change and reconstruct: grain, revision order, exact money, invalid-data policy, denominator choice and filter context. You may consult documentation for syntax in a real job, but you should not need a tutorial to decide what the calculation means.

READ ONLY marks wiring: argparse, UTF-8 CSV writing, module entry points and environment/CI setup. Understand the purpose and recognize failures. Do not spend interview preparation time memorizing every keyword or option. Setup can still contain real bugs; the label is a learning priority, not a guarantee that code is trivial or safe to ignore.

For example, 'drop exact duplicate exports, then identify the latest revision, then validate it' is interview-focus reasoning. The exact argparse declaration for --raw-dir is read-only wiring.

## 3 Generate a source with realistic imperfections

Open partner_analytics/generate.py. Write the two reference-table structures first: partner and vendor. Then inspect how each opportunity gets an ID, creation date, stage-change date, update date, stage and exact cent amounts. This gives one final record per opportunity before export defects are introduced.

random.Random(seed) is local to the generator, so its draws are reproducible and do not depend on some notebook's global random state. Date ordering is created <= stage changed <= updated <= as of. Won/Lost closes on its final stage-change date; open opportunities have no actual close date. A quoted cost can exceed price, allowing a loss-making deal. That is valid business data.

The generator adds 120 older revisions and 30 repeated exports. It then includes five deliberately defective latest records: unknown partner, negative value, impossible close chronology, open deal with a close date and invalid creation date. These are seeded test cases, not bugs we discovered in a real CRM. There are 1,350 raw rows for 1,200 distinct opportunity IDs.

Exercise before running: what count should remain if five latest records are invalid and the pipeline never falls back to an earlier revision? Answer: 1,195 accepted opportunities. This predicts the expected result before the pipeline computes it.

## 4 Load explicit types and validate identity

Open quality.py. read_source reads all CSV fields as text with keep_default_na=False. Identifiers such as P001 must remain identifiers; empty values should be explicitly checked. Whitespace is normalized before duplicate comparison. The required column set is strict: a changed CRM export schema fails visibly rather than feeding a partially understood dataset downstream.

validate_dimension rejects empty values and duplicate keys. If dim_partner had two rows for one key, an ordinary join could multiply opportunity rows. A dashboard can look normal while summing inflated amounts, so the dimension check is a business protection.

Missing opportunity IDs or invalid/future update dates stop the batch. These fields establish identity and revision order. A quarantine policy is not enough if we cannot determine which record is current. Date precision is daily in this simulation; conflicting newest records on the same date are considered ambiguous. A production source should supply a trustworthy timestamp or revision sequence.

## 5 Select the latest revision without hiding errors

Write this algorithm in pseudocode before following clean_opportunities. Remove identical normalized rows. Group the remaining records by opportunity_id. Identify the maximum updated_date per group. Keep rows whose date matches that maximum. If more than one conflicting record remains for an opportunity, stop. Only then validate business fields.

The library-specific step is groupby(...).transform('max'). Unlike an aggregation that returns one row per group, transform produces a value aligned to every original row. Comparing each row's update date to its group's maximum creates the latest-record mask without a merge. ISO YYYY-MM-DD dates can be ordered lexicographically after strict validation.

The ordering prevents a subtle analytical error. Suppose the older record says Won for $100 but the newer record has an invalid amount. Filtering the bad amount first could resurrect the outdated Won row. The dashboard would silently report $100. Our pipeline excludes the entire invalid latest opportunity and records why. That exclusion can bias results too, so quarantine is disclosed rather than presented as free accuracy.

The accepted list is sorted by ID to keep exports stable. Input row order does not choose winners. Sorting is not a substitute for an explicit tie policy.

## 6 Validate money dates and business rules

The cents function converts text through Decimal, checks finiteness, checks that no fraction of a cent would be discarded, checks the stated range and converts to integer cents. '0.10' becomes 10 exactly. A value of '1.001' is rejected rather than rounded. Floating-point error is a representation issue; it should not decide whether a reconciliation matches.

Do not reject all cost > price records. Those represent valid negative margins in this case. Reject negative costs, malformed values and impossible lifecycle dates. Won/Lost must have a close date aligned with its final stage; an open deal must not have an actual close date. An expected close date would be a different field and is deliberately not used here.

Rejected latest records keep their original normalized fields and rejection_reasons. Reasons can overlap, so the sum of reason counts is not necessarily the number of rejected records. The row reconciliation is exact: raw = exact duplicates + superseded revisions + quarantined latest + accepted latest. This release evaluates to 1,350 = 30 + 120 + 5 + 1,195.

Exercise: temporarily make an open deal's stage_changed_date equal to its creation date, then rerun. Explain why its stale classification may change even if the most recent general CRM update does not. Reset the source with the generator afterwards.

## 7 Build the SQL warehouse

Open sql/01_schema.sql before pipeline.py. Write the unique keys and foreign keys first. dim_partner and dim_vendor describe opportunities; dim_date supplies a complete calendar. fact_opportunity stores one accepted latest opportunity. This is a star schema with multiple date roles, not a pre-aggregated spreadsheet with repeated monthly totals.

SQLite is an actual relational SQL engine embedded in Python. It makes this phase portable and removes server-setup work that does not yet advance the analysis. Joins, CTEs, window functions, constraints and safe aggregation are substantive SQL skills. Production deployment may call for PostgreSQL or a warehouse later; copying this exact SQLite date syntax into another engine would require adaptation.

Foreign-key enforcement is explicitly enabled because SQLite does not enable it for every connection by default. Dates reference the calendar, and keys reference their dimensions. Parameterized value inserts keep data separate from SQL syntax. Table names are internal constants, not user-supplied strings.

Indexes support common joins and date access, but this release does not claim a measured performance improvement at this small scale. Query-plan analysis and timing belong in a later exercise if a concrete bottleneck appears.

## 8 Calculate SQL measures at the right grain

Open sql/02_metrics.sql. v_kpis uses conditional aggregation: SUM(CASE WHEN stage='Won' THEN amount_cents ELSE 0 END). Each accepted opportunity contributes once. It divides by 100 only for the dollar output. Booked gross profit sums price minus cost for won deals.

Closed win rate multiplies the numerator by 1.0 to avoid integer division and uses NULLIF(denominator,0). A zero denominator becomes SQL NULL rather than an error or misleading zero. Margin rate is total booked gross profit divided by total bookings. Average deal margin would give small and large deals equal weight, answering another question.

In v_vendor_month, construct the calendar/vendor grid before joining activity. Without this grid, LAG might compare March to January when February has no wins. The dense grid makes February explicitly zero. Percentage growth from zero remains undefined even when the absolute change is known. The first available month has no prior comparison.

v_partner_review starts from the partner dimension and LEFT JOINs facts so partners without activity survive. It reports the last 90 calendar days of closed outcomes and all current open pipeline. DENSE_RANK orders stale dollar exposure and preserves ties. The five-closed-deal note discourages overinterpreting sparse conversion data; it is not a confidence interval.

## 9 Check the arithmetic independently

The tests use two Won deals: $100 with $60 cost, and $300 with $270 cost; one $500 Lost deal; a $200 stale open deal and an $800 fresh open deal. Compute results before looking at the test assertions.

Bookings = $400. Booked gross profit = $70. Booked margin = 70/400 = 17.5%. Closed win rate = 2/3 = 66.67%. Open pipeline = $1,000. Stale pipeline share = 200/1,000 = 20%. The unweighted average of the two won margin percentages would be 25%, which is not the booked margin rate.

The source also includes a partner with no opportunities to check LEFT JOIN preservation. A separate fixture puts deals in January and March to prove that February's zero appears in the lagged comparison. These tests inspect expected behavior, not merely whether the code runs.

## 10 Publish a complete local version

Open pipeline.py. The pipeline validates sources, creates a temporary build directory, writes the warehouse, executes SQL and exports the model and analysis CSVs. It closes the database before moving the directory. A manifest records source and code hashes plus pandas/SQLite versions. The version ID derives from that identity.

The new output is stored under outputs/versions/<dataset-id>. CURRENT.txt changes only when the complete version is available. A failed reference-data check leaves the previous pointer intact. Same inputs, implementation and recorded dependency versions reuse the same directory. Treat that directory as immutable; regenerate from source instead of editing its contents.

This is a single-writer batch design. It is not a concurrent transactional publishing service. SQL table changes are committed before publication, but the files and database are not described as a universal distributed transaction. The pointer pattern solves the specific 'read a half-built export' problem for this workflow.

The real issue corrected during implementation was SQLite connection lifetime. 'with sqlite3.connect(...)' alone manages transaction success/failure but does not close the connection. The final implementation uses contextlib.closing and an explicit commit before moving the build. This was found in code review; we did not reproduce a Windows file-lock failure. See the bug log for the honest account.

## 11 Run and inspect evidence

Use the platform-specific README commands from the repository root. The generated files are intentionally ignored by Git. Open CURRENT.txt and then the directory it names. quality_report.json should show reconciled=true and the four category counts. quarantine.csv lets you inspect each excluded latest record.

For the default seed, SQL reports $25,920,062.28 in synthetic bookings, $3,789,259.60 booked gross profit, 437 wins among 727 closed deals, $29,478,195.15 open pipeline and $18,297,698.41 stale pipeline. These are regression/reference values, not business achievements. Compare them with examples/expected_quality_report.json.

Do not use the sample's 60.11% conversion or 62.07% stale share as external performance benchmarks. The distributions were created by the generator. A genuine recommendation memo will acknowledge that limitation and emphasize how an analyst would investigate the pattern.

## 12 Complete your learning checkpoint

Explain the latest-invalid-record example without looking at the code. Then change one data rule locally, run a relevant test, inspect the quarantine difference and revert or document the change. Finally reproduce the two-won-deal arithmetic independently in Excel with SUMIFS and counts. You do not need an automated workbook for this small cross-check.

Review the README's interview questions and answer them out loud using your own language. If an answer only repeats this file and you cannot show the code it refers to, the phase is not yet personally mastered. Your next session starts with the first unclear decision, then moves to SQL interpretation and the native Power BI model.
