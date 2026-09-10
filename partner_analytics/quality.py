"""Source contracts, deterministic revision handling and explicit quarantine."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd

FIELDS = ["opportunity_id", "partner_id", "vendor_id", "created_date",
          "updated_date", "stage_changed_date", "closed_date", "stage",
          "amount_usd", "cost_usd"]
STAGES = {"Qualified", "Proposal", "Negotiation", "Won", "Lost"}


class DataContractError(ValueError):
    """A critical defect prevents publishing an unambiguous dataset."""


def iso_date(value):
    # 🎯 INTERVIEW FOCUS — reject ambiguous locale formats before dates enter SQL.
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Expected YYYY-MM-DD")
    return date.fromisoformat(value)


def cents(value):
    # 🎯 INTERVIEW FOCUS — exact decimal parsing prevents binary-float money drift.
    try:
        number = Decimal(value)
        scaled = number * 100
        if not number.is_finite() or scaled != scaled.to_integral_value():
            raise ValueError("Money must be finite with at most two decimal places")
        if scaled < 0 or scaled > 1_000_000_000_000:
            raise ValueError("Money outside the declared demo range")
        return int(scaled)
    except (InvalidOperation, OverflowError) as exc:
        raise ValueError("Invalid money") from exc


def read_source(path, required):
    # 📖 READ ONLY — keep IDs as text and empty values visible for validation.
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if set(frame.columns) != set(required):
        raise DataContractError(f"{path.name}: unexpected columns")
    return frame[required].apply(lambda column: column.str.strip())


def validate_dimension(frame, key):
    # 🎯 INTERVIEW FOCUS — duplicate dimension keys would multiply fact-table joins.
    if frame.empty or frame.eq("").any().any() or frame[key].duplicated().any():
        raise DataContractError(f"Invalid reference table: {key}")


def clean_opportunities(raw, partner_ids, vendor_ids, as_of):
    if raw.empty:
        raise DataContractError("Opportunity export is empty")
    # 🎯 INTERVIEW FOCUS — identity and revision order must be trustworthy before deduplication.
    if raw["opportunity_id"].eq("").any():
        raise DataContractError("Missing opportunity identity")
    for value in raw["updated_date"]:
        try:
            if iso_date(value) > as_of:
                raise ValueError("Future revision")
        except ValueError as exc:
            raise DataContractError("Invalid updated_date; cannot safely order revisions") from exc

    unique = raw.drop_duplicates()
    maximum = unique.groupby("opportunity_id")["updated_date"].transform("max")
    latest = unique.loc[unique["updated_date"].eq(maximum)].copy()
    if latest["opportunity_id"].duplicated().any():
        raise DataContractError("Conflicting records at the latest update date")
    latest = latest.sort_values("opportunity_id")
    accepted, rejected = [], []
    for row in latest.to_dict("records"):
        reasons, parsed = [], {}
        if row["partner_id"] not in partner_ids:
            reasons.append("unknown_partner")
        if row["vendor_id"] not in vendor_ids:
            reasons.append("unknown_vendor")
        if row["stage"] not in STAGES:
            reasons.append("unknown_stage")
        for field in ["created_date", "stage_changed_date", "closed_date"]:
            if field == "closed_date" and not row[field]:
                parsed[field] = None
                continue
            try:
                parsed[field] = iso_date(row[field])
            except ValueError:
                parsed[field] = None
                reasons.append(f"invalid_{field}")
        created, changed, closed = (parsed[name] for name in
                                    ["created_date", "stage_changed_date", "closed_date"])
        updated = iso_date(row["updated_date"])
        if created and (created < date(2025, 1, 1) or created > updated):
            reasons.append("creation_outside_contract")
        if changed and (changed > updated or (created and changed < created)):
            reasons.append("stage_date_outside_lifecycle")
        if row["stage"] in {"Won", "Lost"}:
            if not closed:
                reasons.append("closed_stage_requires_date")
            elif closed > updated or (created and closed < created) or closed != changed:
                reasons.append("close_date_outside_lifecycle")
        elif row["closed_date"]:
            reasons.append("open_stage_has_close_date")
        for field in ["amount_usd", "cost_usd"]:
            try:
                parsed[field] = cents(row[field])
            except ValueError:
                reasons.append(f"invalid_{field}")
        if reasons:
            # 🎯 INTERVIEW FOCUS — never revive an older valid revision to hide a bad latest record.
            rejected.append(dict(row, rejection_reasons="|".join(reasons)))
            continue
        accepted.append({
            **{key: row[key] for key in FIELDS if key not in {"amount_usd", "cost_usd"}},
            "closed_date": row["closed_date"] or None,
            "amount_cents": parsed["amount_usd"], "cost_cents": parsed["cost_usd"],
            "as_of_date": str(as_of),
        })
    audit = {
        "raw_rows": len(raw), "exact_duplicates_removed": len(raw) - len(unique),
        "superseded_revisions": len(unique) - len(latest),
        "quarantined_latest": len(rejected), "accepted_latest": len(accepted),
    }
    audit["reconciled"] = audit["raw_rows"] == sum(
        audit[key] for key in ["exact_duplicates_removed", "superseded_revisions",
                              "quarantined_latest", "accepted_latest"])
    if not accepted:
        raise DataContractError("No valid opportunities remain")
    return accepted, rejected, audit
