# Power BI Report Assets

This folder contains the Power Query, DAX and supporting assets used to build the Partner Ecosystem Performance Analytics report in Power BI Desktop.

The completed report contains four analytical pages:

1. Executive Overview
2. Partner Performance
3. Pipeline Health
4. Opportunity Analysis

Dashboard screenshots and the complete four-page PDF are available in the repository’s `assets` folder.

## Analytical Model

The Power BI model loads four analytical tables:

- `dim_date`
- `dim_partner`
- `dim_vendor`
- `fact_opportunity`

`DataFolder.pq` defines the generated-data location, while `fnReadCsv.pq` provides reusable CSV-loading and type-conversion logic.

The dimension tables filter `fact_opportunity` through one-to-many relationships using the appropriate business keys.

## Measures

`measures.dax` contains the report’s business measures, including:

- Net bookings
- Booked gross profit
- Booked margin rate
- Closed win rate
- Open pipeline
- Stale pipeline
- Stale pipeline share
- Opportunity counts and average values

Bookings represent won opportunity value and should not be interpreted as recognized accounting revenue or collected cash.

## Validation

Headline Power BI results were reconciled with the validated Python and SQL pipeline outputs:

| Metric | Validated result |
|---|---:|
| Accepted opportunities | 1,195 |
| Net bookings | $25.92M |
| Booked gross profit | $3.79M |
| Booked margin rate | 14.62% |
| Closed win rate | 60.11% |
| Open pipeline | $29.48M |
| Stale pipeline | $18.30M |
| Stale pipeline share | 62.07% |

The report was built in Power BI Desktop, published to Power BI Service and exported to PDF. Public embedding was unavailable because embed-code creation is disabled by the organization’s tenant administrator. Scheduled refresh and public external access are outside the validated scope of this project.

## Rebuilding the Report

1. Run the Python pipeline to generate the clean model CSV files.
2. Set the `DataFolder` parameter to the generated version directory.
3. Create the Power Query parameter, helper function and four model queries using the files in this folder.
4. Create the star-schema relationships.
5. Add the measures from `measures.dax`.
6. Build the report pages and reconcile the headline metrics with the SQL outputs.

See [`../docs/POWER_BI_BUILD_GUIDE.md`](../docs/POWER_BI_BUILD_GUIDE.md) for detailed implementation guidance.