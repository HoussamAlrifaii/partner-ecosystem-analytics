# Power BI starter assets — native execution pending

These are editable Power Query (M), DAX and theme files. They are not a PBIX report. Read docs/POWER_BI_BUILD_GUIDE.md. Power BI Desktop must execute and validate them in phase 03. The build has not run in the current Linux workspace.

Create DataFolder, then fnReadCsv, then the four table queries, using the exact query names. Import relationships manually; do not load SQL aggregate CSVs into the analytical star. Each DAX measure is created separately. The CSV bridge is deliberate: SQL remains the tested transformation/analysis engine, while Power BI remains the native semantic and visual layer. A direct database connector is not required to demonstrate this end-to-end flow.

## What recruiters will actually ask

**Why use a star schema?** Separate dimensions have unique keys and filter a fact at one explicit grain, making totals and filter behavior predictable. I verify joins preserve the opportunity count.

**Why does pipeline ignore the closed-date slicer?** Open deals have no close date and pipeline is measured as of one fixed snapshot. I show the as-of date on its own page and preserve vendor/partner filters.

**How do you know DAX agrees with SQL?** The pipeline exports independent SQL totals. In phase 03 I will check unfiltered totals, vendor filters, a closed month, blank denominators and date-filter behavior. Those native checks are pending; code review alone does not establish agreement.

**Have you deployed this report?** Not yet. A native report and verified sharing/refresh evidence are required before claiming deployment.
