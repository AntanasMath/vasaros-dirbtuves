#!/usr/bin/env python3
"""Inspect whether the combined export contains clean joined data.

The script streams the large CSV and compares its headers and key fields with
the normalized export tables. It is intended for EDA documentation, not for
building an analytical dataset from the combined file.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


DEFAULT_DATA_DIR = Path("/Users/yil1/Downloads/datasets CO-KTU workshop")
DEFAULT_OUTPUT = Path("docs/combined_export_inspection.md")
COMBINED_FILE = "export (tables combined).csv"

SOURCE_FILES = [
    "export_customers.csv",
    "export_credits.csv",
    "export_credits_rejected.csv",
    "export_credits_decisions.csv",
    "export_credit_ext_requests.csv",
    "export_creditline_paydays.csv",
    "credits_schedules_all.csv",
]


def read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return next(csv.reader(handle))


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def read_key_set(path: Path, key: str) -> set[str]:
    values = set()
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            value = row.get(key)
            if value:
                values.add(value)
    return values


def inspect_combined(data_dir: Path) -> dict:
    headers = {name: read_header(data_dir / name) for name in SOURCE_FILES + [COMBINED_FILE]}
    combined_header = headers[COMBINED_FILE]
    source_union = set().union(*(set(headers[name]) for name in SOURCE_FILES))

    credit_ids = read_key_set(data_dir / "export_credits.csv", "id")
    rejected_ids = read_key_set(data_dir / "export_credits_rejected.csv", "id")

    counts = Counter()
    unique = {key: set() for key in ["customer_id", "id", "cd_credit_id", "credit_id", "cp_credit_id"]}
    patterns = Counter()
    pair_checks = Counter()
    samples: dict[str, dict[str, str]] = {}

    sample_fields = [
        "customer_id",
        "id",
        "cd_credit_id",
        "credit_id",
        "cp_credit_id",
        "created",
        "amount",
        "charge",
        "paid",
        "rejection_date",
        "request_date",
        "complete_date",
    ]

    with (data_dir / COMBINED_FILE).open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            counts["rows"] += 1
            has_credit_like_id = bool(row.get("id"))
            has_rejected = bool(row.get("rejection_date") or row.get("admin_name") or row.get("offer"))
            has_decision = bool(row.get("cd_credit_id") or row.get("cd_decision_info"))
            has_payday = bool(row.get("cp_payday_id") or row.get("cp_credit_id"))
            has_extension = bool(row.get("credit_id") or row.get("request_date") or row.get("complete_date"))
            pattern = (has_credit_like_id, has_rejected, has_decision, has_payday, has_extension)
            patterns[pattern] += 1

            for key in unique:
                value = row.get(key)
                if value:
                    unique[key].add(value)

            main_id = row.get("id") or ""
            decision_credit_id = row.get("cd_credit_id") or ""
            extension_credit_id = row.get("credit_id") or ""
            payday_credit_id = row.get("cp_credit_id") or ""

            if main_id and decision_credit_id:
                label = "id_equals_cd_credit_id" if main_id == decision_credit_id else "id_differs_from_cd_credit_id"
                pair_checks[label] += 1
                samples.setdefault(label, {field: row.get(field, "") for field in sample_fields})
            if main_id and extension_credit_id:
                label = "id_equals_extension_credit_id" if main_id == extension_credit_id else "id_differs_from_extension_credit_id"
                pair_checks[label] += 1
                samples.setdefault(label, {field: row.get(field, "") for field in sample_fields})
            if main_id and payday_credit_id:
                label = "id_equals_payday_credit_id" if main_id == payday_credit_id else "id_differs_from_payday_credit_id"
                pair_checks[label] += 1
                samples.setdefault(label, {field: row.get(field, "") for field in sample_fields})

    combined_id_values = unique["id"]
    return {
        "headers": headers,
        "combined_rows": counts["rows"],
        "combined_size_mb": (data_dir / COMBINED_FILE).stat().st_size / (1024 * 1024),
        "combined_cols": len(combined_header),
        "combined_unique_cols": len(set(combined_header)),
        "source_unique_cols": len(source_union),
        "combined_not_source": sorted(set(combined_header) - source_union),
        "source_not_combined": sorted(source_union - set(combined_header)),
        "overlap_by_file": {
            name: {
                "cols": len(headers[name]),
                "overlap": len(set(headers[name]) & set(combined_header)),
                "missing": sorted(set(headers[name]) - set(combined_header)),
            }
            for name in SOURCE_FILES
        },
        "patterns": patterns,
        "unique_counts": {key: len(values) for key, values in unique.items()},
        "combined_id_in_rejected": len(combined_id_values & rejected_ids),
        "combined_id_in_credits": len(combined_id_values & credit_ids),
        "combined_id_in_neither": len(combined_id_values - rejected_ids - credit_ids),
        "cd_credit_id_in_credits": len(unique["cd_credit_id"] & credit_ids),
        "extension_credit_id_in_credits": len(unique["credit_id"] & credit_ids),
        "pair_checks": pair_checks,
        "samples": samples,
    }


def format_pattern(pattern: tuple[bool, bool, bool, bool, bool]) -> str:
    labels = ["id", "rejected", "decision", "payday", "extension"]
    return ", ".join(label for label, present in zip(labels, pattern) if present) or "none"


def write_markdown(result: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Combined Export Inspection",
        "",
        "## Conclusion",
        "",
        "`export (tables combined).csv` is not a CSV file containing multiple separate tables. It is one very wide denormalized export. It appears to combine columns from several normalized source tables, but it should not be treated as a clean loan-level analytical table.",
        "",
        "The file does not appear to add materially new variables beyond renamed conflict columns such as `cd_credit_id`, `cd_decision_info`, `cp_payday_id`, and `cp_credit_id`. These names look like prefixes added to avoid collisions between source tables.",
        "",
        "The main practical issue is that rows mix records from different one-to-many tables for the same customer. For example, the combined `id` column matches rejected-application IDs, while `cd_credit_id` and extension `credit_id` refer to issued-credit IDs. In many rows these IDs differ, so fields in one row do not necessarily describe the same loan.",
        "",
        "## File Shape",
        "",
        f"- Size: {result['combined_size_mb']:.1f} MB",
        f"- Data rows: {result['combined_rows']:,}",
        f"- Columns: {result['combined_cols']:,}",
        f"- Unique column names: {result['combined_unique_cols']:,}",
        f"- Unique source column names across known exports: {result['source_unique_cols']:,}",
        "",
        "## Header Coverage",
        "",
        "| Source file | Source columns | Columns also present in combined | Missing from combined |",
        "|---|---:|---:|---|",
    ]
    for name, item in result["overlap_by_file"].items():
        missing = ", ".join(item["missing"]) if item["missing"] else "-"
        lines.append(f"| `{name}` | {item['cols']:,} | {item['overlap']:,} | {missing} |")

    lines.extend(
        [
            "",
            f"- Combined-only column names: {', '.join('`' + x + '`' for x in result['combined_not_source']) or '-'}",
            f"- Source-only column names missing from combined: {', '.join('`' + x + '`' for x in result['source_not_combined']) or '-'}",
            "",
            "## Key Identity Checks",
            "",
            f"- Unique non-empty `customer_id` values in combined: {result['unique_counts']['customer_id']:,}",
            f"- Unique non-empty combined `id` values: {result['unique_counts']['id']:,}",
            f"- Combined `id` values found in `export_credits_rejected.id`: {result['combined_id_in_rejected']:,}",
            f"- Combined `id` values found in `export_credits.id`: {result['combined_id_in_credits']:,}",
            f"- Combined `id` values found in neither source ID set: {result['combined_id_in_neither']:,}",
            f"- Unique `cd_credit_id` values: {result['unique_counts']['cd_credit_id']:,}; found in `export_credits.id`: {result['cd_credit_id_in_credits']:,}",
            f"- Unique extension `credit_id` values: {result['unique_counts']['credit_id']:,}; found in `export_credits.id`: {result['extension_credit_id_in_credits']:,}",
            "",
            "## Row Pattern Counts",
            "",
            "Pattern columns are interpreted as: `id`, rejected fields, decision fields, payday fields, extension fields.",
            "",
            "| Present field groups | Rows |",
            "|---|---:|",
        ]
    )
    for pattern, count in result["patterns"].most_common():
        lines.append(f"| {format_pattern(pattern)} | {count:,} |")

    lines.extend(
        [
            "",
            "## Same-Row ID Consistency",
            "",
            "| Check | Rows |",
            "|---|---:|",
        ]
    )
    for key, count in result["pair_checks"].most_common():
        lines.append(f"| `{key}` | {count:,} |")

    lines.extend(["", "## Example Mismatch", ""])
    for key, sample in result["samples"].items():
        if "differs" not in key:
            continue
        lines.append(f"### `{key}`")
        lines.append("")
        for field, value in sample.items():
            lines.append(f"- `{field}`: `{value}`")
        lines.append("")

    lines.extend(
        [
            "## Recommendation",
            "",
            "Use the normalized files for analysis. Treat `export (tables combined).csv` only as a rough convenience export for browsing customer/application context. Do not use it to compute loan-level portfolio counts, profitability, repayment status, or extension histories unless the source join logic is provided and validated.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = inspect_combined(args.data_dir)
    write_markdown(result, args.output)
    print(f"Rows: {result['combined_rows']:,}")
    print(f"Columns: {result['combined_cols']:,}")
    print(f"Combined id values in rejected IDs: {result['combined_id_in_rejected']:,}")
    print(f"Combined id values in issued-credit IDs: {result['combined_id_in_credits']:,}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
