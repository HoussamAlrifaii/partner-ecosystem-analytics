"""Independent small examples prove the important business and failure behavior."""

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import pandas as pd

from partner_analytics.generate import AS_OF, generate, write_csv
from partner_analytics.pipeline import run_pipeline
from partner_analytics.quality import DataContractError, FIELDS, cents, clean_opportunities


def deal(identity="A", stage="Won", amount="100.00", cost="60.00",
         changed="2026-08-10", updated="2026-08-15"):
    # a tiny readable fixture; expected results below are calculated independently.
    return {
        "opportunity_id": identity, "partner_id": "P001", "vendor_id": "V01",
        "created_date": "2026-01-01", "updated_date": updated,
        "stage_changed_date": changed, "closed_date": changed if stage in {"Won", "Lost"} else "",
        "stage": stage, "amount_usd": amount, "cost_usd": cost,
    }


def fixture(raw_dir, rows):
    raw_dir.mkdir(exist_ok=True)
    write_csv(raw_dir / "partners.csv", [
        {"partner_id": "P001", "partner_name": "Demo A", "region": "UAE", "tier": "Gold"},
        {"partner_id": "P002", "partner_name": "Demo No Activity", "region": "UAE", "tier": "Gold"}])
    write_csv(raw_dir / "vendors.csv", [
        {"vendor_id": "V01", "vendor_name": "Demo V", "category": "Cloud"}])
    write_csv(raw_dir / "opportunities.csv", rows)


class QualityTests(unittest.TestCase):
    def clean(self, rows):
        return clean_opportunities(pd.DataFrame(rows, columns=FIELDS), {"P001"}, {"V01"}, AS_OF)

    def test_exact_decimal_and_bad_amounts(self):
        # 0.10 USD is exactly 10 cents, with no hidden rounding.
        self.assertEqual(cents("0.10"), 10)
        for value in ["1.001", "-1", "NaN", "Infinity", "", "abc"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                cents(value)

    def test_latest_revision_precedes_validation(self):
        good = deal(updated="2026-08-12")
        bad_latest = deal(amount="-10")
        accepted, rejected, audit = self.clean([good, bad_latest, deal("B")])
        self.assertEqual([x["opportunity_id"] for x in accepted], ["B"])
        self.assertEqual(rejected[0]["opportunity_id"], "A")
        self.assertEqual(audit["superseded_revisions"], 1)

    def test_ambiguous_latest_is_fatal(self):
        with self.assertRaisesRegex(DataContractError, "Conflicting"):
            self.clean([deal(), deal(amount="101")])

    def test_invalid_ordering_is_fatal(self):
        for updated in ["09/01/2026", "2026-09-01"]:
            with self.subTest(updated=updated), self.assertRaises(DataContractError):
                self.clean([deal(updated=updated)])

    def test_exact_duplicate_is_not_an_extra_opportunity(self):
        accepted, _, audit = self.clean([deal(), deal()])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(audit["exact_duplicates_removed"], 1)
        self.assertTrue(audit["reconciled"])

    def test_quarantine_dates_keys_and_negative_cost_but_allow_loss_margin(self):
        cases = [dict(deal("B"), partner_id="MISSING"),
                 dict(deal("C"), stage="Qualified"),
                 dict(deal("D"), closed_date="2025-12-01"),
                 deal("E", cost="-10")]
        accepted, rejected, _ = self.clean([deal(cost="110"), *cases])
        self.assertEqual(len(rejected), 4)
        self.assertEqual(accepted[0]["cost_cents"], 11000)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw, self.output = self.root / "raw", self.root / "outputs"

    def test_known_kpis_rates_and_stage_age(self):
        # expected values are hand calculations, not copies of the SQL.
        fixture(self.raw, [
            deal("W1", amount="100", cost="60"), deal("W2", amount="300", cost="270"),
            deal("L", stage="Lost", amount="500"),
            deal("S", stage="Proposal", amount="200", changed="2026-06-01"),
            deal("F", stage="Qualified", amount="800", changed="2026-08-01"),
        ])
        audit, version = run_pipeline(self.raw, self.output)
        kpi = audit["sql_kpis"]
        self.assertEqual(kpi["net_bookings_usd"], 400)
        self.assertEqual(kpi["booked_gross_profit_usd"], 70)
        self.assertAlmostEqual(kpi["booked_margin_rate"], 0.175)
        self.assertAlmostEqual(kpi["closed_win_rate"], 2 / 3)
        self.assertEqual(kpi["open_pipeline_usd"], 1000)
        self.assertEqual(kpi["stale_pipeline_usd"], 200)
        self.assertEqual(kpi["stale_pipeline_share"], 0.2)
        with closing(sqlite3.connect(version / "warehouse.sqlite")) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM v_vendor_month").fetchone()[0], 20)
            self.assertEqual(connection.execute(
                "SELECT closed_90d FROM v_partner_review WHERE partner_id='P002'").fetchone()[0], 0)

    def test_zero_denominators_are_null(self):
        fixture(self.raw, [deal(stage="Qualified", amount="0")])
        audit, _ = run_pipeline(self.raw, self.output)
        self.assertIsNone(audit["sql_kpis"]["closed_win_rate"])
        self.assertIsNone(audit["sql_kpis"]["booked_margin_rate"])
        self.assertIsNone(audit["sql_kpis"]["stale_pipeline_share"])

    def test_sixty_days_is_not_over_sixty(self):
        fixture(self.raw, [
            deal("A", stage="Qualified", amount="100", changed="2026-07-02"),
            deal("B", stage="Qualified", amount="200", changed="2026-07-01")])
        audit, _ = run_pipeline(self.raw, self.output)
        self.assertEqual(audit["sql_kpis"]["stale_pipeline_usd"], 200)

    def test_zero_month_is_preserved_before_lag(self):
        fixture(self.raw, [deal(changed="2026-01-10", updated="2026-01-10"),
                           deal("B", changed="2026-03-10", updated="2026-03-10")])
        _, version = run_pipeline(self.raw, self.output)
        with closing(sqlite3.connect(version / "warehouse.sqlite")) as connection:
            prior, change_rate = connection.execute(
                "SELECT previous_month_bookings_usd, bookings_change_rate "
                "FROM v_vendor_month WHERE month_start='2026-03-01'").fetchone()
            self.assertEqual(prior, 0)
            self.assertIsNone(change_rate)

    def test_duplicate_dimension_fails_and_preserves_last_good_pointer(self):
        fixture(self.raw, [deal()])
        run_pipeline(self.raw, self.output)
        pointer_before = (self.output / "CURRENT.txt").read_bytes()
        frame = pd.read_csv(self.raw / "partners.csv")
        pd.concat([frame, frame.iloc[[0]]]).to_csv(self.raw / "partners.csv", index=False)
        with self.assertRaisesRegex(DataContractError, "reference"):
            run_pipeline(self.raw, self.output)
        self.assertEqual((self.output / "CURRENT.txt").read_bytes(), pointer_before)

    def test_repeat_build_reuses_version_and_identical_metrics(self):
        fixture(self.raw, [deal()])
        first, path1 = run_pipeline(self.raw, self.output)
        second, path2 = run_pipeline(self.raw, self.output)
        self.assertEqual(path1, path2)
        self.assertEqual(first, second)
        self.assertFalse(list(self.output.glob(".building-*")))
        manifest = json.loads((path1 / "manifest.json").read_text())
        self.assertTrue(manifest["synthetic"])

    def test_demo_source_reconciles_without_join_fanout(self):
        generate(self.raw)
        audit, version = run_pipeline(self.raw, self.output)
        self.assertEqual(
            [audit[k] for k in ["raw_rows", "exact_duplicates_removed",
                               "superseded_revisions", "quarantined_latest", "accepted_latest"]],
            [1350, 30, 120, 5, 1195])
        with closing(sqlite3.connect(version / "warehouse.sqlite")) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM fact_opportunity f "
                "JOIN dim_partner p ON f.partner_id=p.partner_id "
                "JOIN dim_vendor v ON f.vendor_id=v.vendor_id").fetchone()[0]
            self.assertEqual(count, 1195)


if __name__ == "__main__":
    unittest.main()
