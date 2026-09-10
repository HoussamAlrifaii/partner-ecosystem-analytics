// 🎯 INTERVIEW FOCUS — preserve the declared grain and types across SQL and Power BI.
fnReadCsv("dim_vendor.csv", {
    {"vendor_id", type text},
    {"vendor_name", type text},
    {"category", type text}
})
