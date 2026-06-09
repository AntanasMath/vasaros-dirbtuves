#!/usr/bin/env python3
"""Build a cleaned loan-level dataset for final-outcome prediction.

The output has one row per issued loan. It keeps only terminal loans for
training labels, creates the five mutually exclusive final-outcome labels, and
precomputes 30/60/90-day landmark summary features from repayment, schedule,
and extension-event tables.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("data/modeling/loan_modeling_dataset.csv")
DEFAULT_SUMMARY = Path("docs/loan_modeling_dataset_cleaning.md")
WINDOWS = (30, 60, 90)
AS_OF_DATE = "2026-06-09"

EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00", "0000-00-00 00:00:00.000"}
PAYMENT_COMPONENTS = [
    "amount",
    "charge",
    "administrative_fee",
    "cinterest",
    "interest",
    "insurance",
    "late_fee",
    "penalty",
    "tax1",
    "tax2",
    "tax3",
    "tax4",
    "tax5",
    "tax6",
    "tax7",
    "einsurance",
    "tax8",
    "tax9",
    "tax10",
    "tax11",
    "tax12",
]

CUSTOMER_FEATURES = [
    "age",
    "gender",
    "income",
    "dependents",
    "home_status",
    "work_status",
    "work_activities",
    "region",
    "city",
    "category_id",
    "created",
]

LOAN_FEATURES = [
    "amount",
    "period",
    "charge",
    "administrative_fee",
    "interest",
    "insurance",
    "apr",
    "schedule",
    "product_id",
    "creditline_mode",
    "schedule_type",
]


def meaningful(value: str | None) -> bool:
    return (value or "") not in EMPTY_VALUES


def to_float(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def to_int(value: str | None) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def parse_dt(value: str | None) -> datetime | None:
    if not meaningful(value):
        return None
    text = (value or "").strip().replace("/", "-")
    match = re.match(
        r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2})(?:\.(\d+))?)?)?",
        text,
    )
    if match:
        year, month, day, hour, minute, second, microsecond = match.groups()
        try:
            return datetime(
                int(year),
                int(month),
                int(day),
                int(hour or 0),
                int(minute or 0),
                int(second or 0),
                int((microsecond or "0")[:6].ljust(6, "0")),
            )
        except ValueError:
            return None
    if len(text) >= 19:
        normalized = text[:26].replace(" ", "T")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            pass
        try:
            return datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    if len(text) >= 16:
        try:
            return datetime.strptime(text[:16], "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    if len(text) >= 10:
        try:
            return datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def format_dt(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


def stream_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        yield from csv.DictReader(handle)


@dataclass
class WindowAgg:
    payment_count: int = 0
    payment_total: float = 0.0
    principal_paid: float = 0.0
    interest_paid: float = 0.0
    admin_fee_paid: float = 0.0
    late_fee_paid: float = 0.0
    penalty_paid: float = 0.0
    charge_paid: float = 0.0
    extension_payment_count: int = 0
    extension_payment_total: float = 0.0
    first_payment_day: int | None = None
    last_payment_day: int | None = None
    due_installments: int = 0
    due_total: float = 0.0
    due_principal: float = 0.0
    due_interest: float = 0.0
    due_admin_fee: float = 0.0
    ext_request_count: int = 0
    ext_completed_count: int = 0
    ext_price: float = 0.0
    ext_period_sum: float = 0.0


@dataclass
class LoanRecord:
    credit_id: str
    row: dict[str, str]
    created_dt: datetime | None
    terminal_label: str
    terminal_date: datetime | None
    debt: float
    max_delay: int
    late_fee: float
    windows: dict[int, WindowAgg] = field(default_factory=lambda: {w: WindowAgg() for w in WINDOWS})


def classify_terminal(row: dict[str, str]) -> tuple[str, datetime | None]:
    paid_dt = parse_dt(row.get("paid"))
    sold_dt = parse_dt(row.get("sold"))
    termination_dt = parse_dt(row.get("termination_date"))
    withdraw_dt = parse_dt(row.get("withdraw_date"))
    created_dt = parse_dt(row.get("created"))
    expire_dt = parse_dt(row.get("expire"))

    debt = max(to_float(row.get("debt")), to_float(row.get("s_debt")), to_float(row.get("r_debt")))
    max_delay = to_int(row.get("max_delay"))
    late_fee = to_float(row.get("late_fee"))
    writeoff = max(to_float(row.get("writeoff")), to_float(row.get("writeoff_a")))
    amount = to_float(row.get("amount"))

    if sold_dt:
        return "Sold", sold_dt
    if writeoff > 0:
        return "Written Off", paid_dt or termination_dt or expire_dt
    if paid_dt and debt == 0 and max_delay == 0 and late_fee == 0:
        return "Clean Paid Off", paid_dt
    if paid_dt and debt == 0:
        return "Paid Off After Delinquency", paid_dt
    if paid_dt or termination_dt or withdraw_dt:
        return "Other Terminal / Special Closure", paid_dt or termination_dt or withdraw_dt
    if debt == 0 and amount == 0 and created_dt:
        return "Other Terminal / Special Closure", expire_dt or created_dt
    return "", None


def load_customers(path: Path) -> dict[str, dict[str, str]]:
    customers = {}
    for row in stream_csv(path):
        customer_id = row.get("customer_id")
        if customer_id:
            customers[customer_id] = row
    return customers


def load_loans(path: Path) -> tuple[dict[str, LoanRecord], Counter]:
    loans: dict[str, LoanRecord] = {}
    all_status = Counter()
    for row in stream_csv(path):
        credit_id = row.get("id")
        if not credit_id:
            continue
        label, terminal_date = classify_terminal(row)
        created_dt = parse_dt(row.get("created"))
        debt = max(to_float(row.get("debt")), to_float(row.get("s_debt")), to_float(row.get("r_debt")))
        record = LoanRecord(
            credit_id=credit_id,
            row=row,
            created_dt=created_dt,
            terminal_label=label,
            terminal_date=terminal_date,
            debt=debt,
            max_delay=to_int(row.get("max_delay")),
            late_fee=to_float(row.get("late_fee")),
        )
        all_status[label or "Unfinished / Censored"] += 1
        if label:
            loans[credit_id] = record
    return loans, all_status


def load_payment_meta(path: Path) -> dict[str, dict[str, str | datetime | bool]]:
    payment_meta = {}
    for row in stream_csv(path):
        payment_id = row.get("id")
        if not payment_id:
            continue
        payment_meta[payment_id] = {
            "payment_created": parse_dt(row.get("payment_created")),
            "ignored": row.get("ignored") == "1",
            "registration": row.get("registration") == "1",
            "for_extension": row.get("for_extension") == "1",
            "currency": row.get("currency", ""),
        }
    return payment_meta


def update_payment_windows(loans: dict[str, LoanRecord], allocations_path: Path, payment_meta: dict[str, dict[str, str | datetime | bool]]) -> Counter:
    counts = Counter()
    for row in stream_csv(allocations_path):
        credit_id = row.get("credit_id")
        loan = loans.get(credit_id or "")
        if not loan or not loan.created_dt:
            continue
        payment_id = row.get("payment_id") or ""
        meta = payment_meta.get(payment_id)
        if not meta:
            counts["missing_payment_meta"] += 1
            continue
        if meta.get("ignored") or meta.get("registration"):
            counts["excluded_ignored_or_registration"] += 1
            continue
        payment_dt = meta.get("payment_created")
        if not isinstance(payment_dt, datetime):
            counts["missing_payment_date"] += 1
            continue
        days_since_created = (payment_dt - loan.created_dt).days
        if days_since_created < 0:
            counts["payment_before_created"] += 1
            continue

        principal = to_float(row.get("amount"))
        interest = to_float(row.get("interest")) + to_float(row.get("cinterest"))
        admin_fee = to_float(row.get("administrative_fee"))
        late_fee = to_float(row.get("late_fee"))
        penalty = to_float(row.get("penalty"))
        charge = to_float(row.get("charge"))
        total = sum(to_float(row.get(column)) for column in PAYMENT_COMPONENTS)
        for window in WINDOWS:
            if days_since_created <= window:
                agg = loan.windows[window]
                agg.payment_count += 1
                agg.payment_total += total
                agg.principal_paid += principal
                agg.interest_paid += interest
                agg.admin_fee_paid += admin_fee
                agg.late_fee_paid += late_fee
                agg.penalty_paid += penalty
                agg.charge_paid += charge
                if meta.get("for_extension"):
                    agg.extension_payment_count += 1
                    agg.extension_payment_total += total
                if agg.first_payment_day is None or days_since_created < agg.first_payment_day:
                    agg.first_payment_day = days_since_created
                if agg.last_payment_day is None or days_since_created > agg.last_payment_day:
                    agg.last_payment_day = days_since_created
        counts["used_allocation_rows"] += 1
    return counts


def update_schedule_windows(loans: dict[str, LoanRecord], schedules_path: Path) -> Counter:
    counts = Counter()
    for row in stream_csv(schedules_path):
        credit_id = row.get("credit_id")
        loan = loans.get(credit_id or "")
        if not loan or not loan.created_dt:
            continue
        pay_dt = parse_dt(row.get("pay_date"))
        if not pay_dt:
            counts["missing_pay_date"] += 1
            continue
        days_since_created = (pay_dt - loan.created_dt).days
        if days_since_created < 0:
            counts["schedule_before_created"] += 1
            continue
        principal = to_float(row.get("pay_amount"))
        interest = to_float(row.get("pay_interest"))
        admin_fee = to_float(row.get("pay_administrative_fee"))
        total = to_float(row.get("pay_sum")) or principal + interest + admin_fee
        for window in WINDOWS:
            if days_since_created <= window:
                agg = loan.windows[window]
                agg.due_installments += 1
                agg.due_total += total
                agg.due_principal += principal
                agg.due_interest += interest
                agg.due_admin_fee += admin_fee
        counts["used_schedule_rows"] += 1
    return counts


def update_extension_windows(loans: dict[str, LoanRecord], extensions_path: Path) -> Counter:
    counts = Counter()
    for row in stream_csv(extensions_path):
        credit_id = row.get("credit_id")
        loan = loans.get(credit_id or "")
        if not loan or not loan.created_dt:
            continue
        request_dt = parse_dt(row.get("request_date"))
        if not request_dt:
            counts["missing_request_date"] += 1
            continue
        days_since_created = (request_dt - loan.created_dt).days
        if days_since_created < 0:
            counts["extension_before_created"] += 1
            continue
        completed = meaningful(row.get("complete_date"))
        price = to_float(row.get("price")) or to_float(row.get("o_price"))
        period = to_float(row.get("period"))
        for window in WINDOWS:
            if days_since_created <= window:
                agg = loan.windows[window]
                agg.ext_request_count += 1
                agg.ext_period_sum += period
                if completed:
                    agg.ext_completed_count += 1
                    agg.ext_price += price
        counts["used_extension_rows"] += 1
    return counts


def load_credit_sas(path: Path) -> dict[str, dict[str, str]]:
    scores = {}
    for row in stream_csv(path):
        credit_id = row.get("credit_id")
        if not credit_id:
            continue
        current_time = parse_dt(row.get("time"))
        existing_time = parse_dt(scores.get(credit_id, {}).get("time")) if credit_id in scores else None
        if credit_id not in scores or (current_time and existing_time and current_time > existing_time):
            scores[credit_id] = row
        elif credit_id not in scores:
            scores[credit_id] = row
    return scores


def ratio(numerator: float, denominator: float) -> str:
    if denominator == 0:
        return ""
    return f"{numerator / denominator:.8f}"


def loan_duration_days(record: LoanRecord) -> int | None:
    if not record.created_dt or not record.terminal_date:
        return None
    return (record.terminal_date - record.created_dt).days


def build_row(record: LoanRecord, customer: dict[str, str] | None, credit_sas: dict[str, str] | None) -> dict[str, str]:
    loan = record.row
    created_dt = record.created_dt
    terminal_date = record.terminal_date
    duration = loan_duration_days(record)
    amount = to_float(loan.get("amount"))
    charge = to_float(loan.get("charge"))
    period = to_float(loan.get("period"))

    out: dict[str, str] = {
        "credit_id": record.credit_id,
        "customer_id": loan.get("customer_id", ""),
        "target_final_outcome": record.terminal_label,
        "terminal_date": format_dt(terminal_date),
        "loan_created": format_dt(created_dt),
        "loan_duration_days": "" if duration is None else str(duration),
        "asof_date": AS_OF_DATE,
        "final_debt": f"{record.debt:.2f}",
        "final_max_delay": str(record.max_delay),
        "final_late_fee": f"{record.late_fee:.2f}",
        "loan_created_year": str(created_dt.year) if created_dt else "",
        "loan_created_month": str(created_dt.month) if created_dt else "",
        "contract_charge_rate": ratio(charge, amount),
        "contract_amount_per_day": ratio(amount, period),
        "contract_charge_per_day": ratio(charge, period),
    }

    for column in LOAN_FEATURES:
        out[f"loan_{column}"] = loan.get(column, "")
    if customer:
        for column in CUSTOMER_FEATURES:
            value = customer.get(column, "")
            out[f"customer_{column}"] = value
        customer_created = parse_dt(customer.get("created"))
        if customer_created and created_dt:
            out["customer_age_at_loan_days"] = str((created_dt - customer_created).days)
        else:
            out["customer_age_at_loan_days"] = ""
    else:
        for column in CUSTOMER_FEATURES:
            out[f"customer_{column}"] = ""
        out["customer_age_at_loan_days"] = ""

    if credit_sas:
        out["sas_credit_score"] = credit_sas.get("score", "")
        out["sas_credit_score_value"] = credit_sas.get("score_value", "")
        out["sas_credit_time"] = credit_sas.get("time", "")
    else:
        out["sas_credit_score"] = ""
        out["sas_credit_score_value"] = ""
        out["sas_credit_time"] = ""

    for window in WINDOWS:
        agg = record.windows[window]
        prefix = f"w{window}d"
        eligible = bool(duration is not None and duration > window)
        out[f"eligible_{window}d"] = "1" if eligible else "0"
        out[f"{prefix}_payment_count"] = str(agg.payment_count)
        out[f"{prefix}_payment_total"] = f"{agg.payment_total:.2f}"
        out[f"{prefix}_principal_paid"] = f"{agg.principal_paid:.2f}"
        out[f"{prefix}_interest_paid"] = f"{agg.interest_paid:.2f}"
        out[f"{prefix}_admin_fee_paid"] = f"{agg.admin_fee_paid:.2f}"
        out[f"{prefix}_late_fee_paid"] = f"{agg.late_fee_paid:.2f}"
        out[f"{prefix}_penalty_paid"] = f"{agg.penalty_paid:.2f}"
        out[f"{prefix}_charge_paid"] = f"{agg.charge_paid:.2f}"
        out[f"{prefix}_extension_payment_count"] = str(agg.extension_payment_count)
        out[f"{prefix}_extension_payment_total"] = f"{agg.extension_payment_total:.2f}"
        out[f"{prefix}_days_to_first_payment"] = "" if agg.first_payment_day is None else str(agg.first_payment_day)
        out[f"{prefix}_days_since_last_payment"] = "" if agg.last_payment_day is None else str(window - agg.last_payment_day)
        out[f"{prefix}_due_installments"] = str(agg.due_installments)
        out[f"{prefix}_scheduled_due_total"] = f"{agg.due_total:.2f}"
        out[f"{prefix}_scheduled_due_principal"] = f"{agg.due_principal:.2f}"
        out[f"{prefix}_scheduled_due_interest"] = f"{agg.due_interest:.2f}"
        out[f"{prefix}_scheduled_due_admin_fee"] = f"{agg.due_admin_fee:.2f}"
        out[f"{prefix}_payment_gap"] = f"{agg.due_total - agg.payment_total:.2f}"
        out[f"{prefix}_principal_recovery_rate"] = ratio(agg.principal_paid, amount)
        out[f"{prefix}_total_paid_to_due_ratio"] = ratio(agg.payment_total, agg.due_total)
        out[f"{prefix}_ext_request_count"] = str(agg.ext_request_count)
        out[f"{prefix}_ext_completed_count"] = str(agg.ext_completed_count)
        out[f"{prefix}_ext_price"] = f"{agg.ext_price:.2f}"
        out[f"{prefix}_ext_period_sum"] = f"{agg.ext_period_sum:.2f}"
    return out


def write_dataset(
    loans: dict[str, LoanRecord],
    customers: dict[str, dict[str, str]],
    credit_sas: dict[str, dict[str, str]],
    output_path: Path,
) -> tuple[int, list[str]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for record in loans.values():
        customer = customers.get(record.row.get("customer_id", ""))
        score = credit_sas.get(record.credit_id)
        rows.append(build_row(record, customer, score))

    rows.sort(key=lambda row: (row.get("loan_created", ""), row.get("credit_id", "")))
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), fieldnames


def write_summary(
    summary_path: Path,
    output_path: Path,
    all_status: Counter,
    terminal_loans: dict[str, LoanRecord],
    fieldnames: Iterable[str],
    process_counts: dict[str, Counter],
) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    label_counts = Counter(record.terminal_label for record in terminal_loans.values())
    eligible_counts = {
        window: sum(1 for record in terminal_loans.values() if (loan_duration_days(record) is not None and loan_duration_days(record) > window))
        for window in WINDOWS
    }
    lines = [
        "# Loan Modeling Dataset Cleaning",
        "",
        "## Purpose",
        "",
        "This dataset is prepared for final-outcome prediction at the loan level. Each row is one issued loan, not one borrower. Borrower-level variables may therefore repeat across multiple loan rows.",
        "",
        "## Final Outcome Labels",
        "",
        "The five mutually exclusive terminal labels are assigned in priority order:",
        "",
        "1. `Sold`: `sold` has a valid date.",
        "2. `Written Off`: `writeoff` or `writeoff_a` is positive, excluding loans already labelled as sold.",
        "3. `Clean Paid Off`: `paid` has a valid date, final debt is zero, `max_delay = 0`, and `late_fee = 0`.",
        "4. `Paid Off After Delinquency`: `paid` has a valid date and final debt is zero, but delay or fee signals exist.",
        "5. `Other Terminal / Special Closure`: terminal or special closure signals exist but do not fit the four main labels.",
        "",
        "Unfinished loans are excluded from the training dataset because their final outcome is right-censored.",
        "",
        "## Output",
        "",
        f"- Dataset: `{output_path}`",
        f"- Rows: {len(terminal_loans):,}",
        f"- Columns: {len(list(fieldnames)):,}",
        "",
        "## Full Issued-Loan Status Before Filtering",
        "",
        "| Status | Loans |",
        "|---|---:|",
    ]
    for label, count in all_status.most_common():
        lines.append(f"| {label} | {count:,} |")

    lines.extend(["", "## Label Distribution In Cleaned Dataset", "", "| Final outcome | Loans |", "|---|---:|"])
    for label, count in label_counts.most_common():
        lines.append(f"| {label} | {count:,} |")

    lines.extend(["", "## Landmark Eligibility", "", "A loan is eligible for a landmark model only if its terminal date is later than the landmark day. For example, a 45-day loan is eligible for the 30-day model, but not for the 60-day or 90-day model.", "", "| Landmark | Eligible terminal loans |", "|---|---:|"])
    for window, count in eligible_counts.items():
        lines.append(f"| {window} days | {count:,} |")

    lines.extend(["", "## Window Features", "", "For each of 30/60/90 days, the script computes cumulative repayment, scheduled due, payment-gap, recovery-rate, and extension-event features using only events dated on or before the landmark day.", ""])

    lines.extend(["## Processing Notes", ""])
    for name, counter in process_counts.items():
        lines.append(f"### {name}")
        lines.append("")
        if counter:
            for key, value in counter.most_common():
                lines.append(f"- `{key}`: {value:,}")
        else:
            lines.append("- No notable counts.")
        lines.append("")

    lines.extend(
        [
            "## Leakage Notes",
            "",
            "The cleaning script keeps a conservative set of borrower variables such as age, gender, income, work status, home status, region, and customer registration date. It intentionally does not include customer-master aggregate fields such as `credits_paid`, `last_payment_date`, or `all_paid` as default features because those fields are likely measured at export time and may contain post-outcome information.",
            "",
        ]
    )
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    data_dir = args.data_dir
    customers = load_customers(data_dir / "export_customers.csv")
    terminal_loans, all_status = load_loans(data_dir / "export_credits.csv")
    payment_meta = load_payment_meta(data_dir / "payment_202606081636.csv")
    process_counts = {
        "payment_allocations": update_payment_windows(terminal_loans, data_dir / "payments_credits_202606081635.csv", payment_meta),
        "schedules": update_schedule_windows(terminal_loans, data_dir / "credits_schedules_all.csv"),
        "extensions": update_extension_windows(terminal_loans, data_dir / "export_credit_ext_requests.csv"),
    }
    credit_sas = load_credit_sas(data_dir / "sas_credits_results_202606081620.csv")
    row_count, fieldnames = write_dataset(terminal_loans, customers, credit_sas, args.output)
    write_summary(args.summary, args.output, all_status, terminal_loans, fieldnames, process_counts)

    label_counts = Counter(record.terminal_label for record in terminal_loans.values())
    print(f"Wrote {args.output} with {row_count:,} terminal loan rows and {len(fieldnames):,} columns")
    print("Label counts:")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count:,}")
    for window in WINDOWS:
        eligible = sum(1 for record in terminal_loans.values() if (loan_duration_days(record) is not None and loan_duration_days(record) > window))
        print(f"Eligible {window}d: {eligible:,}")
    print(f"Wrote {args.summary}")


if __name__ == "__main__":
    main()
