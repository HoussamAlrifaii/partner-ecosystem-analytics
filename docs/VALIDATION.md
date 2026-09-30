# Validation evidence

Executed 2026-09-10 in the provided Linux workspace. Python 3.12.14; pandas 2.2.3. All data synthetic; as-of date 2026-08-31. Evidence describes this foundation release, not a production deployment.

## Commands actually executed

~~~bash
python -m unittest discover -s tests -v
python -m partner_analytics.generate
python -m partner_analytics.pipeline
~~~

Result: 13 tests passed. Default pipeline completed and reported reconciled=true. Row categories: 1,350 raw; 30 exact duplicates; 120 older revisions; 5 invalid latest records; 1,195 accepted opportunities. Joined dimension/fact count remained 1,195.

## Meaningful checks

| Behavior | Evidence |
|---|---|
| Exact money and invalid precision | 0.10 maps to 10 cents; NaN/infinity/negative/fractional-cent values rejected |
| Latest revision precedes validation | Invalid newest value quarantined; older valid record not revived |
| Ambiguous update order | Conflicting latest or invalid/future update dates fail |
| Deduplication | Repeated identical opportunity does not increase fact count |
| Business validity | Bad dates/keys/negative cost rejected; negative margin allowed |
| Known KPI arithmetic | $400 bookings, $70 gross profit, 17.5% margin, 2/3 win rate, 20% stale share |
| Zero denominators | SQL ratios return NULL |
| Stale threshold boundary | 60 days is fresh under the strict >60 rule; 61 days is stale |
| Calendar continuity | March compares with zero February, not January |
| No-activity partners | LEFT JOIN preserves a partner with zero closed deals |
| Failed refresh | Duplicate dimension key does not change last successful pointer |
| Repeat run | Same identity reuses the version and metrics |
| Demonstration source | Exact row reconciliation and no join fanout |

The test count is 13; some tests exercise multiple related assertions. See tests/test_pipeline.py for the executable specifications. examples/expected_quality_report.json is the generated baseline, not a handcrafted claim of business success.

## Not executed yet

Power Query and DAX were executed in Power BI Desktop on Windows. The completed report contains four pages: Executive Overview, Partner Performance, Pipeline Health and Opportunity Analysis. Headline dashboard results were reconciled with the validated pipeline outputs, including $25.92M net bookings, $3.79M booked gross profit, a 14.62% booked margin rate, a 60.11% closed win rate, $29.48M open pipeline and a 62.07% stale pipeline share. The report was published to Power BI Service and exported as a four-page PDF. Public embedding was not enabled by the organization’s Power BI administrator. Scheduled refresh, public external access and Docker execution were not validated.
