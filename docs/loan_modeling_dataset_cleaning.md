# Loan Modeling Dataset Cleaning

## Purpose

This dataset is prepared for final-outcome prediction at the loan level. Each row is one issued loan, not one borrower. Borrower-level variables may therefore repeat across multiple loan rows.

## Final Outcome Labels

The five mutually exclusive terminal labels are assigned in priority order:

1. `Sold`: `sold` has a valid date.
2. `Written Off`: `writeoff` or `writeoff_a` is positive, excluding loans already labelled as sold.
3. `Clean Paid Off`: `paid` has a valid date, final debt is zero, `max_delay = 0`, and `late_fee = 0`.
4. `Paid Off After Delinquency`: `paid` has a valid date and final debt is zero, but delay or fee signals exist.
5. `Other Terminal / Special Closure`: terminal or special closure signals exist but do not fit the four main labels.

Unfinished loans are excluded from the training dataset because their final outcome is right-censored.

## Output

- Dataset: `data/modeling/loan_modeling_dataset.csv`
- Rows: 18,851
- Columns: 116

## Full Issued-Loan Status Before Filtering

| Status | Loans |
|---|---:|
| Clean Paid Off | 10,318 |
| Paid Off After Delinquency | 8,097 |
| Unfinished / Censored | 2,191 |
| Sold | 398 |
| Written Off | 28 |
| Other Terminal / Special Closure | 10 |

## Label Distribution In Cleaned Dataset

| Final outcome | Loans |
|---|---:|
| Clean Paid Off | 10,318 |
| Paid Off After Delinquency | 8,097 |
| Sold | 398 |
| Written Off | 28 |
| Other Terminal / Special Closure | 10 |

## Landmark Eligibility

A loan is eligible for a landmark model only if its terminal date is later than the landmark day. For example, a 45-day loan is eligible for the 30-day model, but not for the 60-day or 90-day model.

| Landmark | Eligible terminal loans |
|---|---:|
| 30 days | 12,895 |
| 60 days | 9,057 |
| 90 days | 7,254 |

## Window Features

For each of 30/60/90 days, the script computes cumulative repayment, scheduled due, payment-gap, recovery-rate, and extension-event features using only events dated on or before the landmark day.

## Processing Notes

### payment_allocations

- `used_allocation_rows`: 120,042
- `payment_before_created`: 61

### schedules

- `used_schedule_rows`: 275,071

### extensions

- `used_extension_rows`: 4,662

## Leakage Notes

The cleaning script keeps a conservative set of borrower variables such as age, gender, income, work status, home status, region, and customer registration date. It intentionally does not include customer-master aggregate fields such as `credits_paid`, `last_payment_date`, or `all_paid` as default features because those fields are likely measured at export time and may contain post-outcome information.
