#!/usr/bin/env python3
"""Build concrete customer lifecycle examples from sampled credit-platform data.

The script samples customers first, then streams each CSV and keeps only rows
for those customers. This keeps memory use small even when source files are
hundreds of MB.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path
from typing import Iterable


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/customer_lifecycle_examples.md")
CURRENT_DATE = date(2026, 6, 8)
EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00"}
REJECTED_CHART = "lifecycle_direct_rejected.svg"
ACCEPTED_CHART = "lifecycle_accepted.svg"
FLOWCHART = "lifecycle_flowchart.svg"
FLOWCHART_PNG = "lifecycle_flowchart.png"


def is_meaningful(value: str | None) -> bool:
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
    if not is_meaningful(value):
        return None
    text = (value or "").replace("/", "-")[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def first_values(rows: Iterable[dict[str, str]], fields: list[str], limit: int = 2) -> list[str]:
    values = []
    for row in rows:
        bits = []
        for field in fields:
            value = (row.get(field) or "").replace("\n", " ").strip()
            if is_meaningful(value):
                bits.append(f"{field}={value[:80]}")
        if bits:
            values.append("; ".join(bits))
        if len(values) >= limit:
            break
    return values


def read_customers(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle))


def sample_customer_ids(customers: list[dict[str, str]], sample_size: int, seed: int) -> list[str]:
    ids = [row["customer_id"] for row in customers if row.get("customer_id")]
    rng = random.Random(seed)
    return rng.sample(ids, min(sample_size, len(ids)))


def stream_by_customer(path: Path, customer_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            customer_id = row.get("customer_id")
            if customer_id in customer_ids:
                grouped[customer_id].append(row)
    return grouped


def stream_decisions_by_credit(path: Path, credit_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            credit_id = row.get("credit_id")
            if credit_id in credit_ids:
                grouped[credit_id].append(row)
    return grouped


def extract_schedule_preview(schedule: str | None, limit: int = 3) -> list[str]:
    if not schedule:
        return []
    matches = re.findall(
        r's:4:"date";s:\d+:"([^"]+)".*?s:1:"o";s:\d+:"([^"]+)".*?s:6:"amount";s:\d+:"([^"]+)"',
        schedule,
    )
    return [f"{schedule_date}: opening_balance={opening}, due={amount}" for schedule_date, opening, amount in matches[:limit]]


def credit_is_unpaid(credit: dict[str, str]) -> bool:
    return not is_meaningful(credit.get("paid"))


def credit_has_default_signal(credit: dict[str, str]) -> bool:
    debt = max(to_float(credit.get("debt")), to_float(credit.get("s_debt")), to_float(credit.get("r_debt")))
    delay = max(to_int(credit.get("current_delay")), to_int(credit.get("max_delay")))
    expire_date = parse_date(credit.get("expire"))
    return (
        debt > 0
        and (
            delay > 30
            or is_meaningful(credit.get("sold"))
            or to_float(credit.get("writeoff")) > 0
            or (expire_date is not None and expire_date < CURRENT_DATE)
        )
    )


def credit_is_clean_paid(credit: dict[str, str]) -> bool:
    return (
        is_meaningful(credit.get("paid"))
        and max(to_float(credit.get("debt")), to_float(credit.get("s_debt")), to_float(credit.get("r_debt"))) == 0
        and to_int(credit.get("max_delay")) == 0
        and to_float(credit.get("late_fee")) == 0
    )


def credit_is_active_current(credit: dict[str, str]) -> bool:
    expire_date = parse_date(credit.get("expire"))
    return (
        credit_is_unpaid(credit)
        and max(to_float(credit.get("debt")), to_float(credit.get("r_debt"))) > 0
        and to_int(credit.get("current_delay")) == 0
        and to_int(credit.get("max_delay")) == 0
        and not is_meaningful(credit.get("sold"))
        and (expire_date is None or expire_date >= CURRENT_DATE)
    )


def sort_by_created(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: row.get("created") or row.get("request_date") or row.get("date") or "")


def classify_customer(credits: list[dict[str, str]], rejected: list[dict[str, str]]) -> str:
    if rejected and not credits:
        return "1_direct_rejected"
    if any(credit_is_unpaid(credit) and credit_has_default_signal(credit) for credit in credits):
        return "2_issued_default_or_interrupted"
    if any(credit_is_clean_paid(credit) for credit in credits):
        return "3_issued_clean_completed"
    if any(credit_is_active_current(credit) for credit in credits):
        return "4_issued_active_current"
    if credits:
        return "5_issued_other_or_mixed"
    if rejected:
        return "6_rejected_only_other"
    return "7_no_application_found"


def choose_representative_credit(case_type: str, credits: list[dict[str, str]]) -> dict[str, str] | None:
    if not credits:
        return None
    predicates = {
        "2_issued_default_or_interrupted": lambda credit: credit_is_unpaid(credit) and credit_has_default_signal(credit),
        "3_issued_clean_completed": credit_is_clean_paid,
        "4_issued_active_current": credit_is_active_current,
    }
    predicate = predicates.get(case_type)
    if predicate:
        for credit in sort_by_created(credits):
            if predicate(credit):
                return credit
    return sort_by_created(credits)[-1]


def select_examples(classifications: dict[str, str], limit: int) -> list[str]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for customer_id, case_type in classifications.items():
        buckets[case_type].append(customer_id)
    for customer_ids in buckets.values():
        customer_ids.sort(key=lambda value: int(value))

    order = [
        "1_direct_rejected",
        "2_issued_default_or_interrupted",
        "3_issued_clean_completed",
        "4_issued_active_current",
        "5_issued_other_or_mixed",
        "6_rejected_only_other",
        "7_no_application_found",
    ]
    selected = []
    while len(selected) < limit:
        before = len(selected)
        for case_type in order:
            if buckets[case_type] and len(selected) < limit:
                selected.append(buckets[case_type].pop(0))
        if len(selected) == before:
            break
    return selected


def svg_text(x: int, y: int, text: str, size: int = 13, weight: str = "400", color: str = "#172033") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{escape(text)}</text>'
    )


def svg_box(x: int, y: int, width: int, height: int, title: str, lines: list[str], fill: str) -> list[str]:
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="#243047" stroke-width="1.2"/>',
        svg_text(x + 14, y + 25, title, 14, "700"),
    ]
    for index, line in enumerate(lines):
        parts.append(svg_text(x + 14, y + 48 + index * 18, line, 12, "400", "#3b4658"))
    return parts


def svg_arrow(x1: int, y1: int, x2: int, y2: int, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#516070" '
        f'stroke-width="2" marker-end="url(#arrow)"{dash}/>'
    )


def svg_arrow_label(x: int, y: int, text: str) -> str:
    return svg_text(x, y, text, 12, "700", "#384356")


def write_combined_flowchart(path: Path, selected_counts: dict[str, int], selected_total: int) -> None:
    direct = selected_counts.get("1_direct_rejected", 0) + selected_counts.get("6_rejected_only_other", 0)
    defaulted = selected_counts.get("2_issued_default_or_interrupted", 0)
    completed = selected_counts.get("3_issued_clean_completed", 0)
    active_current = selected_counts.get("4_issued_active_current", 0)
    mixed = selected_counts.get("5_issued_other_or_mixed", 0)
    no_application = selected_counts.get("7_no_application_found", 0)
    accepted = defaulted + completed + active_current + mixed
    observed_application = direct + accepted

    width, height = 1580, 940
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#516070"/>',
        "</marker>",
        "</defs>",
        '<rect width="1580" height="940" fill="#f7f8fb"/>',
        svg_text(38, 42, "Loan Application Lifecycle Flow", 25, "800"),
        svg_text(
            38,
            70,
            "Counts start from the 50 selected example customers. Timestamp/date fields are marked with [time].",
            13,
            "400",
            "#556070",
        ),
        svg_text(1220, 70, f"selected examples n={selected_total}", 14, "800", "#172033"),
    ]

    parts += svg_box(
        40,
        120,
        245,
        150,
        f"Sample customers (n={selected_total})",
        [
            "Action: sample customers",
            "Table: export_customers.csv",
            "Fields: customer_id",
            "created [time], modified [time]",
            "age, gender, category_id",
        ],
        "#e9f2ff",
    )
    parts += svg_box(
        345,
        120,
        285,
        150,
        f"Loan application observed (n={observed_application})",
        [
            "Action: loan application",
            "Rejected path table:",
            "export_credits_rejected.csv",
            "Fields: created [time], amount, period",
            "Accepted path: export_credits.created [time]",
        ],
        "#fff4df",
    )
    parts += svg_box(
        345,
        335,
        285,
        130,
        f"No application evidence (n={no_application})",
        [
            "Action: no linked loan event",
            "Tables scanned by customer_id",
            "No rows in credits or rejected",
            "Useful as profile-only customers",
        ],
        "#edf1f7",
    )
    parts += svg_box(
        700,
        60,
        300,
        155,
        f"Rejected after assessment (n={direct})",
        [
            "Action: credit assessment -> reject",
            "Table: export_credits_rejected.csv",
            "Fields: rejection_date [time]",
            "reason, admin_name, amount, period",
            "Join: customer_id",
        ],
        "#ffe7e7",
    )
    parts += svg_box(
        700,
        270,
        300,
        170,
        f"Credit issued / accepted (n={accepted})",
        [
            "Action: approve and issue credit",
            "Table: export_credits.csv",
            "Fields: id, customer_id, amount, period",
            "created [time], registered [time]",
            "expire [time], paid [time]",
            "Join to decisions: id -> credit_id",
        ],
        "#e9f8ef",
    )
    parts += svg_box(
        1060,
        80,
        310,
        145,
        "Credit assessment details",
        [
            "Action: approval / confirmation",
            "Table: export_credits_decisions.csv",
            "Fields: credit_id",
            "approve_date [time], confirm_date [time]",
            "decision_info, info, approver_id",
        ],
        "#f0ecff",
    )
    parts += svg_box(
        1060,
        275,
        310,
        165,
        "Repayment schedule",
        [
            "Action: planned instalments",
            "Table: export_credits.csv",
            "Field: schedule",
            "Nested fields: date [time], day",
            "o/opening balance, amount due",
            "planned, not actual payment ledger",
        ],
        "#fff7e8",
    )
    parts += svg_box(
        1060,
        500,
        310,
        150,
        "Post-issue monitoring",
        [
            "Action: track repayment status",
            "Tables: export_credits.csv",
            "export_credit_ext_requests.csv",
            "export_creditline_paydays.csv",
            "Fields: debt, r_debt, current_delay",
            "request_date/date/modified [time]",
        ],
        "#e8f7fb",
    )

    parts += svg_box(
        80,
        710,
        285,
        135,
        f"Completed normally (n={completed})",
        [
            "Action: loan completed",
            "Table: export_credits.csv",
            "Fields: paid [time], debt",
            "r_debt, max_delay, late_fee",
        ],
        "#edf7ed",
    )
    parts += svg_box(
        435,
        710,
        285,
        135,
        f"Default / interrupted (n={defaulted})",
        [
            "Action: loan performance breaks",
            "Table: export_credits.csv",
            "Fields: current_delay, max_delay",
            "r_debt, sold [time], writeoff",
        ],
        "#ffe7e7",
    )
    parts += svg_box(
        790,
        710,
        285,
        135,
        f"Active and current (n={active_current})",
        [
            "Action: still repaying",
            "Table: export_credits.csv",
            "Fields: paid empty, debt/r_debt",
            "expire [time], current_delay=0",
        ],
        "#eef3ff",
    )
    parts += svg_box(
        1145,
        710,
        285,
        135,
        f"Mixed / boundary (n={mixed})",
        [
            "Action: issued but not cleanly classified",
            "Tables: credits + rejected history",
            "Fields: paid [time], max_delay",
            "late_fee, rejection_date [time]",
        ],
        "#f3eef7",
    )

    parts += [
        svg_arrow(285, 195, 345, 195),
        svg_arrow_label(298, 180, f"n={selected_total}"),
        svg_arrow(470, 270, 470, 335),
        svg_arrow_label(485, 310, f"n={no_application}"),
        svg_arrow(630, 170, 700, 135),
        svg_arrow_label(638, 132, f"rejected n={direct}"),
        svg_arrow(630, 215, 700, 345),
        svg_arrow_label(640, 290, f"accepted n={accepted}"),
        svg_arrow(1000, 345, 1060, 152, dashed=True),
        svg_arrow_label(1010, 196, "decision join"),
        svg_arrow(1000, 355, 1060, 355),
        svg_arrow_label(1008, 340, "schedule"),
        svg_arrow(1215, 440, 1215, 500),
        svg_arrow_label(1230, 475, "monitor"),
        svg_arrow(1140, 650, 225, 710),
        svg_arrow_label(235, 690, f"n={completed}"),
        svg_arrow(1205, 650, 575, 710),
        svg_arrow_label(585, 690, f"n={defaulted}"),
        svg_arrow(1270, 650, 930, 710),
        svg_arrow_label(940, 690, f"n={active_current}"),
        svg_arrow(1335, 650, 1285, 710),
        svg_arrow_label(1295, 690, f"n={mixed}"),
        "</svg>",
    ]
    path.write_text("\n".join(parts), encoding="utf-8")


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped_text(draw, xy: tuple[int, int], text: str, font, fill: str, max_width: int, line_gap: int) -> int:
    x, y = xy
    words = text.split()
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        bbox = draw.textbbox((x, y), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not line:
            line = trial
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += line_gap
            line = word
    if line:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_gap
    return y


def draw_png_box(draw, x: int, y: int, width: int, height: int, title: str, lines: list[str], fill: str) -> None:
    title_font = load_font(18, bold=True)
    body_font = load_font(15)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=11, fill=fill, outline="#243047", width=2)
    draw_wrapped_text(draw, (x + 18, y + 22), title, title_font, "#172033", width - 36, 24)
    cursor = y + 62
    for line in lines:
        cursor = draw_wrapped_text(draw, (x + 18, cursor), line, body_font, "#3b4658", width - 36, 20)


def draw_png_arrow(draw, start: tuple[int, int], end: tuple[int, int], label: str | None = None) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill="#516070", width=4)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 14
    left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), left, right], fill="#516070")
    if label:
        label_font = load_font(15, bold=True)
        lx = int((x1 + x2) / 2)
        ly = int((y1 + y2) / 2) - 8
        draw.text((lx, ly), label, font=label_font, fill="#384356")


def write_combined_flowchart_png(path: Path, selected_counts: dict[str, int], selected_total: int) -> None:
    from PIL import Image, ImageDraw

    direct = selected_counts.get("1_direct_rejected", 0) + selected_counts.get("6_rejected_only_other", 0)
    defaulted = selected_counts.get("2_issued_default_or_interrupted", 0)
    completed = selected_counts.get("3_issued_clean_completed", 0)
    active_current = selected_counts.get("4_issued_active_current", 0)
    mixed = selected_counts.get("5_issued_other_or_mixed", 0)
    no_application = selected_counts.get("7_no_application_found", 0)
    accepted = defaulted + completed + active_current + mixed
    observed_application = direct + accepted

    width, height = 1800, 1120
    image = Image.new("RGBA", (width, height), "#f7f8fb")
    draw = ImageDraw.Draw(image)
    title_font = load_font(34, bold=True)
    subtitle_font = load_font(18)
    draw.text((44, 42), "Loan Application Lifecycle Flow", font=title_font, fill="#172033")
    draw.text(
        (44, 88),
        "Counts start from the 50 selected example customers. Timestamp/date fields are marked with [time].",
        font=subtitle_font,
        fill="#556070",
    )
    draw.text((1410, 88), f"selected examples n={selected_total}", font=load_font(18, bold=True), fill="#172033")

    draw_png_box(
        draw,
        50,
        160,
        300,
        170,
        f"Sample customers (n={selected_total})",
        [
            "Action: sample customers",
            "Table: export_customers.csv",
            "Fields: customer_id",
            "created [time], modified [time]",
            "age, gender, category_id",
        ],
        "#e9f2ff",
    )
    draw_png_box(
        draw,
        430,
        150,
        350,
        200,
        f"Loan application observed (n={observed_application})",
        [
            "Action: loan application",
            "Rejected path table:",
            "export_credits_rejected.csv",
            "Fields: created [time], amount, period",
            "Accepted path: export_credits.created [time]",
        ],
        "#fff4df",
    )
    draw_png_box(
        draw,
        430,
        420,
        350,
        150,
        f"No application evidence (n={no_application})",
        [
            "Action: no linked loan event",
            "Tables scanned by customer_id",
            "No rows in credits or rejected",
            "Useful as profile-only customers",
        ],
        "#edf1f7",
    )
    draw_png_box(
        draw,
        870,
        90,
        350,
        180,
        f"Rejected after assessment (n={direct})",
        [
            "Action: credit assessment -> reject",
            "Table: export_credits_rejected.csv",
            "Fields: rejection_date [time]",
            "reason, admin_name, amount, period",
            "Join: customer_id",
        ],
        "#ffe7e7",
    )
    draw_png_box(
        draw,
        870,
        330,
        350,
        200,
        f"Credit issued / accepted (n={accepted})",
        [
            "Action: approve and issue credit",
            "Table: export_credits.csv",
            "Fields: id, customer_id, amount, period",
            "created [time], registered [time]",
            "expire [time], paid [time]",
            "Join to decisions: id -> credit_id",
        ],
        "#e9f8ef",
    )
    draw_png_box(
        draw,
        1330,
        90,
        370,
        170,
        "Credit assessment details",
        [
            "Action: approval / confirmation",
            "Table: export_credits_decisions.csv",
            "Fields: credit_id",
            "approve_date [time], confirm_date [time]",
            "decision_info, info, approver_id",
        ],
        "#f0ecff",
    )
    draw_png_box(
        draw,
        1330,
        320,
        370,
        180,
        "Repayment schedule",
        [
            "Action: planned instalments",
            "Table: export_credits.csv",
            "Field: schedule",
            "Nested fields: date [time], day",
            "o/opening balance, amount due",
            "planned, not actual payment ledger",
        ],
        "#fff7e8",
    )
    draw_png_box(
        draw,
        1330,
        560,
        370,
        170,
        "Post-issue monitoring",
        [
            "Action: track repayment status",
            "Tables: export_credits.csv",
            "export_credit_ext_requests.csv",
            "export_creditline_paydays.csv",
            "Fields: debt, r_debt, current_delay",
            "request_date/date/modified [time]",
        ],
        "#e8f7fb",
    )
    draw_png_box(
        draw,
        70,
        860,
        330,
        145,
        f"Completed normally (n={completed})",
        [
            "Action: loan completed",
            "Table: export_credits.csv",
            "Fields: paid [time], debt",
            "r_debt, max_delay, late_fee",
        ],
        "#edf7ed",
    )
    draw_png_box(
        draw,
        510,
        860,
        330,
        145,
        f"Default / interrupted (n={defaulted})",
        [
            "Action: loan performance breaks",
            "Table: export_credits.csv",
            "Fields: current_delay, max_delay",
            "r_debt, sold [time], writeoff",
        ],
        "#ffe7e7",
    )
    draw_png_box(
        draw,
        950,
        860,
        330,
        145,
        f"Active and current (n={active_current})",
        [
            "Action: still repaying",
            "Table: export_credits.csv",
            "Fields: paid empty, debt/r_debt",
            "expire [time], current_delay=0",
        ],
        "#eef3ff",
    )
    draw_png_box(
        draw,
        1390,
        860,
        330,
        145,
        f"Mixed / boundary (n={mixed})",
        [
            "Action: issued but not cleanly classified",
            "Tables: credits + rejected history",
            "Fields: paid [time], max_delay",
            "late_fee, rejection_date [time]",
        ],
        "#f3eef7",
    )

    draw_png_arrow(draw, (350, 245), (430, 245), f"n={selected_total}")
    draw_png_arrow(draw, (605, 350), (605, 420), f"n={no_application}")
    draw_png_arrow(draw, (780, 220), (870, 175), f"rejected n={direct}")
    draw_png_arrow(draw, (780, 280), (870, 430), f"accepted n={accepted}")
    draw_png_arrow(draw, (1220, 430), (1330, 175), "decision join")
    draw_png_arrow(draw, (1220, 430), (1330, 410), "schedule")
    draw_png_arrow(draw, (1515, 500), (1515, 560), "monitor")
    draw_png_arrow(draw, (1440, 730), (235, 860), f"n={completed}")
    draw_png_arrow(draw, (1480, 730), (675, 860), f"n={defaulted}")
    draw_png_arrow(draw, (1520, 730), (1115, 860), f"n={active_current}")
    draw_png_arrow(draw, (1560, 730), (1555, 860), f"n={mixed}")

    image.save(path)


def write_lifecycle_flowchart(output_path: Path, selected_counts: dict[str, int], selected_total: int) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path = output_path.parent / FLOWCHART
    png_path = output_path.parent / FLOWCHART_PNG
    write_combined_flowchart(svg_path, selected_counts, selected_total)
    write_combined_flowchart_png(png_path, selected_counts, selected_total)
    return png_path


def write_rejected_chart(path: Path) -> None:
    width, height = 1120, 420
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#516070"/>',
        "</marker>",
        "</defs>",
        '<rect width="1120" height="420" fill="#f7f8fb"/>',
        svg_text(34, 40, "Direct Rejection Lifecycle", 22, "800"),
        svg_text(34, 66, "Time flows left to right. Labels show the source table and field used in EDA.", 13, "400", "#556070"),
        '<line x1="70" y1="330" x2="1030" y2="330" stroke="#8994a3" stroke-width="2" marker-end="url(#arrow)"/>',
        svg_text(1010, 356, "time", 13, "700", "#556070"),
    ]
    parts += svg_box(
        50,
        120,
        250,
        130,
        "Customer record",
        ["export_customers.customer_id", "export_customers.created", "profile / demographics"],
        "#e9f2ff",
    )
    parts += svg_box(
        365,
        120,
        260,
        130,
        "Application submitted",
        ["export_credits_rejected.created", "amount / period / charge", "customer_id links to customer"],
        "#fff4df",
    )
    parts += svg_box(
        690,
        120,
        290,
        130,
        "Rejected decision",
        ["export_credits_rejected.rejection_date", "export_credits_rejected.reason", "no matching issued credit required"],
        "#ffe7e7",
    )
    parts += svg_box(
        690,
        275,
        290,
        82,
        "EDA classification",
        ["rejected rows > 0", "issued credits = 0 for customer_id"],
        "#edf7ed",
    )
    parts += [
        svg_arrow(300, 185, 365, 185),
        svg_arrow(625, 185, 690, 185),
        svg_arrow(835, 250, 835, 275, dashed=True),
        "</svg>",
    ]
    path.write_text("\n".join(parts), encoding="utf-8")


def write_accepted_chart(path: Path) -> None:
    width, height = 1280, 560
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#516070"/>',
        "</marker>",
        "</defs>",
        '<rect width="1280" height="560" fill="#f7f8fb"/>',
        svg_text(34, 40, "Accepted Credit Lifecycle", 22, "800"),
        svg_text(34, 66, "Time flows left to right. Source fields are shown inside each lifecycle stage.", 13, "400", "#556070"),
        '<line x1="72" y1="485" x2="1190" y2="485" stroke="#8994a3" stroke-width="2" marker-end="url(#arrow)"/>',
        svg_text(1168, 512, "time", 13, "700", "#556070"),
    ]
    parts += svg_box(
        40,
        118,
        210,
        126,
        "Customer",
        ["export_customers.customer_id", "created / age / gender", "history aggregates"],
        "#e9f2ff",
    )
    parts += svg_box(
        300,
        118,
        220,
        126,
        "Credit issued",
        ["export_credits.id", "customer_id / created", "amount / period / expire"],
        "#e9f8ef",
    )
    parts += svg_box(
        570,
        118,
        240,
        126,
        "Approval details",
        ["export_credits_decisions.credit_id", "approve_date / confirm_date", "decision_info / info"],
        "#f0ecff",
    )
    parts += svg_box(
        860,
        105,
        250,
        150,
        "Repayment plan",
        ["export_credits.schedule", "date / opening balance", "due amount per period", "planned, not necessarily paid"],
        "#fff4df",
    )
    parts += svg_box(
        860,
        285,
        250,
        122,
        "Optional monthly signals",
        ["export_creditline_paydays.date", "debt / delay / max_delay", "extension requests if present"],
        "#e8f7fb",
    )
    parts += svg_box(
        1125,
        70,
        125,
        98,
        "Completed",
        ["paid set", "debt = 0", "max_delay = 0"],
        "#edf7ed",
    )
    parts += svg_box(
        1125,
        220,
        125,
        110,
        "Default",
        ["unpaid debt", "high delay", "sold/writeoff"],
        "#ffe7e7",
    )
    parts += svg_box(
        1125,
        382,
        125,
        105,
        "Active current",
        ["paid empty", "delay = 0", "future expire"],
        "#eef3ff",
    )
    parts += [
        svg_arrow(250, 181, 300, 181),
        svg_arrow(520, 181, 570, 181),
        svg_arrow(810, 181, 860, 181),
        svg_arrow(985, 255, 985, 285, dashed=True),
        svg_arrow(1110, 180, 1125, 120),
        svg_arrow(1110, 205, 1125, 275),
        svg_arrow(1110, 360, 1125, 435),
        "</svg>",
    ]
    path.write_text("\n".join(parts), encoding="utf-8")


def write_lifecycle_charts(output_path: Path) -> tuple[Path, Path]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path = output_path.parent / REJECTED_CHART
    accepted_path = output_path.parent / ACCEPTED_CHART
    write_rejected_chart(rejected_path)
    write_accepted_chart(accepted_path)
    return rejected_path, accepted_path


def write_report(
    output_path: Path,
    sampled_ids: list[str],
    selected_ids: list[str],
    customers_by_id: dict[str, dict[str, str]],
    credits_by_customer: dict[str, list[dict[str, str]]],
    rejected_by_customer: dict[str, list[dict[str, str]]],
    ext_by_customer: dict[str, list[dict[str, str]]],
    payday_by_customer: dict[str, list[dict[str, str]]],
    decisions_by_credit: dict[str, list[dict[str, str]]],
    combined_by_customer: dict[str, list[dict[str, str]]],
) -> None:
    classifications = {
        customer_id: classify_customer(credits_by_customer[customer_id], rejected_by_customer[customer_id])
        for customer_id in sampled_ids
    }
    selected_counts = defaultdict(int)
    for customer_id in selected_ids:
        selected_counts[classifications[customer_id]] += 1
    flowchart_path = write_lifecycle_flowchart(output_path, selected_counts, len(selected_ids))

    counts = defaultdict(int)
    for case_type in classifications.values():
        counts[case_type] += 1
    matched_rows = {
        "issued_credits": sum(len(rows) for rows in credits_by_customer.values()),
        "rejected_applications": sum(len(rows) for rows in rejected_by_customer.values()),
        "extension_requests": sum(len(rows) for rows in ext_by_customer.values()),
        "payday_snapshots": sum(len(rows) for rows in payday_by_customer.values()),
        "decision_rows": sum(len(rows) for rows in decisions_by_credit.values()),
        "combined_rows": sum(len(rows) for rows in combined_by_customer.values()),
    }

    lines = [
        "# Sampled Customer Lifecycle Examples",
        "",
        f"Sample method: `{len(sampled_ids)}` random customers from `export_customers.csv`, seed `20260608`.",
        f"Selected examples: `{len(selected_ids)}` customers from that sample.",
        "",
        "Large-file strategy: sample customer IDs first, then stream each CSV and keep only matching rows. `export_credits_decisions.csv` has no `customer_id`, so the script first collects `export_credits.id`, then joins `credits.id -> decisions.credit_id`.",
        "",
        "## How to Join One Customer Across Tables",
        "",
        "- Direct `customer_id` lookup: `export_customers.csv`, `export_credits.csv`, `export_credits_rejected.csv`, `export_credit_ext_requests.csv`, `export_creditline_paydays.csv`, and the combined export.",
        "- Indirect lookup for decisions: `export_customers.customer_id -> export_credits.customer_id`, then `export_credits.id -> export_credits_decisions.credit_id`.",
        "- The combined export is useful as a check, but the source tables are clearer for lifecycle logic.",
        "",
        "## Lifecycle Flowchart",
        "",
        "The flowchart branch counts start from the 50 selected example customers, while the next section reports counts for the full 200-customer random sample.",
        "",
        f"![Loan Application Lifecycle Flow]({flowchart_path.name})",
        "",
        f"## Case Counts In The {len(sampled_ids)}-Customer Sample",
        "",
    ]
    for case_type in sorted(counts):
        lines.append(f"- `{case_type}`: {counts[case_type]}")

    lines.extend(
        [
            "",
            f"## Linked Rows Found For The {len(sampled_ids)} Customers",
            "",
        ]
    )
    for table_name, row_count in matched_rows.items():
        lines.append(f"- `{table_name}`: {row_count}")

    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- `1_direct_rejected`: rejected applications exist and no issued credit was found for this customer in the sample-linked scan.",
            "- `2_issued_default_or_interrupted`: at least one issued credit is unpaid and has debt plus a strong default signal such as high delay, sale/writeoff, or overdue maturity.",
            "- `3_issued_clean_completed`: at least one issued credit has `paid` set, zero debt, zero max delay, and zero late fee.",
            "- `4_issued_active_current`: at least one issued credit is unpaid, has outstanding debt, has no current/max delay, and its due date is not before the analysis date.",
            "",
            "## Selected Customer Examples",
            "",
        ]
    )

    for customer_id in selected_ids:
        customer = customers_by_id[customer_id]
        credits = sort_by_created(credits_by_customer[customer_id])
        rejected = sort_by_created(rejected_by_customer[customer_id])
        extensions = sorted(ext_by_customer[customer_id], key=lambda row: row.get("request_date") or "")
        paydays = sorted(payday_by_customer[customer_id], key=lambda row: row.get("date") or "")
        combined_rows = combined_by_customer[customer_id]
        case_type = classifications[customer_id]
        representative_credit = choose_representative_credit(case_type, credits)
        decision_count = sum(len(decisions_by_credit.get(credit.get("id", ""), [])) for credit in credits)

        lines.extend(
            [
                f"### Customer `{customer_id}` - `{case_type}`",
                "",
                (
                    f"- Customer snapshot: age `{customer.get('age', '')}`, gender `{customer.get('gender', '')}`, "
                    f"created `{customer.get('created', '')}`, applications `{customer.get('applications', '')}`, "
                    f"customer-table credits `{customer.get('credits', '')}`, credits_paid `{customer.get('credits_paid', '')}`, "
                    f"delay_max `{customer.get('delay_max', '')}`."
                ),
                (
                    f"- Linked rows: issued credits `{len(credits)}`, rejected applications `{len(rejected)}`, "
                    f"extension requests `{len(extensions)}`, payday snapshots `{len(paydays)}`, "
                    f"decision rows `{decision_count}`, combined rows `{len(combined_rows)}`."
                ),
            ]
        )

        rejected_examples = first_values(
            rejected,
            ["id", "created", "amount", "period", "rejection_date", "reason"],
        )
        for item in rejected_examples:
            lines.append(f"- Rejected example: {item}")

        if representative_credit:
            credit_id = representative_credit.get("id", "")
            decisions = decisions_by_credit.get(credit_id, [])
            lines.append(
                "- Representative credit: "
                f"id `{credit_id}`, created `{representative_credit.get('created', '')}`, "
                f"amount `{representative_credit.get('amount', '')}`, period `{representative_credit.get('period', '')}`, "
                f"expire `{representative_credit.get('expire', '')}`, paid `{representative_credit.get('paid', '')}`, "
                f"debt `{representative_credit.get('debt', '')}`, r_debt `{representative_credit.get('r_debt', '')}`, "
                f"current_delay `{representative_credit.get('current_delay', '')}`, max_delay `{representative_credit.get('max_delay', '')}`, "
                f"late_fee `{representative_credit.get('late_fee', '')}`, sold `{representative_credit.get('sold', '')}`."
            )
            schedule_preview = extract_schedule_preview(representative_credit.get("schedule"))
            if schedule_preview:
                lines.append(f"- Schedule preview: {' | '.join(schedule_preview)}")
            decision_examples = first_values(decisions, ["approve_date", "confirm_date", "approver_id", "confirmer_id"])
            for item in decision_examples:
                lines.append(f"- Decision example for credit `{credit_id}`: {item}")

        extension_examples = first_values(
            extensions,
            ["credit_id", "request_date", "period", "complete_date", "price", "application_status"],
        )
        for item in extension_examples:
            lines.append(f"- Extension example: {item}")

        payday_examples = first_values(paydays, ["credit_id", "date", "delay", "debt", "reduction", "ret", "max_delay"])
        for item in payday_examples:
            lines.append(f"- Payday example: {item}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample customers and build lifecycle examples.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--examples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    customers = read_customers(args.data_dir / "export_customers.csv")
    sampled_ids = sample_customer_ids(customers, args.sample_size, args.seed)
    sampled_id_set = set(sampled_ids)
    customers_by_id = {row["customer_id"]: row for row in customers if row.get("customer_id") in sampled_id_set}

    credits_by_customer = stream_by_customer(args.data_dir / "export_credits.csv", sampled_id_set)
    rejected_by_customer = stream_by_customer(args.data_dir / "export_credits_rejected.csv", sampled_id_set)
    ext_by_customer = stream_by_customer(args.data_dir / "export_credit_ext_requests.csv", sampled_id_set)
    payday_by_customer = stream_by_customer(args.data_dir / "export_creditline_paydays.csv", sampled_id_set)
    combined_by_customer = stream_by_customer(args.data_dir / "export (tables combined).csv", sampled_id_set)

    credit_ids = {row["id"] for rows in credits_by_customer.values() for row in rows if row.get("id")}
    decisions_by_credit = stream_decisions_by_credit(args.data_dir / "export_credits_decisions.csv", credit_ids)

    classifications = {
        customer_id: classify_customer(credits_by_customer[customer_id], rejected_by_customer[customer_id])
        for customer_id in sampled_ids
    }
    selected_ids = select_examples(classifications, args.examples)

    write_report(
        args.output,
        sampled_ids,
        selected_ids,
        customers_by_id,
        credits_by_customer,
        rejected_by_customer,
        ext_by_customer,
        payday_by_customer,
        decisions_by_credit,
        combined_by_customer,
    )

    print(f"Sampled customers: {len(sampled_ids)}")
    print(f"Selected examples: {len(selected_ids)}")
    for case_type in sorted(set(classifications.values())):
        print(f"{case_type}: {sum(1 for value in classifications.values() if value == case_type)}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
