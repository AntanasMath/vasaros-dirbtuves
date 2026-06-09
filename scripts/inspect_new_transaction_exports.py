#!/usr/bin/env python3
"""Inspect newly received transaction, payout, and SAS score exports.

The script streams large CSV files and writes an EDA note. It does not load the
large payment tables into pandas or memory-heavy dataframes.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/new_transaction_exports_inspection.md")

FILES = {
    "payments": "payment_202606081636.csv",
    "allocations": "payments_credits_202606081635.csv",
    "payouts": "payouts_202606081703.csv",
    "sas_credit": "sas_credits_results_202606081620.csv",
    "sas_customer": "sas_results_202606081620.csv",
}

EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00", "0000-00-00 00:00:00.000"}
ALLOCATION_MONEY_COLUMNS = [
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


def meaningful(value: str | None) -> bool:
    return (value or "") not in EMPTY_VALUES


def to_float(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def date_part(value: str | None) -> str:
    if not meaningful(value):
        return ""
    return (value or "")[:10]


def money(value: float) -> str:
    return f"{value:,.2f}"


def stream_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        yield from csv.DictReader(handle)


def read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return next(csv.reader(handle))


def read_key_set(path: Path, key: str) -> set[str]:
    values = set()
    for row in stream_csv(path):
        value = row.get(key)
        if value:
            values.add(value)
    return values


def summarize_payments(path: Path, credit_ids: set[str], customer_ids: set[str]) -> tuple[dict, dict[str, str], dict[str, float]]:
    stats = {
        "rows": 0,
        "unique_payment_ids": set(),
        "unique_credit_ids": set(),
        "unique_customer_ids": set(),
        "credit_rows_in_export_credits": 0,
        "customer_ids_in_master": 0,
        "amount_sum": 0.0,
        "nonzero_amount_rows": 0,
        "overpayment_sum": 0.0,
        "dates": [],
        "years": Counter(),
        "currency": Counter(),
        "ignored": Counter(),
        "registration": Counter(),
        "for_extension": Counter(),
        "flag_amounts": defaultdict(lambda: defaultdict(float)),
        "bank": Counter(),
        "customer_category_id": Counter(),
    }
    payment_dates: dict[str, str] = {}
    payment_credit_ids: dict[str, str] = {}
    payment_amounts: dict[str, float] = {}

    for row in stream_csv(path):
        stats["rows"] += 1
        payment_id = row.get("id") or ""
        credit_id = row.get("credit_id") or ""
        customer_id = row.get("customer_id") or ""
        amount = to_float(row.get("payment_amount"))
        payment_dates[payment_id] = row.get("payment_created") or ""
        payment_credit_ids[payment_id] = credit_id
        payment_amounts[payment_id] = amount

        if payment_id:
            stats["unique_payment_ids"].add(payment_id)
        if credit_id:
            stats["unique_credit_ids"].add(credit_id)
            if credit_id in credit_ids:
                stats["credit_rows_in_export_credits"] += 1
        if customer_id:
            stats["unique_customer_ids"].add(customer_id)
        stats["amount_sum"] += amount
        if amount != 0:
            stats["nonzero_amount_rows"] += 1
        stats["overpayment_sum"] += to_float(row.get("overpayment_amount"))
        date = date_part(row.get("payment_created"))
        if date:
            stats["dates"].append(date)
            stats["years"][date[:4]] += 1
        for key in ["currency", "ignored", "registration", "for_extension", "bank", "customer_category_id"]:
            stats[key][row.get(key, "")] += 1
        for key in ["ignored", "registration", "for_extension"]:
            stats["flag_amounts"][key][row.get(key, "")] += amount

    stats["customer_ids_in_master"] = len(stats["unique_customer_ids"] & customer_ids)
    return stats, payment_dates, payment_amounts | {"__credit_map_size__": float(len(payment_credit_ids))}, payment_credit_ids


def summarize_allocations(
    path: Path,
    credit_ids: set[str],
    customer_ids: set[str],
    payment_ids: set[str],
    payment_dates: dict[str, str],
    payment_credit_ids: dict[str, str],
) -> dict:
    stats = {
        "rows": 0,
        "unique_ids": set(),
        "blank_ids": 0,
        "unique_payment_ids": set(),
        "unique_credit_ids": set(),
        "unique_customer_ids": set(),
        "rows_payment_id_in_payment_table": 0,
        "rows_credit_id_in_export_credits": 0,
        "currency": Counter(),
        "money_sums": defaultdict(float),
        "nonzero_money_columns": Counter(),
        "issued_rows": 0,
        "issued_credit_ids": set(),
        "issued_payment_ids": set(),
        "issued_money_sums": defaultdict(float),
        "issued_total": 0.0,
        "issued_dates": [],
        "issued_years": Counter(),
        "issued_payment_credit_match": 0,
        "issued_payment_credit_mismatch": 0,
    }
    seen_ids = Counter()

    for row in stream_csv(path):
        stats["rows"] += 1
        allocation_id = row.get("id") or ""
        payment_id = row.get("payment_id") or ""
        credit_id = row.get("credit_id") or ""
        customer_id = row.get("customer_id") or ""

        if allocation_id:
            stats["unique_ids"].add(allocation_id)
            seen_ids[allocation_id] += 1
        else:
            stats["blank_ids"] += 1
        if payment_id:
            stats["unique_payment_ids"].add(payment_id)
            if payment_id in payment_ids:
                stats["rows_payment_id_in_payment_table"] += 1
        if credit_id:
            stats["unique_credit_ids"].add(credit_id)
            if credit_id in credit_ids:
                stats["rows_credit_id_in_export_credits"] += 1
        if customer_id:
            stats["unique_customer_ids"].add(customer_id)
        stats["currency"][row.get("currency", "")] += 1

        row_total = 0.0
        for column in ALLOCATION_MONEY_COLUMNS:
            value = to_float(row.get(column))
            stats["money_sums"][column] += value
            row_total += value
            if value != 0:
                stats["nonzero_money_columns"][column] += 1

        if credit_id in credit_ids:
            stats["issued_rows"] += 1
            stats["issued_credit_ids"].add(credit_id)
            stats["issued_payment_ids"].add(payment_id)
            stats["issued_total"] += row_total
            for column in ALLOCATION_MONEY_COLUMNS:
                stats["issued_money_sums"][column] += to_float(row.get(column))
            pay_date = date_part(payment_dates.get(payment_id))
            if pay_date:
                stats["issued_dates"].append(pay_date)
                stats["issued_years"][pay_date[:4]] += 1
            payment_credit_id = payment_credit_ids.get(payment_id, "")
            if payment_credit_id == credit_id:
                stats["issued_payment_credit_match"] += 1
            elif payment_credit_id:
                stats["issued_payment_credit_mismatch"] += 1

    stats["duplicate_nonblank_ids"] = sum(count - 1 for count in seen_ids.values() if count > 1)
    stats["customer_ids_in_master"] = len(stats["unique_customer_ids"] & customer_ids)
    return stats


def summarize_payouts(path: Path, credit_ids: set[str], customer_ids: set[str]) -> dict:
    stats = {
        "rows": 0,
        "unique_ids": set(),
        "unique_credit_ids": set(),
        "unique_customer_ids": set(),
        "credit_rows_in_export_credits": 0,
        "amount_sum": 0.0,
        "dates": [],
        "years": Counter(),
        "status": Counter(),
        "type": Counter(),
        "confirmed_rows": 0,
        "issued_rows": 0,
        "issued_credit_ids": set(),
        "issued_amount_sum": 0.0,
        "issued_dates": [],
        "issued_years": Counter(),
        "issued_status": Counter(),
    }
    for row in stream_csv(path):
        stats["rows"] += 1
        payout_id = row.get("id") or ""
        credit_id = row.get("credit_id") or ""
        customer_id = row.get("customer_id") or ""
        amount = to_float(row.get("amount"))
        if payout_id:
            stats["unique_ids"].add(payout_id)
        if credit_id:
            stats["unique_credit_ids"].add(credit_id)
            if credit_id in credit_ids:
                stats["credit_rows_in_export_credits"] += 1
        if customer_id:
            stats["unique_customer_ids"].add(customer_id)
        stats["amount_sum"] += amount
        date = date_part(row.get("date"))
        if date:
            stats["dates"].append(date)
            stats["years"][date[:4]] += 1
        stats["status"][row.get("payout_status", "")] += 1
        stats["type"][row.get("payout_type", "")] += 1
        if meaningful(row.get("payout_confirmed")):
            stats["confirmed_rows"] += 1
        if credit_id in credit_ids:
            stats["issued_rows"] += 1
            stats["issued_credit_ids"].add(credit_id)
            stats["issued_amount_sum"] += amount
            if date:
                stats["issued_dates"].append(date)
                stats["issued_years"][date[:4]] += 1
            stats["issued_status"][row.get("payout_status", "")] += 1
    stats["customer_ids_in_master"] = len(stats["unique_customer_ids"] & customer_ids)
    return stats


def summarize_sas_credit(path: Path, credit_ids: set[str]) -> dict:
    stats = {
        "rows": 0,
        "unique_credit_ids": set(),
        "matched_rows": 0,
        "matched_credit_ids": set(),
        "dates": [],
        "years": Counter(),
        "score_value": Counter(),
        "scores": [],
    }
    for row in stream_csv(path):
        stats["rows"] += 1
        credit_id = row.get("credit_id") or ""
        if credit_id:
            stats["unique_credit_ids"].add(credit_id)
        if credit_id in credit_ids:
            stats["matched_rows"] += 1
            stats["matched_credit_ids"].add(credit_id)
        date = date_part(row.get("time"))
        if date:
            stats["dates"].append(date)
            stats["years"][date[:4]] += 1
        stats["score_value"][row.get("score_value", "")] += 1
        try:
            stats["scores"].append(float(row.get("score") or 0))
        except ValueError:
            pass
    return stats


def summarize_sas_customer(path: Path, customer_ids: set[str]) -> dict:
    stats = {
        "rows": 0,
        "unique_customer_ids": set(),
        "matched_rows": 0,
        "dates": [],
        "years": Counter(),
        "score_value": Counter(),
        "scores": [],
    }
    for row in stream_csv(path):
        stats["rows"] += 1
        customer_id = row.get("customer_id") or ""
        if customer_id:
            stats["unique_customer_ids"].add(customer_id)
        if customer_id in customer_ids:
            stats["matched_rows"] += 1
        date = date_part(row.get("time"))
        if date:
            stats["dates"].append(date)
            stats["years"][date[:4]] += 1
        stats["score_value"][row.get("scoreValue0", "")] += 1
        try:
            stats["scores"].append(float(row.get("score0") or 0))
        except ValueError:
            pass
    return stats


def minmax(values: list[str]) -> str:
    return f"{min(values)} to {max(values)}" if values else "-"


def counter_top(counter: Counter, n: int = 8) -> str:
    if not counter:
        return "-"
    return ", ".join(f"{key or '(blank)'}: {value:,}" for key, value in counter.most_common(n))


def amount_by_flag(flag_amounts: dict[str, dict[str, float]], key: str) -> str:
    items = sorted(flag_amounts.get(key, {}).items(), key=lambda item: item[0])
    return ", ".join(f"{value_key or '(blank)'}: {money(value)}" for value_key, value in items) if items else "-"


def score_summary(scores: list[float]) -> str:
    if not scores:
        return "-"
    ordered = sorted(scores)
    n = len(ordered)
    return f"min {ordered[0]:.0f}, median {ordered[n // 2]:.0f}, max {ordered[-1]:.0f}"


def nonzero_money(money_sums: dict[str, float], unit: str = "currency units") -> str:
    parts = [f"`{key}` {unit} {money(value)}" for key, value in money_sums.items() if abs(value) > 0.005]
    return "; ".join(parts) if parts else "-"


def inspect(data_dir: Path) -> dict:
    headers = {key: read_header(data_dir / filename) for key, filename in FILES.items()}
    credit_ids = read_key_set(data_dir / "export_credits.csv", "id")
    customer_ids = read_key_set(data_dir / "export_customers.csv", "customer_id")
    paid_credit_ids = set()
    for row in stream_csv(data_dir / "export_credits.csv"):
        if meaningful(row.get("paid")):
            paid_credit_ids.add(row["id"])

    payments, payment_dates, _, payment_credit_ids = summarize_payments(data_dir / FILES["payments"], credit_ids, customer_ids)
    allocations = summarize_allocations(
        data_dir / FILES["allocations"],
        credit_ids,
        customer_ids,
        payments["unique_payment_ids"],
        payment_dates,
        payment_credit_ids,
    )
    payouts = summarize_payouts(data_dir / FILES["payouts"], credit_ids, customer_ids)
    sas_credit = summarize_sas_credit(data_dir / FILES["sas_credit"], credit_ids)
    sas_customer = summarize_sas_customer(data_dir / FILES["sas_customer"], customer_ids)

    return {
        "headers": headers,
        "credit_ids": credit_ids,
        "customer_ids": customer_ids,
        "paid_credit_ids": paid_credit_ids,
        "payments": payments,
        "allocations": allocations,
        "payouts": payouts,
        "sas_credit": sas_credit,
        "sas_customer": sas_customer,
    }


def write_markdown(result: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    credit_ids = result["credit_ids"]
    paid_credit_ids = result["paid_credit_ids"]
    payments = result["payments"]
    allocations = result["allocations"]
    payouts = result["payouts"]
    sas_credit = result["sas_credit"]
    sas_customer = result["sas_customer"]

    allocation_total = sum(allocations["money_sums"].values())
    issued_paid_with_alloc = len(paid_credit_ids & allocations["issued_credit_ids"])
    ongoing_with_alloc = len((credit_ids - paid_credit_ids) & allocations["issued_credit_ids"])

    lines = [
        "# New Transaction Export Inspection",
        "",
        "## Main Conclusion",
        "",
        "The new files do contain actual cash-flow information. The strongest repayment-history source is the pair `payment_202606081636.csv` and `payments_credits_202606081635.csv`: the first table records incoming payment events and timestamps, while the second table allocates each payment to a credit and splits the paid amount into principal, interest, administrative fee, late fee, penalty, and related components.",
        "",
        "For loan-level repayment panel construction, use `payment.id = payments_credits.payment_id` and then use `payments_credits.credit_id = export_credits.id`. The payment date should come from `payment.payment_created`; the component amounts should come from `payments_credits_*` columns.",
        "",
        "`payouts_202606081703.csv` appears to record outgoing disbursement/payout events. The two `sas_*` files record SAS risk scoring results at the credit and customer levels.",
        "",
        "These files cover a broader historical universe than the 21,042 issued loans currently in `export_credits.csv`, so all analysis should explicitly filter to the research credit-id universe when needed.",
        "",
        "## File Inventory",
        "",
        "| File | Rows | Columns | Likely role |",
        "|---|---:|---:|---|",
        f"| `{FILES['payments']}` | {payments['rows']:,} | {len(result['headers']['payments']):,} | Incoming payment events / receipts |",
        f"| `{FILES['allocations']}` | {allocations['rows']:,} | {len(result['headers']['allocations']):,} | Payment-to-credit allocation and component split |",
        f"| `{FILES['payouts']}` | {payouts['rows']:,} | {len(result['headers']['payouts']):,} | Outgoing disbursement / payout events |",
        f"| `{FILES['sas_credit']}` | {sas_credit['rows']:,} | {len(result['headers']['sas_credit']):,} | Credit-level SAS scoring result |",
        f"| `{FILES['sas_customer']}` | {sas_customer['rows']:,} | {len(result['headers']['sas_customer']):,} | Customer-level SAS scoring result |",
        "",
        "## Payment Events",
        "",
        f"- Unique payment IDs: {len(payments['unique_payment_ids']):,}",
        f"- Date range: {minmax(payments['dates'])}",
        f"- Total `payment_amount`: {money(payments['amount_sum'])} in reported currency units",
        f"- Non-zero payment rows: {payments['nonzero_amount_rows']:,}",
        f"- Unique payment credit IDs: {len(payments['unique_credit_ids']):,}",
        f"- Payment rows whose `credit_id` is in current `export_credits.id`: {payments['credit_rows_in_export_credits']:,}",
        f"- Unique payment customers: {len(payments['unique_customer_ids']):,}; in current customer master: {payments['customer_ids_in_master']:,}",
        f"- Currency distribution: {counter_top(payments['currency'])}",
        f"- Ignored flag distribution: {counter_top(payments['ignored'])}",
        f"- Ignored flag amount split: {amount_by_flag(payments['flag_amounts'], 'ignored')}",
        f"- Registration flag distribution: {counter_top(payments['registration'])}",
        f"- Registration flag amount split: {amount_by_flag(payments['flag_amounts'], 'registration')}",
        f"- Extension flag distribution: {counter_top(payments['for_extension'])}",
        f"- Extension flag amount split: {amount_by_flag(payments['flag_amounts'], 'for_extension')}",
        f"- Years: {counter_top(payments['years'], 20)}",
        "",
        "## Payment-Credit Allocations",
        "",
        f"- Allocation rows: {allocations['rows']:,}",
        f"- Unique allocation IDs: {len(allocations['unique_ids']):,}; duplicate non-empty ID rows: {allocations['duplicate_nonblank_ids']:,}",
        f"- Unique `payment_id`: {len(allocations['unique_payment_ids']):,}",
        f"- Allocation rows with `payment_id` found in payment table: {allocations['rows_payment_id_in_payment_table']:,}",
        f"- Unique allocation credit IDs: {len(allocations['unique_credit_ids']):,}",
        f"- Allocation rows whose `credit_id` is in current `export_credits.id`: {allocations['rows_credit_id_in_export_credits']:,}",
        f"- Total allocated components across all records: {money(allocation_total)} in reported currency units",
        f"- Component sums across all records: {nonzero_money(allocations['money_sums'])}",
        f"- Currency distribution: {counter_top(allocations['currency'])}",
        "",
        "### Coverage of the 21,042 Issued-Loan Research Scope",
        "",
        f"- Issued loans in `export_credits.csv`: {len(credit_ids):,}",
        f"- Issued loans with at least one allocation row: {len(allocations['issued_credit_ids']):,}",
        f"- Issued loans without allocation rows: {len(credit_ids - allocations['issued_credit_ids']):,}",
        f"- Completed loans in `export_credits.csv` with allocation rows: {issued_paid_with_alloc:,} of {len(paid_credit_ids):,}",
        f"- Ongoing/unpaid loans with allocation rows: {ongoing_with_alloc:,}",
        f"- Issued-scope allocation rows: {allocations['issued_rows']:,}",
        f"- Issued-scope allocation date range: {minmax(allocations['issued_dates'])}",
        f"- Issued-scope allocated total: EUR {money(allocations['issued_total'])}",
        f"- Issued-scope component sums: {nonzero_money(allocations['issued_money_sums'], 'EUR')}",
        f"- For issued-scope rows, payment-table `credit_id` matched allocation `credit_id` in {allocations['issued_payment_credit_match']:,} rows and differed in {allocations['issued_payment_credit_mismatch']:,} rows.",
        f"- Issued-scope payment years: {counter_top(allocations['issued_years'], 20)}",
        "",
        "## Payouts",
        "",
        f"- Payout rows: {payouts['rows']:,}",
        f"- Date range: {minmax(payouts['dates'])}",
        f"- Total payout `amount`: {money(payouts['amount_sum'])} in reported currency units",
        f"- Unique payout credit IDs: {len(payouts['unique_credit_ids']):,}",
        f"- Payout rows whose `credit_id` is in current `export_credits.id`: {payouts['credit_rows_in_export_credits']:,}",
        f"- Payout status distribution: {counter_top(payouts['status'])}",
        f"- Payout type distribution: {counter_top(payouts['type'])}",
        f"- Confirmed payout rows: {payouts['confirmed_rows']:,}",
        f"- Issued-scope payout rows: {payouts['issued_rows']:,}",
        f"- Issued loans with payout rows: {len(payouts['issued_credit_ids']):,}",
        f"- Issued-scope payout amount: EUR {money(payouts['issued_amount_sum'])}",
        f"- Issued-scope payout date range: {minmax(payouts['issued_dates'])}",
        "",
        "## SAS Scoring Files",
        "",
        "### Credit-Level SAS Results",
        "",
        f"- Rows: {sas_credit['rows']:,}",
        f"- Unique credit IDs: {len(sas_credit['unique_credit_ids']):,}",
        f"- Rows matched to current `export_credits.id`: {sas_credit['matched_rows']:,}",
        f"- Matched issued credit IDs: {len(sas_credit['matched_credit_ids']):,}",
        f"- Time range: {minmax(sas_credit['dates'])}",
        f"- Score value distribution: {counter_top(sas_credit['score_value'])}",
        f"- Score summary: {score_summary(sas_credit['scores'])}",
        "",
        "### Customer-Level SAS Results",
        "",
        f"- Rows: {sas_customer['rows']:,}",
        f"- Unique customer IDs: {len(sas_customer['unique_customer_ids']):,}",
        f"- Rows matched to current `export_customers.customer_id`: {sas_customer['matched_rows']:,}",
        f"- Time range: {minmax(sas_customer['dates'])}",
        f"- Score value distribution: {counter_top(sas_customer['score_value'])}",
        f"- Score summary: {score_summary(sas_customer['scores'])}",
        "",
        "## Practical Use",
        "",
        "For actual repayment analysis, build a transaction panel from `payments_credits_202606081635.csv` joined to `payment_202606081636.csv`. This can support monthly repayment curves, realized cash collections, paid principal/interest/fees, delinquency-recovery timing, and realized revenue analysis for the current 21,042-loan scope after filtering on `payments_credits.credit_id`.",
        "",
        "For disbursement/cash-out analysis, use `payouts_202606081703.csv`, but validate why it covers fewer current issued credits than the payment allocation table before using it as the sole source of original principal disbursement.",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = inspect(args.data_dir)
    write_markdown(result, args.output)
    allocations = result["allocations"]
    print(f"Payment rows: {result['payments']['rows']:,}")
    print(f"Allocation rows: {allocations['rows']:,}")
    print(f"Issued loans with payment allocations: {len(allocations['issued_credit_ids']):,} of {len(result['credit_ids']):,}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
