"""Write deterministic CRM exports with deliberate revisions and data defects."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

AS_OF = date(2026, 8, 31)
START = date(2025, 1, 1)


def write_csv(path, rows):
    # 📖 READ ONLY — newline/encoding choices make CSVs portable to Power BI.
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(raw_dir: Path, seed: int = 42):
    # 🎯 INTERVIEW FOCUS — synthetic evidence demonstrates a workflow, not market truth.
    rng = random.Random(seed)
    raw_dir.mkdir(parents=True, exist_ok=True)
    partners = [
        {"partner_id": f"P{i:03}", "partner_name": f"Demo Partner {i:02}",
         "region": ("Lebanon", "UAE", "KSA", "Qatar")[(i - 1) % 4],
         "tier": ("Standard", "Gold", "Platinum")[(i - 1) % 3]}
        for i in range(1, 49)
    ]
    vendors = [
        {"vendor_id": f"V{i:02}", "vendor_name": name, "category": category}
        for i, (name, category) in enumerate([
            ("Demo Cloud", "Cloud"), ("Demo Shield", "Cybersecurity"),
            ("Demo Storage", "Storage"), ("Demo Connect", "Connectivity")], 1)
    ]
    latest, revisions = [], []
    for i in range(1, 1201):
        created = START + timedelta(days=rng.randrange((AS_OF - START).days - 1))
        changed = created + timedelta(days=rng.randrange((AS_OF - created).days + 1))
        updated = changed + timedelta(days=rng.randrange((AS_OF - changed).days + 1))
        stage = rng.choices(
            ["Won", "Lost", "Qualified", "Proposal", "Negotiation"],
            weights=[36, 24, 18, 14, 8], k=1)[0]
        amount = rng.randrange(100_000, 12_000_000)
        cost = round(amount * rng.uniform(0.65, 1.06))
        row = {
            "opportunity_id": f"O{i:06}", "partner_id": rng.choice(partners)["partner_id"],
            "vendor_id": rng.choice(vendors)["vendor_id"],
            "created_date": str(created), "updated_date": str(updated),
            "stage_changed_date": str(changed),
            "closed_date": str(changed) if stage in {"Won", "Lost"} else "",
            "stage": stage, "amount_usd": f"{amount // 100}.{amount % 100:02}",
            "cost_usd": f"{cost // 100}.{cost % 100:02}",
        }
        latest.append(row)
        if len(revisions) < 120 and updated > created:
            revisions.append(dict(row, updated_date=str(created),
                                  stage_changed_date=str(created),
                                  stage="Qualified", closed_date=""))

    # 🎯 INTERVIEW FOCUS — inject known bad input; these are exercises, not bug discoveries.
    latest[10]["partner_id"] = "P_UNKNOWN"
    latest[11]["amount_usd"] = "-150.00"
    latest[12].update(stage="Won", closed_date="2024-01-01")
    latest[13].update(stage="Proposal", closed_date=latest[13]["stage_changed_date"])
    latest[14]["created_date"] = "not-a-date"
    raw = revisions + latest + [dict(row) for row in latest[100:130]]
    rng.shuffle(raw)
    write_csv(raw_dir / "partners.csv", partners)
    write_csv(raw_dir / "vendors.csv", vendors)
    write_csv(raw_dir / "opportunities.csv", raw)
    return len(raw)


def main():
    # 📖 READ ONLY — CLI wiring, not business logic.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(f"Wrote {generate(args.raw_dir, args.seed)} SYNTHETIC source rows to {args.raw_dir}")


if __name__ == "__main__":
    main()
