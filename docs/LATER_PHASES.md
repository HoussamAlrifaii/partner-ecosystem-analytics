# Remaining build and portfolio gates

This document describes the complete route after the runnable foundation. Detailed code for each later phase will be written alongside its explanation when that phase starts. Planned work is not represented as implemented. We will not bulk-finish the learning project in one opaque code delivery.

## Phase 02 analyze and recommend

Begin by choosing one management question: for example, why did a selected vendor's monthly bookings change? Write the period, inclusion rules and comparison before the SQL. Decompose the absolute change by partner, deal count and deal size. Make sure contributions sum to the reported change. Inspect sparse groups and partial periods. Do not claim that outreach caused conversion because the source has no treatment assignment, exposure dates or confounder controls.

Add SQL files for the question and a separate explanation. Use a small independent reconciliation example if the aggregation logic is new. Verify a sampled calculation in Excel with a pivot table or SUMIFS/COUNTIFS. Explain why this exercise is an independent calculation, not the core dashboard. Build a one-page analyst memo with decision, observation, evidence, caveat and proposed next check. Any numbers come from the actual run and are labeled synthetic.

If richer facts are needed, define their grain first. Outreach activities would be one row per activity, and monthly targets would be one row per vendor-month; joining either straight onto opportunities can multiply value. Historical pipeline requires snapshots or genuine event history available at each past time. We will add such a source only for a clearly scoped question, never backfill a fictitious history from today's final stages.

Recruiter question: How do you know a vendor's decline is not just deal mix? Prepared answer: I break the change into contributing partners and deal sizes, compare like-for-like segments with counts, and label unexplained association. I need additional evidence for a causal explanation.

Exit gate: one reproducible analysis, exact contribution reconciliation, an honest recommendation memo and a phase commit. No forecast or predictive model is needed to prove analyst competence.

## Phase 03 create the native report

Follow POWER_BI_BUILD_GUIDE.md, starting with the typed inputs and explicit relationships. Implement the smallest coherent report before adding drill-through or custom visuals. Verify raw totals, slices, blank denominators and date-role behavior. Then improve interaction, accessibility and performance using actual observations.

Recruiter question: How do you test a dashboard? Prepared answer: I check underlying rows and joins, compare measures against SQL at matching filter scopes, verify edge selections and exercise the report as a decision-maker. A visually plausible chart is not enough.

Exit gate: a saved native PBIX or verified PBIP, tested measures, useful pages, screenshots and a walkthrough Houssam can reproduce. Every added DAX or M file has the two learning comment categories where meaningful. A separate phase explanation records why the model behaves as it does.

## Phase 04 execute deployment and refresh

Build and run the container in a Docker-capable environment. Confirm the pipeline output, persistence and exit behavior. Publish the Power BI report through a usable account and choose sharing appropriate to fully synthetic data. Verify that the intended viewer can access it. Configure the actual data-refresh route and prove it updates the model. Record executed commands, dates, known restrictions and screenshots; do not reuse placeholders as evidence.

Recruiter question: Is a Dockerfile deployment? Prepared answer: It is deployment configuration. I can claim a deployed/reproducible batch only after running the image successfully; report hosting and refresh have separate checks.

Exit gate: verified batch run, native report access, tested refresh and a short operations runbook. If account/tenant limits block one route, document the real limitation and choose a supported route before marking the project complete.

## Phase 05 release and interview preparation

Revise the README to lead with the problem, recommendation and demo. Add architecture, data provenance, actual results, data-quality policy, reproduction commands, limitations and measured validation. Remove 'pending' only when the linked evidence exists. Package each finished phase and preserve its commit. Record a concise walkthrough that demonstrates one business decision and one technical correctness check.

Rehearse explaining grain, duplicate policy, ratio denominators, dates, why SQL and Python are both present, Power BI relationships, filter context, refresh, one bug and one tradeoff. Rebuild a key SQL aggregation or a validation example without copying it. There is no need to memorize every environment command.

Recruiter question: What can you honestly claim from a synthetic project? Prepared answer: I can claim the implemented workflow, artifacts, tests and measured system behavior. I cannot claim company revenue lift, real adoption or causal business impact.

Only then rewrite role-specific CV bullets. One possible structure is 'Built [verified artifact] using [relevant tools], handling [measured data volume/quality cases] and validated by [actual checks].' This is a template, not an achievement to paste before execution. Keep the role target focused and do not label this transition as senior employment experience.
