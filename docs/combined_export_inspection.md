# Combined Export Inspection

## Conclusion

`export (tables combined).csv` is not a CSV file containing multiple separate tables. It is one very wide denormalized export. It appears to combine columns from several normalized source tables, but it should not be treated as a clean loan-level analytical table.

The file does not appear to add materially new variables beyond renamed conflict columns such as `cd_credit_id`, `cd_decision_info`, `cp_payday_id`, and `cp_credit_id`. These names look like prefixes added to avoid collisions between source tables.

The main practical issue is that rows mix records from different one-to-many tables for the same customer. For example, the combined `id` column matches rejected-application IDs, while `cd_credit_id` and extension `credit_id` refer to issued-credit IDs. In many rows these IDs differ, so fields in one row do not necessarily describe the same loan.

## File Shape

- Size: 648.1 MB
- Data rows: 76,000
- Columns: 357
- Unique column names: 357
- Unique source column names across known exports: 375

## Header Coverage

| Source file | Source columns | Columns also present in combined | Missing from combined |
|---|---:|---:|---|
| `export_customers.csv` | 170 | 170 | - |
| `export_credits.csv` | 179 | 179 | - |
| `export_credits_rejected.csv` | 27 | 27 | - |
| `export_credits_decisions.csv` | 7 | 1 | approve_date, approver_id, confirm_date, confirmer_id, decision_info, info |
| `export_credit_ext_requests.csv` | 26 | 26 | - |
| `export_creditline_paydays.csv` | 14 | 9 | active, create_date, date, protection, reduction |
| `credits_schedules_all.csv` | 14 | 3 | paid_administrative_fee, paid_amount, paid_interest, pay_administrative_fee, pay_amount, pay_date, pay_delay, pay_interest, pay_number, pay_status, pay_sum |

- Combined-only column names: `cd_credit_id`, `cd_decision_info`, `cp_credit_id`, `cp_payday_id`
- Source-only column names missing from combined: `active`, `approve_date`, `approver_id`, `confirm_date`, `confirmer_id`, `create_date`, `date`, `decision_info`, `info`, `paid_administrative_fee`, `paid_amount`, `paid_interest`, `pay_administrative_fee`, `pay_amount`, `pay_date`, `pay_delay`, `pay_interest`, `pay_number`, `pay_status`, `pay_sum`, `protection`, `reduction`

## Key Identity Checks

- Unique non-empty `customer_id` values in combined: 5,504
- Unique non-empty combined `id` values: 15,978
- Combined `id` values found in `export_credits_rejected.id`: 15,978
- Combined `id` values found in `export_credits.id`: 0
- Combined `id` values found in neither source ID set: 0
- Unique `cd_credit_id` values: 4,560; found in `export_credits.id`: 4,560
- Unique extension `credit_id` values: 1,423; found in `export_credits.id`: 1,422

## Row Pattern Counts

Pattern columns are interpreted as: `id`, rejected fields, decision fields, payday fields, extension fields.

| Present field groups | Rows |
|---|---:|
| id, rejected, decision | 24,090 |
| id, rejected, extension | 23,431 |
| id, rejected, decision, extension | 15,640 |
| id, rejected | 8,576 |
| extension | 1,533 |
| none | 1,499 |
| decision | 598 |
| decision, extension | 355 |
| id, rejected, decision, payday, extension | 144 |
| id, rejected, decision, payday | 134 |

## Same-Row ID Consistency

| Check | Rows |
|---|---:|
| `id_differs_from_cd_credit_id` | 40,008 |
| `id_differs_from_extension_credit_id` | 39,215 |
| `id_differs_from_payday_credit_id` | 278 |

## Example Mismatch

### `id_differs_from_cd_credit_id`

- `customer_id`: `10481`
- `id`: `150360`
- `cd_credit_id`: `178356`
- `credit_id`: ``
- `cp_credit_id`: ``
- `created`: `2021-11-03 14:40:19`
- `amount`: `1000.00`
- `charge`: `999.20`
- `paid`: `2024-11-11 10:04:00`
- `rejection_date`: `2021-11-03 14:41:33`
- `request_date`: ``
- `complete_date`: ``

### `id_differs_from_extension_credit_id`

- `customer_id`: `45726`
- `id`: `261308`
- `cd_credit_id`: `110158`
- `credit_id`: `111713`
- `cp_credit_id`: ``
- `created`: `2025-10-09 19:28:45`
- `amount`: `900.00`
- `charge`: `526.56`
- `paid`: `2020-01-24 17:07:00`
- `rejection_date`: `2025-10-10 08:16:00`
- `request_date`: `2020-02-24 08:45:11`
- `complete_date`: `2020-02-24 08:45:11`

### `id_differs_from_payday_credit_id`

- `customer_id`: `51759`
- `id`: `129898`
- `cd_credit_id`: `201546`
- `credit_id`: ``
- `cp_credit_id`: `201546`
- `created`: `2020-11-04 14:34:56`
- `amount`: `200.00`
- `charge`: `200.00`
- `paid`: `0000-00-00 00:00:00`
- `rejection_date`: `2020-11-04 14:39:34`
- `request_date`: ``
- `complete_date`: ``

## Recommendation

Use the normalized files for analysis. Treat `export (tables combined).csv` only as a rough convenience export for browsing customer/application context. Do not use it to compute loan-level portfolio counts, profitability, repayment status, or extension histories unless the source join logic is provided and validated.
