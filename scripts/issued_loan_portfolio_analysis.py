#!/usr/bin/env python3
"""Analyze the 21,042 issued loans and write a LaTeX portfolio report."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/issued_loan_portfolio_report.tex")
CURRENT_DATE = date(2026, 6, 8)
EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00"}


STATUS_LABELS = {
    "completed_clean": "Completed clean",
    "completed_with_delay_or_fees": "Completed with delay/fees",
    "active_current_not_due_or_no_delay": "Active current",
    "active_delinquent_current_delay": "Active delinquent",
    "sold_or_written_off": "Sold / written off",
    "other_unpaid_no_debt": "Other unpaid/no debt",
    "unpaid_past_maturity_no_current_delay": "Unpaid past maturity",
    "paid_but_debt_or_flags_remain": "Paid but debt/flags remain",
}


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


def parse_date(value: str | None) -> date | None:
    if not meaningful(value):
        return None
    try:
        return date.fromisoformat((value or "").replace("/", "-")[:10])
    except ValueError:
        return None


def pct(part: int | float, whole: int | float) -> float:
    return 100 * part / whole if whole else 0.0


def money(value: float) -> str:
    return f"{value:,.2f}"


def number(value: int | float) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.2f}"


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("~", "\\textasciitilde{}")
        .replace("^", "\\textasciicircum{}")
    )


def credit_status(row: dict[str, str]) -> str:
    paid = meaningful(row.get("paid"))
    debt = max(to_float(row.get("debt")), to_float(row.get("s_debt")), to_float(row.get("r_debt")))
    current_delay = to_int(row.get("current_delay"))
    max_delay = to_int(row.get("max_delay"))
    late_fee = to_float(row.get("late_fee"))
    sold = meaningful(row.get("sold"))
    writeoff = max(to_float(row.get("writeoff")), to_float(row.get("writeoff_a")))
    expire = parse_date(row.get("expire"))

    if paid and debt == 0:
        if max_delay == 0 and late_fee == 0 and not sold and writeoff == 0:
            return "completed_clean"
        return "completed_with_delay_or_fees"
    if sold or writeoff > 0:
        return "sold_or_written_off"
    if not paid and debt > 0:
        if current_delay > 0:
            return "active_delinquent_current_delay"
        if expire and expire < CURRENT_DATE:
            return "unpaid_past_maturity_no_current_delay"
        return "active_current_not_due_or_no_delay"
    if paid:
        return "paid_but_debt_or_flags_remain"
    return "other_unpaid_no_debt"


def delay_bucket(value: int) -> str:
    if value == 0:
        return "0"
    if value <= 30:
        return "1-30"
    if value <= 60:
        return "31-60"
    if value <= 90:
        return "61-90"
    return "90+"


def read_credits(path: Path) -> dict[str, dict[str, str]]:
    credits = {}
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            credit_id = row.get("id")
            if credit_id:
                row["status"] = credit_status(row)
                credits[credit_id] = row
    return credits


def read_customer_funnel(data_dir: Path) -> dict:
    customer_ids = set()
    rejected_customers = set()
    approved_customers = set()

    with (data_dir / "export_customers.csv").open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            if row.get("customer_id"):
                customer_ids.add(row["customer_id"])

    with (data_dir / "export_credits_rejected.csv").open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            if row.get("customer_id"):
                rejected_customers.add(row["customer_id"])

    with (data_dir / "export_credits.csv").open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            if row.get("customer_id"):
                approved_customers.add(row["customer_id"])

    applicants = rejected_customers | approved_customers
    return {
        "registered_customers": len(customer_ids),
        "applicant_customers": len(applicants),
        "no_application_customers": len(customer_ids - applicants),
        "rejected_customers": len(rejected_customers),
        "approved_customers": len(approved_customers),
        "rejected_only_customers": len(rejected_customers - approved_customers),
        "approved_only_customers": len(approved_customers - rejected_customers),
        "both_rejected_and_approved": len(rejected_customers & approved_customers),
    }


def read_rejected_rows(path: Path) -> int:
    rows = 0
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for _ in csv.DictReader(handle):
            rows += 1
    return rows


def aggregate_extensions(path: Path, credit_ids: set[str]) -> dict[str, dict[str, float | int]]:
    ext = defaultdict(lambda: {"count": 0, "completed_count": 0, "price": 0.0, "completed_price": 0.0})
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            credit_id = row.get("credit_id")
            if credit_id not in credit_ids:
                continue
            price = to_float(row.get("price"))
            ext[credit_id]["count"] += 1
            ext[credit_id]["price"] += price
            if meaningful(row.get("complete_date")):
                ext[credit_id]["completed_count"] += 1
                ext[credit_id]["completed_price"] += price
    return dict(ext)


def aggregate_schedules(path: Path, credit_ids: set[str], credits: dict[str, dict[str, str]]) -> dict:
    by_credit = defaultdict(
        lambda: {
            "rows": 0,
            "principal": 0.0,
            "interest": 0.0,
            "fee": 0.0,
            "sum": 0.0,
            "future_principal": 0.0,
            "future_interest": 0.0,
            "future_fee": 0.0,
            "future_sum": 0.0,
        }
    )
    future_by_month = defaultdict(float)
    rows = 0
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            credit_id = row.get("credit_id")
            if credit_id not in credit_ids:
                continue
            rows += 1
            principal = to_float(row.get("pay_amount"))
            interest = to_float(row.get("pay_interest"))
            fee = to_float(row.get("pay_administrative_fee"))
            total = to_float(row.get("pay_sum"))
            item = by_credit[credit_id]
            item["rows"] += 1
            item["principal"] += principal
            item["interest"] += interest
            item["fee"] += fee
            item["sum"] += total
            pay_date = parse_date(row.get("pay_date"))
            if pay_date and pay_date >= CURRENT_DATE and not meaningful(credits[credit_id].get("paid")):
                item["future_principal"] += principal
                item["future_interest"] += interest
                item["future_fee"] += fee
                item["future_sum"] += total
                future_by_month[pay_date.strftime("%Y-%m")] += total
    return {"by_credit": dict(by_credit), "rows": rows, "future_by_month": dict(future_by_month)}


def summarize(credits: dict[str, dict[str, str]], extensions: dict, schedules: dict) -> dict:
    values_amount = [to_float(row.get("amount")) for row in credits.values()]
    values_period = [to_int(row.get("period")) for row in credits.values()]
    customer_ids = {row.get("customer_id") for row in credits.values() if row.get("customer_id")}
    status_counts = Counter(row["status"] for row in credits.values())
    status_amounts = defaultdict(float)
    year_counts = Counter()
    year_amounts = defaultdict(float)
    max_delay_buckets = Counter()
    current_delay_buckets = Counter()
    revenue = defaultdict(float)
    exposure = defaultdict(float)
    status_exposure = defaultdict(float)
    loans_with_extension = 0

    for credit_id, row in credits.items():
        amount = to_float(row.get("amount"))
        charge = to_float(row.get("charge"))
        late_fee = to_float(row.get("late_fee"))
        administrative_fee = to_float(row.get("administrative_fee"))
        interest = to_float(row.get("interest"))
        insurance = to_float(row.get("insurance"))
        ext_completed = float(extensions.get(credit_id, {}).get("completed_price", 0.0))
        if credit_id in extensions:
            loans_with_extension += 1

        status = row["status"]
        status_amounts[status] += amount
        revenue["charge"] += charge
        revenue["late_fee"] += late_fee
        revenue["administrative_fee"] += administrative_fee
        revenue["interest"] += interest
        revenue["insurance"] += insurance
        revenue["extension_fee"] += ext_completed

        if meaningful(row.get("paid")) and max(to_float(row.get("debt")), to_float(row.get("s_debt")), to_float(row.get("r_debt"))) == 0:
            revenue["completed_revenue_proxy"] += charge + late_fee + ext_completed

        outstanding = max(to_float(row.get("debt")), to_float(row.get("s_debt")), to_float(row.get("r_debt")))
        exposure["outstanding"] += outstanding
        status_exposure[status] += outstanding
        if status in {"active_delinquent_current_delay", "sold_or_written_off", "unpaid_past_maturity_no_current_delay"}:
            exposure["impaired_or_high_risk"] += outstanding
        if status == "active_current_not_due_or_no_delay":
            exposure["active_current"] += outstanding

        year = (row.get("created") or "")[:4]
        if year.isdigit():
            year_counts[year] += 1
            year_amounts[year] += amount

        max_delay_buckets[delay_bucket(to_int(row.get("max_delay")))] += 1
        current_delay_buckets[delay_bucket(to_int(row.get("current_delay")))] += 1

    sched_by_credit = schedules["by_credit"]
    future = defaultdict(float)
    schedule_coverage = 0
    for credit_id, item in sched_by_credit.items():
        if item["rows"] > 0:
            schedule_coverage += 1
        for key in ["future_principal", "future_interest", "future_fee", "future_sum"]:
            future[key] += item[key]

    return {
        "n_loans": len(credits),
        "n_borrowers": len(customer_ids),
        "amount_total": sum(values_amount),
        "amount_mean": statistics.mean(values_amount),
        "amount_median": statistics.median(values_amount),
        "period_mean": statistics.mean(values_period),
        "period_median": statistics.median(values_period),
        "status_counts": status_counts,
        "status_amounts": status_amounts,
        "year_counts": year_counts,
        "year_amounts": year_amounts,
        "max_delay_buckets": max_delay_buckets,
        "current_delay_buckets": current_delay_buckets,
        "revenue": revenue,
        "exposure": exposure,
        "status_exposure": status_exposure,
        "loans_with_extension": loans_with_extension,
        "schedule_coverage": schedule_coverage,
        "future": future,
        "future_by_month": schedules["future_by_month"],
    }


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_bar_chart(path: Path, title: str, labels: list[str], values: list[float], value_suffix: str = "") -> None:
    from PIL import Image, ImageDraw

    width = 1400
    height = 760
    margin_left = 260
    margin_right = 80
    margin_top = 95
    bar_h = 42
    gap = 22
    image = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    title_font = load_font(28, True)
    label_font = load_font(16)
    value_font = load_font(15, True)
    draw.text((40, 35), title, font=title_font, fill="#172033")
    max_value = max(values) if values else 1
    for idx, (label, value) in enumerate(zip(labels, values)):
        y = margin_top + idx * (bar_h + gap)
        draw.text((40, y + 9), label, font=label_font, fill="#253044")
        bar_w = int((width - margin_left - margin_right) * value / max_value)
        draw.rounded_rectangle((margin_left, y, margin_left + bar_w, y + bar_h), radius=6, fill="#4477aa")
        draw.text((margin_left + bar_w + 12, y + 10), f"{value:,.0f}{value_suffix}", font=value_font, fill="#253044")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def draw_line_like_chart(path: Path, title: str, series: dict[str, float], max_points: int = 18) -> None:
    from PIL import Image, ImageDraw

    items = sorted(series.items())[:max_points]
    labels = [item[0] for item in items]
    values = [item[1] for item in items]
    draw_bar_chart(path, title, labels, values)


def write_figures(output_dir: Path, summary: dict) -> dict[str, Path]:
    status_items = summary["status_counts"].most_common()
    status_labels = [STATUS_LABELS.get(key, key) for key, _ in status_items]
    status_values = [value for _, value in status_items]
    status_path = output_dir / "issued_status_distribution.png"
    draw_bar_chart(status_path, "Issued Credit Status Distribution", status_labels, status_values)

    year_items = sorted(summary["year_counts"].items())
    year_path = output_dir / "annual_issued_loans.png"
    draw_bar_chart(year_path, "Issued Loans by Origination Year", [k for k, _ in year_items], [v for _, v in year_items])

    future_path = output_dir / "expected_future_schedule_cashflow.png"
    draw_line_like_chart(future_path, "Expected Future Scheduled Receipts for Ongoing Loans", summary["future_by_month"])
    return {"status": status_path, "year": year_path, "future": future_path}


def table_status(summary: dict) -> str:
    lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Status & Loans & Share & Principal & Outstanding exposure \\\\",
        "\\midrule",
    ]
    n = summary["n_loans"]
    for key, count in summary["status_counts"].most_common():
        lines.append(
            f"{latex_escape(STATUS_LABELS.get(key, key))} & {count:,} & {pct(count, n):.1f}\\% & "
            f"{money(summary['status_amounts'][key])} & {money(summary['status_exposure'][key])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def table_revenue(summary: dict) -> str:
    rev = summary["revenue"]
    rows = [
        ("Contractual charge", rev["charge"]),
        ("Administrative fee component", rev["administrative_fee"]),
        ("Interest component", rev["interest"]),
        ("Insurance component", rev["insurance"]),
        ("Late fee balance", rev["late_fee"]),
        ("Completed extension request fees", rev["extension_fee"]),
        ("Completed-loan gross revenue proxy", rev["completed_revenue_proxy"]),
    ]
    lines = ["\\begin{tabular}{lr}", "\\toprule", "Metric & EUR \\\\", "\\midrule"]
    for name, value in rows:
        lines.append(f"{latex_escape(name)} & {money(value)} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def table_delay(counter: Counter) -> str:
    order = ["0", "1-30", "31-60", "61-90", "90+"]
    total = sum(counter.values())
    lines = ["\\begin{tabular}{lrr}", "\\toprule", "Bucket & Loans & Share \\\\", "\\midrule"]
    for bucket in order:
        count = counter.get(bucket, 0)
        lines.append(f"{bucket} & {count:,} & {pct(count, total):.1f}\\% \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def write_report(output_path: Path, summary: dict, funnel: dict, rejected_rows: int, figures: dict[str, Path]) -> None:
    report_dir = output_path.parent
    relative = {key: path.name for key, path in figures.items()}
    report = rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{float}}
\usepackage{{hyperref}}
\title{{Descriptive Portfolio Analysis of Issued Loans}}
\author{{CO-KTU Workshop Credit Platform Data}}
\date{{Generated on {CURRENT_DATE.isoformat()}}}

\begin{{document}}
\maketitle

\begin{{abstract}}
This report studies the {summary['n_loans']:,} issued loans recorded in \texttt{{export\_credits.csv}}. The goal is descriptive rather than predictive: we summarize the platform's current operating condition, contractual revenue base, available loss and exposure indicators, expected contractual cash flows for unresolved loans, and credit performance. Customer-level application flow is used only to motivate the transition into the issued-loan portfolio; all portfolio analysis after issuance uses loan identifiers.
\end{{abstract}}

\section{{Scope and Unit of Analysis}}
The full data funnel contains {funnel['registered_customers']:,} registered customers, of whom {funnel['applicant_customers']:,} have loan application evidence. A customer may appear in both rejected and approved paths. The approved path contains {funnel['approved_customers']:,} unique customers, consisting of {funnel['approved_only_customers']:,} customers with issued credit and no rejection rows plus {funnel['both_rejected_and_approved']:,} customers with both rejection history and issued credit. These {funnel['approved_customers']:,} customers account for {summary['n_loans']:,} issued loans. The rejected-application table contains {rejected_rows:,} rejected application rows, but rejected loans are outside the main analytical scope of this report.

\begin{{figure}}[H]
\centering
\includegraphics[width=0.95\linewidth]{{portfolio_flowchart.png}}
\caption{{Portfolio funnel. Customer-level counts are used before issuance; credit-id level counts are used after issuance.}}
\end{{figure}}

The unit of analysis is therefore the issued loan:
\[
i \in \{{1,\ldots,N\}}, \quad N = {summary['n_loans']:,}.
\]
Completed loans are identified by a non-empty \texttt{{paid}} field. Ongoing loans are those with an empty \texttt{{paid}} field. Because actual payment transaction records are not available, monetary revenue measures should be interpreted as contractual or proxy measures, not audited cash receipts.

\section{{Definitions and Formulas}}
For loan \(i\), let \(A_i\) denote principal amount, \(C_i\) contractual charge, \(F_i\) late fee balance, and \(X_i\) completed extension request fees. The contractual revenue proxy is
\[
R_i^{{contract}} = C_i + F_i + X_i.
\]
For completed loans with \texttt{{paid}} present and zero remaining debt, the completed-loan gross revenue proxy is
\[
R_i^{{completed}} = C_i + F_i + X_i.
\]
This assumes that loan completion implies collection of scheduled contractual charges. It is an assumption imposed by data limitations, because individual cash payment transactions are not observed.

Remaining exposure is defined as
\[
E_i = \max(\texttt{{debt}}_i, \texttt{{s\_debt}}_i, \texttt{{r\_debt}}_i).
\]
High-risk or impaired exposure is the sum of \(E_i\) over loans classified as currently delinquent, sold/written off, or unpaid past maturity. This is an exposure proxy, not a realized accounting loss.

\section{{Portfolio Overview}}
The issued portfolio contains {summary['n_loans']:,} loans to {summary['n_borrowers']:,} borrowers. Total issued principal is EUR {money(summary['amount_total'])}. The average loan amount is EUR {money(summary['amount_mean'])}, and the median is EUR {money(summary['amount_median'])}. The average contractual period is {summary['period_mean']:.1f} days, with a median of {summary['period_median']:.0f} days.

\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\linewidth]{{{relative['year']}}}
\caption{{Issued loans by origination year.}}
\end{{figure}}

\section{{Revenue Analysis}}
The revenue analysis is based on fields available in the issued-loan table and extension-request table. The main planned revenue field is \texttt{{charge}}, which largely decomposes into interest and administrative fees. Late fees and completed extension request fees are reported separately.

\begin{{table}}[H]
\centering
\caption{{Revenue-related measures. Values are contractual/proxy measures, not audited cash receipts.}}
{table_revenue(summary)}
\end{{table}}

The completed-loan gross revenue proxy is EUR {money(summary['revenue']['completed_revenue_proxy'])}. This measure includes only loans that are marked paid and have zero remaining debt. It excludes unresolved loans because their final cash outcome is not yet observed.

\section{{Cost and Loss Analysis}}
The available data do not include funding cost, acquisition cost, servicing cost, or recovery proceeds from sold debt. Therefore, the analysis focuses on credit exposure and loss proxies rather than full cost accounting. Total remaining exposure, defined by \(E_i\), is EUR {money(summary['exposure']['outstanding'])}. High-risk or impaired exposure is EUR {money(summary['exposure']['impaired_or_high_risk'])}. Active-current exposure is EUR {money(summary['exposure']['active_current'])}.

These figures should be interpreted as portfolio risk indicators. They do not prove realized loss, especially for active delinquent loans that may later cure or be recovered.

\section{{Expected Contractual Cash Flow for Ongoing Loans}}
The schedule table \texttt{{credits\_schedules\_all.csv}} provides planned installment dates and amounts. For unresolved loans, expected future scheduled receipts are computed as:
\[
\text{{FutureScheduled}} = \sum_{{i: \texttt{{paid}}_i=\emptyset}} \sum_{{t \geq {CURRENT_DATE.isoformat()}}} \texttt{{pay\_sum}}_{{i,t}}.
\]
This is a contractual schedule measure. It is not a forecast of actual repayment behavior.

Among issued loans, {summary['schedule_coverage']:,} have schedule rows in the current schedule export. For ongoing loans covered by schedules, future scheduled receipts from {CURRENT_DATE.isoformat()} onward total EUR {money(summary['future']['future_sum'])}, composed of EUR {money(summary['future']['future_principal'])} principal, EUR {money(summary['future']['future_interest'])} interest, and EUR {money(summary['future']['future_fee'])} administrative fee.

\begin{{figure}}[H]
\centering
\includegraphics[width=0.9\linewidth]{{{relative['future']}}}
\caption{{Expected future scheduled receipts for unresolved loans, grouped by planned pay month.}}
\end{{figure}}

\section{{Credit Performance and Risk}}
Credit performance is summarized using status classifications derived from \texttt{{paid}}, remaining debt fields, current and maximum delay, late fees, sold flags, and writeoff fields.

\begin{{table}}[H]
\centering
\caption{{Issued-credit status distribution.}}
{table_status(summary)}
\end{{table}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\linewidth]{{{relative['status']}}}
\caption{{Issued-credit status distribution.}}
\end{{figure}}

Historical delinquency is represented by \texttt{{max\_delay}}, while current delinquency is represented by \texttt{{current\_delay}}.

\begin{{table}}[H]
\centering
\caption{{Historical maximum delay buckets.}}
{table_delay(summary['max_delay_buckets'])}
\end{{table}}

\begin{{table}}[H]
\centering
\caption{{Current delay buckets.}}
{table_delay(summary['current_delay_buckets'])}
\end{{table}}

The portfolio has {summary['status_counts'].get('completed_clean', 0):,} cleanly completed loans and {summary['status_counts'].get('completed_with_delay_or_fees', 0):,} completed loans with delay or fee signals. There are {summary['status_counts'].get('active_delinquent_current_delay', 0):,} currently delinquent active loans and {summary['status_counts'].get('sold_or_written_off', 0):,} sold or written-off loans.

\section{{Conclusion}}
The issued portfolio is large enough for descriptive operating analysis: {summary['n_loans']:,} issued loans, EUR {money(summary['amount_total'])} in principal, and EUR {money(summary['revenue']['charge'])} in contractual charges. The data support portfolio overview, contractual revenue analysis, credit exposure analysis, expected contractual cash-flow analysis for unresolved loans, and credit performance analysis.

However, the available data do not contain actual installment-level payment transactions. Therefore, profitability is evaluated as a contractual and credit-risk proxy. A definitive accounting profit statement would require actual cash collections, funding cost, operating cost, acquisition cost, and recovery proceeds.

\end{{document}}
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze issued loan portfolio and write a LaTeX report.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_dir = args.output.parent
    credits = read_credits(args.data_dir / "export_credits.csv")
    credit_ids = set(credits)
    funnel = read_customer_funnel(args.data_dir)
    rejected_rows = read_rejected_rows(args.data_dir / "export_credits_rejected.csv")
    extensions = aggregate_extensions(args.data_dir / "export_credit_ext_requests.csv", credit_ids)
    schedules = aggregate_schedules(args.data_dir / "credits_schedules_all.csv", credit_ids, credits)
    summary = summarize(credits, extensions, schedules)
    figures = write_figures(report_dir, summary)
    write_report(args.output, summary, funnel, rejected_rows, figures)
    print(f"Issued loans: {summary['n_loans']:,}")
    print(f"Borrowers: {summary['n_borrowers']:,}")
    print(f"Total principal: EUR {money(summary['amount_total'])}")
    print(f"Contractual charge: EUR {money(summary['revenue']['charge'])}")
    print(f"Outstanding exposure proxy: EUR {money(summary['exposure']['outstanding'])}")
    print(f"High-risk/impaired exposure proxy: EUR {money(summary['exposure']['impaired_or_high_risk'])}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
