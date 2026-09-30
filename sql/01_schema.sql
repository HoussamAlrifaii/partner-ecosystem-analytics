-- SQLite is the first-phase engine; no external server is needed.
PRAGMA foreign_keys = ON;
CREATE TABLE dim_partner (
    partner_id TEXT PRIMARY KEY NOT NULL,
    partner_name TEXT NOT NULL, region TEXT NOT NULL, tier TEXT NOT NULL
);
CREATE TABLE dim_vendor (
    vendor_id TEXT PRIMARY KEY NOT NULL,
    vendor_name TEXT NOT NULL, category TEXT NOT NULL
);
CREATE TABLE dim_date (
    date_key TEXT PRIMARY KEY NOT NULL,
    year INTEGER NOT NULL, month_number INTEGER NOT NULL,
    month_start TEXT NOT NULL, month_label TEXT NOT NULL
);
-- one current record per opportunity; source revisions are not additive.
CREATE TABLE fact_opportunity (
    opportunity_id TEXT PRIMARY KEY NOT NULL,
    partner_id TEXT NOT NULL REFERENCES dim_partner(partner_id),
    vendor_id TEXT NOT NULL REFERENCES dim_vendor(vendor_id),
    created_date TEXT NOT NULL REFERENCES dim_date(date_key),
    updated_date TEXT NOT NULL REFERENCES dim_date(date_key),
    stage_changed_date TEXT NOT NULL REFERENCES dim_date(date_key),
    closed_date TEXT REFERENCES dim_date(date_key),
    stage TEXT NOT NULL CHECK(stage IN ('Qualified','Proposal','Negotiation','Won','Lost')),
    amount_cents INTEGER NOT NULL CHECK(amount_cents >= 0),
    cost_cents INTEGER NOT NULL CHECK(cost_cents >= 0),
    as_of_date TEXT NOT NULL,
    CHECK((stage IN ('Won','Lost') AND closed_date IS NOT NULL)
       OR (stage NOT IN ('Won','Lost') AND closed_date IS NULL)),
    CHECK(created_date <= stage_changed_date AND stage_changed_date <= updated_date),
    CHECK(updated_date <= as_of_date),
    CHECK(closed_date IS NULL OR closed_date = stage_changed_date)
);
CREATE INDEX ix_fact_closed_date ON fact_opportunity(closed_date);
CREATE INDEX ix_fact_partner ON fact_opportunity(partner_id);
CREATE INDEX ix_fact_vendor ON fact_opportunity(vendor_id);
