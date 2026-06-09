#!/usr/bin/env python3
"""Portfolio-level descriptive statistics for the credit platform exports.

The script streams each CSV and keeps only small sets/counters in memory. It
uses customer_id before loan issuance and credit id after issuance.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/portfolio_overview.md")
DEFAULT_FLOWCHART = Path("docs/portfolio_flowchart.png")
CURRENT_DATE = date(2026, 6, 8)
EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00"}


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


def read_customer_ids(path: Path) -> tuple[int, set[str]]:
    rows = 0
    customer_ids = set()
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            if row.get("customer_id"):
                customer_ids.add(row["customer_id"])
    return rows, customer_ids


def read_rejections(path: Path) -> dict:
    customer_ids = set()
    rows = 0
    amount_total = 0.0
    by_customer = Counter()
    by_year = Counter()

    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            customer_id = row.get("customer_id")
            if customer_id:
                customer_ids.add(customer_id)
                by_customer[customer_id] += 1
            amount_total += to_float(row.get("amount"))
            year = (row.get("created") or "")[:4]
            if year.isdigit():
                by_year[year] += 1

    return {
        "rows": rows,
        "customer_ids": customer_ids,
        "amount_total": amount_total,
        "by_customer": by_customer,
        "by_year": by_year,
    }


def read_credits(path: Path) -> dict:
    customer_ids = set()
    credit_ids = set()
    rows = 0
    by_customer = Counter()
    by_year = Counter()
    status_counts = Counter()
    status_amounts = defaultdict(float)
    max_delay_buckets = Counter()
    current_delay_buckets = Counter()
    totals = Counter()
    money = defaultdict(float)

    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            customer_id = row.get("customer_id")
            credit_id = row.get("id")
            if customer_id:
                customer_ids.add(customer_id)
                by_customer[customer_id] += 1
            if credit_id:
                credit_ids.add(credit_id)

            amount = to_float(row.get("amount"))
            status = credit_status(row)
            status_counts[status] += 1
            status_amounts[status] += amount

            money["amount_total"] += amount
            money["charge_total"] += to_float(row.get("charge"))
            money["debt_total"] += to_float(row.get("debt"))
            money["r_debt_total"] += to_float(row.get("r_debt"))
            money["late_fee_total"] += to_float(row.get("late_fee"))
            if meaningful(row.get("paid")):
                totals["paid_count"] += 1

            max_delay = to_int(row.get("max_delay"))
            current_delay = to_int(row.get("current_delay"))
            bucket_delay(max_delay_buckets, max_delay)
            bucket_delay(current_delay_buckets, current_delay)

            year = (row.get("created") or "")[:4]
            if year.isdigit():
                by_year[year] += 1

    return {
        "rows": rows,
        "customer_ids": customer_ids,
        "credit_ids": credit_ids,
        "by_customer": by_customer,
        "by_year": by_year,
        "status_counts": status_counts,
        "status_amounts": status_amounts,
        "max_delay_buckets": max_delay_buckets,
        "current_delay_buckets": current_delay_buckets,
        "totals": totals,
        "money": money,
    }


def bucket_delay(counter: Counter, value: int) -> None:
    if value == 0:
        counter["0"] += 1
    elif value <= 30:
        counter["1-30"] += 1
    elif value <= 60:
        counter["31-60"] += 1
    elif value <= 90:
        counter["61-90"] += 1
    else:
        counter["90+"] += 1


def read_schedule_coverage(path: Path, issued_credit_ids: set[str]) -> dict:
    rows = 0
    schedule_credit_ids = set()
    totals = defaultdict(float)

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            credit_id = row.get("credit_id")
            if credit_id:
                schedule_credit_ids.add(credit_id)
            totals["principal"] += to_float(row.get("pay_amount"))
            totals["interest"] += to_float(row.get("pay_interest"))
            totals["fee"] += to_float(row.get("pay_administrative_fee"))
            totals["sum"] += to_float(row.get("pay_sum"))

    return {
        "rows": rows,
        "schedule_credit_ids": schedule_credit_ids,
        "issued_with_schedule": issued_credit_ids & schedule_credit_ids,
        "issued_without_schedule": issued_credit_ids - schedule_credit_ids,
        "schedule_not_in_issued": schedule_credit_ids - issued_credit_ids,
        "totals": totals,
    }


def collect_stats(data_dir: Path) -> dict:
    customer_rows, customer_ids = read_customer_ids(data_dir / "export_customers.csv")
    rejections = read_rejections(data_dir / "export_credits_rejected.csv")
    credits = read_credits(data_dir / "export_credits.csv")
    schedules = read_schedule_coverage(data_dir / "credits_schedules_all.csv", credits["credit_ids"])

    applicants = rejections["customer_ids"] | credits["customer_ids"]
    rejected_only = rejections["customer_ids"] - credits["customer_ids"]
    approved_only = credits["customer_ids"] - rejections["customer_ids"]
    both = rejections["customer_ids"] & credits["customer_ids"]
    no_application = customer_ids - applicants

    return {
        "customer_rows": customer_rows,
        "customer_ids": customer_ids,
        "applicants": applicants,
        "rejected_only": rejected_only,
        "approved_only": approved_only,
        "both": both,
        "no_application": no_application,
        "rejections": rejections,
        "credits": credits,
        "schedules": schedules,
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


def draw_text(draw, xy, text: str, font, fill: str, width: int, line_height: int) -> int:
    x, y = xy
    words = text.split()
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        bbox = draw.textbbox((x, y), trial, font=font)
        if bbox[2] - bbox[0] <= width or not line:
            line = trial
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height
            line = word
    if line:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def draw_box(draw, x: int, y: int, w: int, h: int, title: str, lines: list[str], fill: str) -> None:
    title_font = load_font(18, True)
    body_font = load_font(15)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=fill, outline="#243047", width=2)
    draw_text(draw, (x + 16, y + 18), title, title_font, "#172033", w - 32, 24)
    cy = y + 58
    for line in lines:
        cy = draw_text(draw, (x + 16, cy), line, body_font, "#3b4658", w - 32, 20)


def draw_arrow(draw, start: tuple[int, int], end: tuple[int, int], label: str = "") -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill="#516070", width=4)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 14
    left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), left, right], fill="#516070")
    if label:
        draw.text(((x1 + x2) / 2, (y1 + y2) / 2 - 12), label, font=load_font(15, True), fill="#384356")


def write_flowchart(path: Path, stats: dict) -> None:
    from PIL import Image, ImageDraw

    total_customers = len(stats["customer_ids"])
    applicants = len(stats["applicants"])
    no_application = len(stats["no_application"])
    rejected_only = len(stats["rejected_only"])
    approved_only = len(stats["approved_only"])
    both = len(stats["both"])
    approved_customers = len(stats["credits"]["customer_ids"])
    issued_credits = stats["credits"]["rows"]
    statuses = stats["credits"]["status_counts"]
    other_count = statuses.get("other_unpaid_no_debt", 0) + statuses.get("unpaid_past_maturity_no_current_delay", 0)

    image = Image.new("RGBA", (2100, 1120), "#f7f8fb")
    draw = ImageDraw.Draw(image)
    draw.text((42, 34), "Portfolio Application and Issued-Credit Flow", font=load_font(34, True), fill="#172033")
    draw.text(
        (42, 82),
        "Customer-level before issuance; credit-id level after issuance. Counts are full-table counts.",
        font=load_font(18),
        fill="#556070",
    )

    draw_box(
        draw,
        50,
        175,
        330,
        165,
        f"Registered customers (n={total_customers:,})",
        ["Unit: customer_id", "Table: export_customers.csv", "Field: customer_id"],
        "#e9f2ff",
    )
    draw_box(
        draw,
        470,
        155,
        380,
        210,
        f"Loan application evidence (n={applicants:,})",
        [
            "Unit: customer_id",
            "Rejected evidence: export_credits_rejected.csv",
            "Approved evidence: export_credits.csv",
            "Join field: customer_id",
        ],
        "#fff4df",
    )
    draw_box(
        draw,
        470,
        455,
        380,
        150,
        f"No application evidence (n={no_application:,})",
        ["In customer master only", "No rows in issued or rejected tables"],
        "#edf1f7",
    )
    draw_box(
        draw,
        960,
        100,
        390,
        160,
        f"Rejected only customers (n={rejected_only:,})",
        ["Unit: customer_id", "Rejected rows exist", "No issued credit found"],
        "#ffe7e7",
    )
    draw_box(
        draw,
        960,
        360,
        430,
        245,
        f"Customers with issued credit (n={approved_customers:,})",
        [
            "Unit: customer_id",
            f"{approved_only:,} approved only",
            f"{both:,} with rejection history",
            "Rejection history means at least one",
            "rejected application and at least one",
            "issued credit for the same customer",
        ],
        "#e9f8ef",
    )
    draw_box(
        draw,
        1510,
        225,
        430,
        190,
        f"Issued credits (n={issued_credits:,})",
        [
            "Unit switches to credit id",
            f"Approved customers: {approved_customers:,}",
            "Table: export_credits.csv",
            "Key: export_credits.id",
        ],
        "#e9f8ef",
    )
    draw_box(
        draw,
        1510,
        565,
        500,
        360,
        "Issued-credit status distribution",
        [
            f"Completed clean: {statuses.get('completed_clean', 0):,}",
            f"Completed with delay/fees: {statuses.get('completed_with_delay_or_fees', 0):,}",
            f"Active current: {statuses.get('active_current_not_due_or_no_delay', 0):,}",
            f"Active delinquent: {statuses.get('active_delinquent_current_delay', 0):,}",
            f"Sold / written off: {statuses.get('sold_or_written_off', 0):,}",
            f"Other issued states: {other_count:,}",
            "Unit: credit id",
        ],
        "#edf1f7",
    )

    draw_arrow(draw, (380, 255), (470, 255))
    draw_arrow(draw, (660, 365), (660, 455))
    draw_arrow(draw, (850, 220), (960, 175))
    draw_arrow(draw, (850, 300), (960, 480))
    draw_arrow(draw, (1390, 480), (1510, 320))
    draw_arrow(draw, (1725, 415), (1725, 565))

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def write_report(output_path: Path, flowchart_path: Path, stats: dict) -> None:
    customers = len(stats["customer_ids"])
    applicants = len(stats["applicants"])
    approved_customers = len(stats["credits"]["customer_ids"])
    rejected_customers = len(stats["rejections"]["customer_ids"])
    rejected_only = len(stats["rejected_only"])
    approved_only = len(stats["approved_only"])
    both = len(stats["both"])
    no_application = len(stats["no_application"])
    credits = stats["credits"]
    rejections = stats["rejections"]
    schedules = stats["schedules"]

    lines = [
        "# Portfolio Overview",
        "",
        "This is a descriptive full-table portfolio view. Customer-level counts use `customer_id` before issuance; issued-credit status counts use `export_credits.id` after issuance.",
        "",
        f"![Portfolio Flowchart]({flowchart_path.name})",
        "",
        "## Customer-Level Funnel",
        "",
        f"- Registered customers: `{customers:,}`",
        f"- Customers with loan application evidence: `{applicants:,}` ({pct(applicants, customers):.1f}% of registered customers)",
        f"- Customers with no application evidence: `{no_application:,}` ({pct(no_application, customers):.1f}%)",
        f"- Customers with at least one rejected application: `{rejected_customers:,}`",
        f"- Customers with at least one issued/approved credit: `{approved_customers:,}`",
        f"- Rejected only: `{rejected_only:,}`",
        f"- Approved only: `{approved_only:,}`",
        f"- Issued customers with rejection history: `{both:,}`",
        "",
        "## Application / Credit Rows",
        "",
        f"- Rejected application rows: `{rejections['rows']:,}`",
        f"- Issued credit rows: `{credits['rows']:,}`",
        f"- Row-level issued share among issued + rejected rows: `{pct(credits['rows'], credits['rows'] + rejections['rows']):.1f}%`",
        f"- Total requested amount in rejected rows: `EUR {rejections['amount_total']:,.2f}`",
        f"- Total issued principal amount: `EUR {credits['money']['amount_total']:,.2f}`",
        f"- Total planned charge in issued credits: `EUR {credits['money']['charge_total']:,.2f}`",
        "",
        "## Issued-Credit Status",
        "",
        "| status | credits | share | issued amount |",
        "|---|---:|---:|---:|",
    ]
    for key, count in credits["status_counts"].most_common():
        amount = credits["status_amounts"].get(key, 0.0)
        lines.append(f"| `{key}` | {count:,} | {pct(count, credits['rows']):.1f}% | EUR {amount:,.2f} |")

    lines.extend(
        [
            "",
            "## Delay And Debt Snapshot",
            "",
            f"- Paid credits: `{credits['totals']['paid_count']:,}`",
            f"- Sum of `debt`: `EUR {credits['money']['debt_total']:,.2f}`",
            f"- Sum of `r_debt`: `EUR {credits['money']['r_debt_total']:,.2f}`",
            f"- Sum of `late_fee`: `EUR {credits['money']['late_fee_total']:,.2f}`",
            f"- `max_delay` buckets: `{dict(credits['max_delay_buckets'])}`",
            f"- `current_delay` buckets: `{dict(credits['current_delay_buckets'])}`",
            "",
            "## Schedule Coverage",
            "",
            f"- Schedule rows: `{schedules['rows']:,}`",
            f"- Unique credit IDs in schedule table: `{len(schedules['schedule_credit_ids']):,}`",
            f"- Issued credits with schedule rows: `{len(schedules['issued_with_schedule']):,}`",
            f"- Issued credits without schedule rows: `{len(schedules['issued_without_schedule']):,}`",
            f"- Schedule credit IDs not present in current `export_credits.csv`: `{len(schedules['schedule_not_in_issued']):,}`",
            f"- Planned schedule principal total: `EUR {schedules['totals']['principal']:,.2f}`",
            f"- Planned schedule interest total: `EUR {schedules['totals']['interest']:,.2f}`",
            f"- Planned schedule administrative fee total: `EUR {schedules['totals']['fee']:,.2f}`",
            "",
            "## Notes",
            "",
            "- Customer counts can overlap: a customer may have rejected applications and later issued credits.",
            "- The mutually exclusive customer groups are `rejected_only`, `approved_only`, `issued customers with rejection history`, and `no_application`.",
            f"- The {approved_customers:,} customers with issued credit consist of {approved_only:,} approved-only customers plus {both:,} issued customers with rejection history.",
            "- Issued-credit status is counted by loan/credit ID, not by customer.",
            "- `credits_schedules_all.csv` is planned installment schedule data, not actual payment history.",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a full portfolio overview.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--flowchart", type=Path, default=DEFAULT_FLOWCHART)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = collect_stats(args.data_dir)
    write_flowchart(args.flowchart, stats)
    write_report(args.output, args.flowchart, stats)
    print(f"Registered customers: {len(stats['customer_ids']):,}")
    print(f"Applicant customers: {len(stats['applicants']):,}")
    print(f"Rejected-only customers: {len(stats['rejected_only']):,}")
    print(f"Approved customers: {len(stats['credits']['customer_ids']):,}")
    print(f"Issued credits: {stats['credits']['rows']:,}")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.flowchart}")


if __name__ == "__main__":
    main()
