// preserve the declared grain and types across SQL and Power BI.
fnReadCsv("dim_date.csv", {
    {"date_key", type date},
    {"year", Int64.Type},
    {"month_number", Int64.Type},
    {"month_start", type date},
    {"month_label", type text}
})
