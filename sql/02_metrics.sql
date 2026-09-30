-- bookings are Won value, not all pipeline and not recognized revenue.
CREATE VIEW v_kpis AS
SELECT
    COUNT(*) AS accepted_opportunities,
    SUM(CASE WHEN stage = 'Won' THEN amount_cents ELSE 0 END) / 100.0 AS net_bookings_usd,
    SUM(CASE WHEN stage = 'Won' THEN amount_cents-cost_cents ELSE 0 END) / 100.0 AS booked_gross_profit_usd,
    SUM(CASE WHEN stage = 'Won' THEN amount_cents-cost_cents ELSE 0 END) * 1.0 /
        NULLIF(SUM(CASE WHEN stage = 'Won' THEN amount_cents ELSE 0 END), 0) AS booked_margin_rate,
    SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) AS won_count,
    SUM(CASE WHEN stage IN ('Won','Lost') THEN 1 ELSE 0 END) AS closed_count,
    SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) * 1.0 /
        NULLIF(SUM(CASE WHEN stage IN ('Won','Lost') THEN 1 ELSE 0 END), 0) AS closed_win_rate,
    SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN amount_cents ELSE 0 END) / 100.0 AS open_pipeline_usd,
    SUM(CASE WHEN stage NOT IN ('Won','Lost')
         AND julianday(as_of_date)-julianday(stage_changed_date)>60
         THEN amount_cents ELSE 0 END) / 100.0 AS stale_pipeline_usd,
    SUM(CASE WHEN stage NOT IN ('Won','Lost')
         AND julianday(as_of_date)-julianday(stage_changed_date)>60
         THEN amount_cents ELSE 0 END) * 1.0 /
        NULLIF(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN amount_cents ELSE 0 END), 0)
        AS stale_pipeline_share
FROM fact_opportunity;

-- a dense month/vendor grid prevents LAG from skipping a zero-sales month.
CREATE VIEW v_vendor_month AS
WITH months AS (
    SELECT DISTINCT month_start FROM dim_date
), grid AS (
    SELECT v.vendor_id, v.vendor_name, m.month_start FROM dim_vendor v CROSS JOIN months m
), closed AS (
    SELECT vendor_id, substr(closed_date,1,7)||'-01' AS month_start,
        SUM(CASE WHEN stage='Won' THEN amount_cents ELSE 0 END) AS bookings_cents,
        SUM(CASE WHEN stage='Won' THEN 1 ELSE 0 END) AS won_count,
        COUNT(*) AS closed_count
    FROM fact_opportunity WHERE stage IN ('Won','Lost')
    GROUP BY vendor_id, substr(closed_date,1,7)
), totals AS (
    SELECT g.*, COALESCE(c.bookings_cents,0)/100.0 AS net_bookings_usd,
        COALESCE(c.won_count,0) AS won_count, COALESCE(c.closed_count,0) AS closed_count
    FROM grid g LEFT JOIN closed c
        ON g.vendor_id=c.vendor_id AND g.month_start=c.month_start
), lagged AS (
    SELECT *, LAG(net_bookings_usd) OVER (
        PARTITION BY vendor_id ORDER BY month_start) AS previous_month_bookings_usd
    FROM totals
)
SELECT *, won_count*1.0/NULLIF(closed_count,0) AS closed_win_rate,
    net_bookings_usd-previous_month_bookings_usd AS bookings_change_usd,
    (net_bookings_usd-previous_month_bookings_usd)/
        NULLIF(previous_month_bookings_usd,0) AS bookings_change_rate
FROM lagged;

-- preserve partners without activity and display the conversion denominator.
CREATE VIEW v_partner_review AS
WITH rollup AS (
    SELECT p.partner_id, p.partner_name, p.region, p.tier,
        SUM(CASE WHEN f.stage='Won'
             AND f.closed_date >= date(f.as_of_date,'-89 days') THEN 1 ELSE 0 END) AS won_90d,
        SUM(CASE WHEN f.stage IN ('Won','Lost')
             AND f.closed_date >= date(f.as_of_date,'-89 days') THEN 1 ELSE 0 END) AS closed_90d,
        SUM(CASE WHEN f.stage NOT IN ('Won','Lost') THEN f.amount_cents ELSE 0 END)/100.0
             AS open_pipeline_usd,
        SUM(CASE WHEN f.stage NOT IN ('Won','Lost')
             AND julianday(f.as_of_date)-julianday(f.stage_changed_date)>60
             THEN f.amount_cents ELSE 0 END)/100.0 AS stale_pipeline_usd
    FROM dim_partner p LEFT JOIN fact_opportunity f ON p.partner_id=f.partner_id
    GROUP BY p.partner_id,p.partner_name,p.region,p.tier
)
SELECT *, won_90d*1.0/NULLIF(closed_90d,0) AS win_rate_90d,
    DENSE_RANK() OVER (ORDER BY stale_pipeline_usd DESC) AS stale_value_rank,
    CASE WHEN closed_90d<5 THEN 'Low closed-deal count: avoid conversion ranking'
         ELSE 'Review conversion alongside deal mix' END AS conversion_note
FROM rollup;
