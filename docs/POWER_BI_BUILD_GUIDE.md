# Native Power BI build guide

Status: The four-page report has been built in Power BI Desktop, reconciled against the validated Python and SQL outputs, published to Power BI Service, and exported to PDF. Interface labels may vary between Power BI Desktop releases. Public embedding and scheduled refresh are outside the validated scope of this portfolio project.

## 1 Prepare the inputs

Run the Python generator and pipeline. Copy the local absolute version path printed at completion. This is your DataFolder; do not use the author's /workspace path. The folder contains dim_partner.csv, dim_vendor.csv, dim_date.csv and fact_opportunity.csv. It also contains SQL reference outputs, which you will compare with your DAX measures.

Open Power BI Desktop in a supported Windows environment and create a blank report. Save it as PartnerEcosystem.pbix in your local working folder. Keep it out of Git for now. Turn off automatic date/time tables for this file and create relationships deliberately, because we already have a complete date dimension. Use Import mode for these local CSV tables. This phase does not claim live database queries or DirectQuery.

## 2 Create Power Query parameters and tables

Choose Transform data to open Power Query. Create a blank query through New Source, then Blank Query. Open its Advanced Editor. Paste powerbi/DataFolder.pq, rename the query DataFolder, and replace its sample string with your own version-folder path. Forward slashes in Windows paths are convenient and avoid confusion when copying code. Keep the trailing slash off because the function adds it.

Create another blank query named fnReadCsv and paste its file. The function accepts a filename and a list of column/type pairs. It reads UTF-8 CSV, promotes the first row to headers, normalizes empty fields to null, and applies explicit types. This prevents an ID from turning into a number and makes empty closed dates valid for open deals.

Create the four remaining queries using their exact filenames without .pq: dim_partner, dim_vendor, dim_date and fact_opportunity. Paste each matching file. Only these four tables should load into the analytical model; DataFolder and fnReadCsv are a parameter and function. Inspect previews for errors, then Close & Apply. Do not use Remove Errors to make an unexplained failure disappear.

Expected fact count: 1,195. Expected partners: 48. Expected vendors: 4. The date table contains every day from 2025-01-01 to 2026-08-31 inclusive. Monetary columns are whole-number cents; dates are Date, not localized text. Source schema changes should be handled in the pipeline and typed queries, then revalidated.

## 3 Build and inspect relationships

Use Model view. Each relationship below is one-to-many, with a single filter direction from dimension to fact. Ensure the 'one' side really has unique keys. Delete unintended automatically created relationships before validating this explicit model.

| One side | Many side | State | Meaning |
|---|---|---|---|
| dim_partner[partner_id] | fact_opportunity[partner_id] | Active | Partner and region filters |
| dim_vendor[vendor_id] | fact_opportunity[vendor_id] | Active | Vendor and category filters |
| dim_date[date_key] | fact_opportunity[closed_date] | Active | Closed performance period |
| dim_date[date_key] | fact_opportunity[created_date] | Inactive | Creation-cohort questions only |

Mark dim_date as the date table using date_key. Sort month_label by month_start. Hide technical keys and cent columns from normal report authors if they are not needed for visible tables. Use explicit measures instead of implicit sums where metric semantics matter. Do not create bidirectional relationships to force a visual to show a desired value.

Open opportunities have a blank close date. That is expected. A close-date slicer would filter them out, so current pipeline measures explicitly remove the date-dimension filter. A relationship on created_date would answer a different question and would shift the apparent period of won bookings.

## 4 Add measures one at a time

Open powerbi/measures.dax. In Desktop, select the fact table and use New measure. Paste one definition at a time, with its measure name and expression. The file contains multiple separate measures; pasting the whole file into one measure is invalid. Format amounts as USD with appropriate decimal display, rates as percentages and counts as whole numbers.

CALCULATE changes filter context. The Won condition limits bookings to the won stage, while vendor/partner/date filters still apply. SUMX iterates the selected opportunities to calculate price minus cost or evaluate stage age. DIVIDE returns blank when its denominator is zero unless you deliberately provide another result. REMOVEFILTERS(dim_date) clears closed-period restrictions for current pipeline while preserving partner/vendor filters. KEEPFILTERS intersects the open-stage set with a selected stage, so a stage breakdown does not repeat the entire pipeline for each row. USERELATIONSHIP selects the inactive created-date relationship only inside the specifically named Created Opportunities measure.

The stale calculation is intentionally evaluated inside CALCULATE after the date filter is cleared. A table filter created before clearing the date context can already exclude every open opportunity, which is why the filtered-date acceptance check is essential. Code review suggests the intended behavior; execution in the native DAX engine is still required.

## 5 Build three decision focused pages

Page 1 is Closed performance. Add a title, a synthetic-data label and a close-date slicer. Add vendor, partner-region and partner-tier slicers. Show bookings, booked gross profit, margin, closed win rate and the closed-deal count. Use a monthly bookings line chart, a vendor bookings bar chart and a partner matrix with bookings, margin and closed counts. Keep win rate next to its denominator. Avoid a large number of decorative cards.

Page 2 is Partner review. Use a partner table with closed counts, conversion and current stale exposure. Show the as-of date prominently and distinguish the conversion period from the pipeline snapshot. Add drill-through to a partner detail page only when the detail adds useful context. Use explicit text labels alongside color so red/green is not the only signal. Our initial SQL partner-review output uses a fixed 90-day closed window; if you reproduce it in DAX, define that exact window and validate it instead of mixing it with an arbitrary slicer.

Page 3 is Current pipeline. Use a clear subtitle 'Synthetic snapshot as of 31 August 2026'. Show current open value, stale value and stale share by vendor and partner. Include a detail table of opportunity ID, stage, stage-change date and value to make follow-up actionable. Filter the table to open stages. Do not add a timeline labeled historical pipeline; there is no historical snapshot dataset. Keep the closed-date slicer off this page even though the measures deliberately ignore it.

The supplied theme is optional. Use consistent USD/percentage formats, meaningful titles, readable label sizes and restrained colors. Add tooltip definitions for bookings and stale status. A chart should state the quantity, period and grouping without the reader guessing them.

## 6 Verify numbers and interactions

Start with an unfiltered model. Check all values against examples/expected_quality_report.json and the generated v_kpis.csv. Do not validate DAX by comparing one visual to another visual using the same faulty measure.

| Check | Expected result | Evidence to record |
|---|---|---|
| Fact count | 1,195 unique opportunity IDs | Model count and source reconciliation |
| All-period bookings | USD 25,920,062.28 | SQL CSV and matching card |
| All-period booked gross profit | USD 3,789,259.60 | SQL CSV and matching card |
| Closed outcomes | 437 wins / 727 closed | Count measures and 60.1100 percent ratio |
| Current open pipeline | USD 29,478,195.15 | SQL CSV and matching card |
| Current stale pipeline | USD 18,297,698.41 | SQL CSV and matching card |
| Vendor and month filter | Exact corresponding v_vendor_month row | SQL row beside filtered visual |
| Closed-date slicer changed | Closed measures change; current pipeline remains constant for same partner/vendor selection | Before and after screenshots |
| Partner or vendor changed | Current pipeline changes with the selected dimension | Filtered SQL query and report result |
| Empty closed selection | Blank win rate; closed count zero | Screenshot and short explanation |

For a filtered SQL check, open warehouse.sqlite with a SQLite-capable editor. Aggregate directly over fact_opportunity with WHERE clauses for your selected partner/vendor/closed dates. Be explicit about filters: current pipeline must not inherit a closed_date constraint. Round only display values; compare stored counts/cents exactly and rates with an appropriate tolerance.

Use Performance Analyzer in Desktop to record an actual interaction, then inspect slow visuals if any. Do not promise a speed improvement without before/after measurements on the same data and machine. Record relationship state, visual checks and actual observed results in docs/VALIDATION.md. This acceptance table is a checklist, not evidence that those checks have already passed.

## 7 Save, publish and refresh

Save the native report after validation. If your version supports Power BI Project format and you choose it, verify the text project opens correctly before committing it. Otherwise distribute a reviewed PBIX as a downloadable release asset. Add screenshots and a short walkthrough showing the business question, filters, definitions and one quality check.

Publish through your actual Power BI account and workspace, then test access as the intended viewer. Sharing, licensing and tenant policies must be checked at that time. A link that only works for its author does not satisfy a recruiter demo. Local CSV paths do not become cloud-accessible when you upload a report. DataFolder currently pins an immutable dataset version; a new pipeline run does not automatically change that parameter. During deployment, either update the parameter to the new published version or implement and validate a source that resolves the current version before importing it. Choose and verify a supported refresh route: for example, an appropriate gateway for local files, or an approved cloud-hosted source with matching credentials. Document the actual route and run a refresh that demonstrably changes a controlled test value before restoring the baseline.

Publish to web exposes report/model content publicly and has tenant and license requirements. Use it only for the fully synthetic public demonstration. Do not combine a claim of confidential row-level restrictions with that public mode; if you demonstrate RLS later, validate it in an appropriate authenticated workspace separately. Official reference: https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web

Refresh reference: https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data

A successful Docker run proves the batch environment is reproducible. A successful Power BI Service publication proves report access. A successful refresh proves data updating. These are distinct checks. The final project needs the report experience and its verified evidence, not merely a Dockerfile.

## What recruiters will actually ask

**Why not join your SQL summary views into the fact table?** Monthly and partner aggregates have different grains and can multiply totals if joined carelessly. I load the base star tables and use SQL summaries as independent checks.

**What is the difference between a measure and a calculated column here?** Measures evaluate under report filter context and are appropriate for totals and ratios. A column is stored per row at refresh; using a ratio column and averaging it can change the business meaning.

**How would refresh work after publication?** I must configure a supported connection from the service to the source, provide the appropriate credentials/gateway or cloud path, and verify an actual refresh. Publishing a report does not automatically expose my local files.

**How would you demonstrate report quality?** I would show SQL-to-DAX reconciliation, a deliberately empty slice, date/partner filter behavior, accessible labels, a saved native report and a tested viewer link. These are planned native checks until evidence is recorded.
