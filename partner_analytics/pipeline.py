"""Build a validated warehouse and a versioned Power BI CSV export."""

import argparse
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from collections import Counter
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

from .generate import AS_OF, START
from .quality import FIELDS, clean_opportunities, read_source, validate_dimension

ROOT = Path(__file__).resolve().parents[1]


def dump_csv(path, rows, fieldnames):
    # 📖 READ ONLY — always write headers, including for an empty quarantine.
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def insert_records(connection, table, rows):
    # 📖 READ ONLY — table names are internal constants; source values are parameterized.
    keys = list(rows[0])
    placeholders = ",".join("?" for _ in keys)
    connection.executemany(
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
        [[row[key] for key in keys] for row in rows])


def run_pipeline(raw_dir, output_dir):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    partners = read_source(raw_dir / "partners.csv", ["partner_id", "partner_name", "region", "tier"])
    vendors = read_source(raw_dir / "vendors.csv", ["vendor_id", "vendor_name", "category"])
    raw = read_source(raw_dir / "opportunities.csv", FIELDS)
    validate_dimension(partners, "partner_id")
    validate_dimension(vendors, "vendor_id")
    accepted, rejected, audit = clean_opportunities(
        raw, set(partners.partner_id), set(vendors.vendor_id), AS_OF)
    day = START
    dates = []
    while day <= AS_OF:
        dates.append({"date_key": str(day), "year": day.year, "month_number": day.month,
                      "month_start": str(day.replace(day=1)), "month_label": day.strftime("%Y-%m")})
        day += timedelta(days=1)

    # 🎯 INTERVIEW FOCUS — publish immutable versions; a failed build must not replace a good dataset.
    output_dir.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix=".building-", dir=output_dir))
    try:
        with closing(sqlite3.connect(build / "warehouse.sqlite")) as connection:
            connection.row_factory = sqlite3.Row
            connection.executescript((ROOT / "sql/01_schema.sql").read_text(encoding="utf-8"))
            insert_records(connection, "dim_partner", partners.to_dict("records"))
            insert_records(connection, "dim_vendor", vendors.to_dict("records"))
            insert_records(connection, "dim_date", dates)
            insert_records(connection, "fact_opportunity", accepted)
            connection.executescript((ROOT / "sql/02_metrics.sql").read_text(encoding="utf-8"))
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("Warehouse referential integrity failed")
            checks = json.loads(json.dumps(dict(connection.execute("SELECT * FROM v_kpis").fetchone())))
            for table, order in [
                ("dim_partner", "partner_id"), ("dim_vendor", "vendor_id"),
                ("dim_date", "date_key"), ("fact_opportunity", "opportunity_id"),
                ("v_kpis", "accepted_opportunities"),
                ("v_vendor_month", "vendor_id,month_start"),
                ("v_partner_review", "partner_id"),
            ]:
                cursor = connection.execute(f"SELECT * FROM {table} ORDER BY {order}")
                dump_csv(build / f"{table}.csv",
                         [dict(row) for row in cursor], [column[0] for column in cursor.description])
            connection.commit()
        dump_csv(build / "quarantine.csv", rejected, FIELDS + ["rejection_reasons"])
        audit.update({
            "synthetic": True, "as_of_date": str(AS_OF),
            "reason_counts": dict(sorted(Counter(
                reason for row in rejected for reason in row["rejection_reasons"].split("|")).items())),
            "sql_kpis": checks,
        })
        (build / "quality_report.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
        # 🎯 INTERVIEW FOCUS — fingerprint the inputs, implementation and dependency version.
        import pandas as pd
        source_paths = sorted(raw_dir.glob("*.csv"))
        code_paths = sorted((ROOT / "partner_analytics").glob("*.py")) + sorted((ROOT / "sql").glob("*.sql"))
        hashes = {f"source/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
        hashes.update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths})
        identity = json.dumps({"hashes": hashes, "pandas": pd.__version__,
                               "sqlite": sqlite3.sqlite_version}, sort_keys=True)
        version = hashlib.sha256(identity.encode()).hexdigest()[:16]
        manifest = {"dataset_id": version, "synthetic": True, "as_of_date": str(AS_OF),
                    "pandas_version": pd.__version__, "sqlite_version": sqlite3.sqlite_version,
                    "input_and_code_sha256": hashes}
        (build / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        version_dir = output_dir / "versions" / version
        version_dir.parent.mkdir(exist_ok=True)
        if version_dir.exists():
            shutil.rmtree(build)  # identical code/inputs reuse the immutable version
        else:
            os.replace(build, version_dir)
        # 📖 READ ONLY — a one-file atomic pointer tells readers which complete version to use.
        pointer = output_dir / "CURRENT.tmp"
        pointer.write_text(str(version_dir.resolve()) + "\n", encoding="utf-8")
        os.replace(pointer, output_dir / "CURRENT.txt")
        return audit, version_dir
    finally:
        if build.exists():
            shutil.rmtree(build)


def main():
    # 📖 READ ONLY — command-line entry point.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    audit, version_dir = run_pipeline(args.raw_dir, args.output_dir)
    print(json.dumps(audit, indent=2))
    print(f"\nPower BI DataFolder (copy this path): {version_dir.resolve()}")


if __name__ == "__main__":
    main()
