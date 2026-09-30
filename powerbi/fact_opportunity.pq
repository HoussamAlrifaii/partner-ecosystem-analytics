// preserve the declared grain and types across SQL and Power BI.
fnReadCsv("fact_opportunity.csv", {
    {"opportunity_id", type text},
    {"partner_id", type text},
    {"vendor_id", type text},
    {"created_date", type date},
    {"updated_date", type date},
    {"stage_changed_date", type date},
    {"closed_date", type date},
    {"stage", type text},
    {"amount_cents", Int64.Type},
    {"cost_cents", Int64.Type},
    {"as_of_date", type date}
})
