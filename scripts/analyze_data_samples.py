#!/usr/bin/env python3
"""Summarize the first rows of the local credit platform CSV exports.

The raw data folder is intentionally kept outside the repository because the
files are large and may contain sensitive fields. This script reads only a
small sample and writes a lightweight Markdown overview.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/data_overview.md")
FILES = {
    "customers": "export_customers.csv",
    "credits": "export_credits.csv",
    "credits_rejected": "export_credits_rejected.csv",
    "credit_ext_requests": "export_credit_ext_requests.csv",
    "creditline_paydays": "export_creditline_paydays.csv",
    "credits_decisions": "export_credits_decisions.csv",
    "tables_combined": "export (tables combined).csv",
}
EMPTY_VALUES = {"", "0", "0.00", "0.000000", "0000-00-00", "0000-00-00 00:00:00"}

TABLE_NOTES = {
    "customers": [
        "This file appears to be customer master data. Each row is a borrower/customer profile with identity/contact fields, demographics, address, employment and income information, registration source, risk/application flags, credit history counters, and aggregate repayment/loan metrics.",
        "The natural primary key is `customer_id`, which links to loan-level files through `customer_id`.",
    ],
    "credits": [
        "This file appears to be loan or credit-contract level data. Each row is a credit issued or requested by a `customer_id`, with amount, term, pricing, due dates, repayment status, delinquency/collection fields, system configuration snapshots, and audit/channel metadata.",
        "The natural join key to customers is `customer_id`; the loan primary key appears to be `id`.",
    ],
    "credits_rejected": [
        "This file appears to contain rejected credit applications. It has requested amount/period/pricing, rejection reason, rejection date, channel fields, and some serialized application data.",
        "It can be useful for modeling approval/rejection outcomes when combined with accepted credits and customer information.",
    ],
    "credit_ext_requests": [
        "This file appears to contain extension or rollover requests for existing credits. Each row links a `customer_id` to a `credit_id` and records request/completion dates, extension period, price, status, and confirmation metadata.",
        "It can be used to study refinancing/extension behavior after credit origination.",
    ],
    "creditline_paydays": [
        "This file appears to contain payday snapshots for credit-line style products. It links `customer_id` and `credit_id` to monthly-like `date` rows with delay, debt, reduction, returned amount, active flag, max delay, discount, and modified time.",
        "This is the most explicit separate time-series table found in the folder, though it is much smaller than the main credit table.",
    ],
    "credits_decisions": [
        "This file appears to contain underwriting or approval decision details for credits. It links to loans through `credit_id` and stores serialized decision signals plus approver/confirmer IDs and approval/confirmation dates.",
        "The `decision_info` and `info` fields likely need parsing before they are useful as model features.",
    ],
    "tables_combined": [
        "This file appears to be a pre-joined wide export that combines customer, credit, payday, decision, and extension-request fields into one table.",
        "It may be convenient for quick EDA, but for clean modeling it is usually safer to understand the source tables first and then build a deliberate analytical table.",
    ],
}

DATE_TOKENS = [
    "date",
    "time",
    "created",
    "modified",
    "expire",
    "paid",
    "registered",
    "last",
    "first",
    "start",
    "stop",
    "withdraw",
    "transfer",
    "termination",
    "reject",
    "request",
    "complete",
]


COLUMN_GROUPS = {
    "credits": {
        "identifiers_and_links": [
            "id",
            "customer_id",
            "contract_id",
            "account_number",
            "number",
            "outer_system_id",
            "outer_credit_id",
            "product_id",
            "investor_id",
            "broker_id",
            "employer_id",
            "representative_id",
        ],
        "loan_terms_and_pricing": [
            "amount",
            "issued_amount",
            "period",
            "charge",
            "administrative_fee",
            "insurance",
            "interest",
            "apr",
            "tax_apr",
            "cinterest",
            "creditline_amount",
            "virtual_amount",
            "discount",
            "discount_code",
        ],
        "dates_and_lifecycle": [
            "created",
            "registered",
            "modified",
            "expire",
            "paid",
            "s_date",
            "s_expire",
            "stop_date",
            "transfer_date",
            "termination_date",
            "withdraw_date",
            "confirm_code_date",
            "admin_start_time",
        ],
        "repayment_and_balance": [
            "debt",
            "s_debt",
            "r_debt",
            "residual_amount",
            "overpaid",
            "p_amount",
            "s_payment",
            "s_paid_number",
            "l_pay",
            "l_amount",
            "balance_order_id",
        ],
        "delinquency_and_collection": [
            "penalty",
            "late_fee",
            "late_fee_corr",
            "late_fee_limit",
            "current_delay",
            "max_delay",
            "dc_contact",
            "dc_contact_date",
            "court_date",
            "sold",
            "writeoff",
            "writeoff_a",
            "urgency",
        ],
        "configuration_fields": [
            "cfg_penalty",
            "cfg_penalty_delay",
            "cfg_late_fee",
            "cfg_late_fee_start",
            "cfg_late_fee_stop",
            "cfg_interest_apr",
            "cfg_interest_start",
            "cfg_interest_stop",
            "cfg_interest_mode",
            "cfg_bailiff",
            "cfg_sais",
            "cfg_court",
        ],
        "structured_or_text_fields": [
            "schedule",
            "o_schedule",
            "description",
            "comments",
            "reason",
            "ref",
            "lander",
            "features_id",
            "plist_options",
        ],
        "audit_channel_and_flags": [
            "confirmed",
            "conditions_accepted",
            "solvency_checked",
            "credit_ip",
            "credit_domain",
            "api_user_id",
            "admin_id",
            "office_id",
            "currency",
            "c_currency",
            "bank",
            "e_sign",
            "archive",
            "category_changed",
        ],
    },
    "customers": {
        "identifiers_and_account": [
            "customer_id",
            "category_id",
            "login",
            "contract_id",
            "contract_code",
            "uin",
            "enabled",
            "status",
            "state",
            "acc_status_id",
            "admin_id",
            "sub_admin_id",
        ],
        "personal_and_contact": [
            "email",
            "email2",
            "realname",
            "surname",
            "midname",
            "midname2",
            "mob_phone",
            "mob_phone2",
            "phone",
            "work_phone",
            "contact_name",
            "contact_phone",
            "person_code",
            "birthday",
            "age",
            "gender",
        ],
        "address_and_region": [
            "city",
            "county",
            "parish",
            "village",
            "address",
            "zipcode",
            "city2",
            "county2",
            "parish2",
            "village2",
            "address2",
            "zipcode2",
            "region",
            "region2",
            "country",
            "street",
        ],
        "employment_and_income": [
            "workplace",
            "workplace_address",
            "workplace_position",
            "work_activities",
            "work_status",
            "work_company_code",
            "company_code",
            "company_name",
            "employers_ids",
            "income",
            "dependents",
            "home_status",
        ],
        "credit_history": [
            "credits",
            "exts",
            "credits_paid",
            "exts_paid",
            "all_paid",
            "all_expired",
            "last_credit_id",
            "last_credit_date",
            "first_credit_date",
            "first_credit_paid_date",
            "last_payment_date",
            "last_extension_date",
            "paid_credits_amount_max",
        ],
        "risk_and_limits": [
            "debt_limit",
            "debt",
            "credit_limit",
            "overpaid",
            "delay",
            "delay_max",
            "days_to_expire",
            "days_from_last_loan_repayment",
            "BDS_score",
            "evaluation_category_id",
            "fraud",
            "exaction_status",
            "applications_disabled",
            "data_use_disabled",
        ],
        "application_and_conversion": [
            "applications",
            "applications_rejected",
            "last_rejection_date",
            "last_application_date",
            "activated",
            "lander",
            "ref",
            "reg_method",
            "reg_form_id",
            "reg_confirm_method",
            "marketing",
        ],
        "financial_aggregates": [
            "all_payments_amount",
            "all_credits_amount_sum",
            "all_credits_charge_sum",
            "active_credits_amount_sum",
            "reg_payments_count",
            "payouts",
            "active_payouts",
            "active_extensions",
            "current_paid_payments",
            "loyalty_points",
        ],
        "audit_and_flags": [
            "created",
            "modified",
            "modified_by_customer",
            "last_login_time",
            "ip",
            "api_user_id",
            "important",
            "force_change",
            "sms_enabled",
            "language",
            "documents_attached",
            "category_changed",
        ],
    },
}


def read_sample(path: Path, limit: int) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        rows = [row for _, row in zip(range(limit), reader)]
    return list(reader.fieldnames or []), rows


def value_profile(rows: list[dict[str, str]], columns: list[str]) -> list[dict[str, str | int]]:
    profiles = []
    for column in columns:
        values = [row.get(column, "") for row in rows]
        meaningful = [value for value in values if value not in EMPTY_VALUES]
        sample_values = []
        for value in meaningful:
            trimmed = value.replace("\n", " ")[:70]
            if trimmed not in sample_values:
                sample_values.append(trimmed)
            if len(sample_values) == 3:
                break
        profiles.append(
            {
                "column": column,
                "filled": len(meaningful),
                "unique": len(set(values)),
                "examples": "; ".join(sample_values),
            }
        )
    return profiles


def classify_columns(table_name: str, columns: list[str]) -> dict[str, list[str]]:
    if table_name not in COLUMN_GROUPS:
        id_columns = [
            column
            for column in columns
            if column == "id"
            or column.endswith("_id")
            or column in {"customer_id", "credit_id", "application_id"}
        ]
        date_columns = [
            column for column in columns if any(token in column.lower() for token in DATE_TOKENS)
        ]
        assigned = set(id_columns) | set(date_columns)
        return {
            "identifiers_and_links": id_columns,
            "date_time_and_lifecycle": date_columns,
            "other_fields": [column for column in columns if column not in assigned],
        }

    grouped = {}
    assigned = set()
    for group_name, group_columns in COLUMN_GROUPS[table_name].items():
        present = [column for column in group_columns if column in columns]
        grouped[group_name] = present
        assigned.update(present)
    grouped["other_or_low_level_system_fields"] = [column for column in columns if column not in assigned]
    return grouped


def write_markdown(
    output_path: Path,
    data_dir: Path,
    sample_size: int,
    summaries: dict[str, tuple[list[str], list[dict[str, str]]]],
) -> None:
    lines = [
        "# Credit Platform Data Sample Overview",
        "",
        f"Data directory: `{data_dir}`",
        f"Sample size per file: first `{sample_size}` data rows",
        "",
        "This report is based on column names and sampled values only. The raw CSV files stay outside the repository.",
        "",
    ]

    for table_name, (columns, rows) in summaries.items():
        lines.extend(
            [
                f"## `{FILES[table_name]}`",
                "",
                f"- Rows inspected: `{len(rows)}`",
                f"- Columns: `{len(columns)}`",
                "",
                "### Business meaning",
                "",
            ]
        )
        for note in TABLE_NOTES[table_name]:
            lines.extend([note, ""])

        lines.extend(["### Column groups", ""])
        for group_name, group_columns in classify_columns(table_name, columns).items():
            if not group_columns:
                continue
            lines.append(f"- `{group_name}`: {', '.join(f'`{column}`' for column in group_columns)}")
        lines.append("")

        lines.extend(["### Sample value profile", "", "| column | filled in sample | unique in sample | examples |", "|---|---:|---:|---|"])
        profiles = value_profile(rows, columns)
        for profile in profiles:
            examples = str(profile["examples"]).replace("|", "\\|")
            lines.append(
                f"| `{profile['column']}` | {profile['filled']}/{len(rows)} | {profile['unique']} | {examples} |"
            )
        lines.append("")

        top_fields = Counter()
        for column in columns:
            for token in column.split("_"):
                if token:
                    top_fields[token] += 1
        common_tokens = ", ".join(f"`{token}` ({count})" for token, count in top_fields.most_common(12))
        lines.extend(["### Common naming tokens", "", common_tokens, ""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze sampled CSV exports from the credit platform.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Folder containing the CSV exports.")
    parser.add_argument("--sample-size", type=int, default=50, help="Number of data rows to inspect per CSV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Markdown output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = {}
    for table_name, filename in FILES.items():
        path = args.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing input file: {path}")
        summaries[table_name] = read_sample(path, args.sample_size)

    write_markdown(args.output, args.data_dir, args.sample_size, summaries)
    for table_name, (columns, rows) in summaries.items():
        print(f"{FILES[table_name]}: inspected {len(rows)} rows, {len(columns)} columns")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
