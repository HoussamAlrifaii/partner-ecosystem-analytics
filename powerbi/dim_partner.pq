// 🎯 INTERVIEW FOCUS — preserve the declared grain and types across SQL and Power BI.
fnReadCsv("dim_partner.csv", {
    {"partner_id", type text},
    {"partner_name", type text},
    {"region", type text},
    {"tier", type text}
})
