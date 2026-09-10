# Business and metric contracts

Decision owner: a fictional channel sales manager. Monthly decision: which partner/vendor combinations warrant review, and whether weak bookings coincide with conversion, margin or stale-pipeline problems. Weekly decision: which open opportunities need owner follow-up. A flag suggests investigation, not proof of cause.

## Data grains and dates

- dim_partner: one current descriptive record per partner; no slowly changing history is claimed.
- dim_vendor: one record per fictional vendor.
- dim_date: one calendar date from 2025-01-01 through the fixed as-of date.
- fact_opportunity: one accepted latest CRM record per opportunity as of 2026-08-31. Monetary fields are integer USD cents; all amounts are net of discounts, excluding tax, freight and rebates in this simulation.
- source rows: export revisions, so the source grain is opportunity + update date, with occasional repeated exports.
- Closed performance uses closed_date. Open pipeline is a point-in-time stock at the as-of date. Today's stage cannot establish last month's pipeline. created_date is a separate cohort question.

## Primary metrics

| Metric | Formula / grain | Time and exclusions | Intended action |
|---|---|---|---|
| Net bookings USD | SUM(amount_cents)/100 for Won opportunities | Closed date in selected period; exclude open/lost/quarantined records | Review vendor/partner contributors to change |
| Closed win rate | Won count / (Won count + Lost count) | Closed date in selected period; NULL/blank for zero closed deals | Investigate conversion with counts displayed |
| Stale pipeline share | Open USD in stage >60 days / all Open USD | Fixed as-of date; ignores closed-date slicer; blank if no open USD | Review aged deals and stale CRM records |

The 60-day threshold is a demonstration policy, not an empirically optimized or industry benchmark. Its purpose is to make a review queue; show sensitivity before recommending operational adoption.

## Supporting metrics and guardrails

Booked gross profit = SUM(amount_cents - cost_cents)/100 for Won. Booked margin rate = SUM(won gross profit)/SUM(won amounts), never average row margin percentages. Bookings are signed deal value, not recognized accounting revenue or cash. Costs are quoted direct costs only, not complete operating expenses. Cost above price is valid and can create negative margin; negative costs are invalid.

Current open pipeline includes Qualified, Proposal and Negotiation. Open deals must have no actual closed date. Won/Lost must have a close date between creation and the as-of date. Stale days use stage_changed_date, not the most recent CRM edit. A deal opened long ago can have a fresh stage.

Closed win rate is deal-count weighted. Value-weighted win rate would be a different measure. Show the closed-deal denominator; do not rank tiny samples as firm evidence. Initial partner action view limits conversion commentary to at least five closed deals in the last 90 calendar days (June 3-August 31 inclusive). This is a demo guardrail, not statistical confidence.

Data quality: raw rows = exact duplicates removed + superseded revisions + quarantined latest records + accepted latest records. Report invalid-record reasons and their observed valid numeric value where possible; excluded errors can bias results, so do not silently bury them. Critical reference-file defects or ambiguous latest timestamps stop the run. Do not fall back to an older valid record when the newest one is invalid.

No growth targets, lift percentages, employer outcomes or claims of market uniqueness are assumed. Any synthetic trend is a generator artifact until supported by real independently obtained evidence.
