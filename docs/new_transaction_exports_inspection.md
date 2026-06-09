# New Transaction Export Inspection

## Main Conclusion

The new files do contain actual cash-flow information. The strongest repayment-history source is the pair `payment_202606081636.csv` and `payments_credits_202606081635.csv`: the first table records incoming payment events and timestamps, while the second table allocates each payment to a credit and splits the paid amount into principal, interest, administrative fee, late fee, penalty, and related components.

For loan-level repayment panel construction, use `payment.id = payments_credits.payment_id` and then use `payments_credits.credit_id = export_credits.id`. The payment date should come from `payment.payment_created`; the component amounts should come from `payments_credits_*` columns.

`payouts_202606081703.csv` appears to record outgoing disbursement/payout events. The two `sas_*` files record SAS risk scoring results at the credit and customer levels.

These files cover a broader historical universe than the 21,042 issued loans currently in `export_credits.csv`, so all analysis should explicitly filter to the research credit-id universe when needed.

## File Inventory

| File | Rows | Columns | Likely role |
|---|---:|---:|---|
| `payment_202606081636.csv` | 556,572 | 45 | Incoming payment events / receipts |
| `payments_credits_202606081635.csv` | 463,373 | 27 | Payment-to-credit allocation and component split |
| `payouts_202606081703.csv` | 21,619 | 31 | Outgoing disbursement / payout events |
| `sas_credits_results_202606081620.csv` | 109,980 | 10 | Credit-level SAS scoring result |
| `sas_results_202606081620.csv` | 10,627 | 14 | Customer-level SAS scoring result |

## Payment Events

- Unique payment IDs: 556,572
- Date range: 2009-12-20 to 2026-06-03
- Total `payment_amount`: 64,982,001.19 in reported currency units
- Non-zero payment rows: 556,571
- Unique payment credit IDs: 70,499
- Payment rows whose `credit_id` is in current `export_credits.id`: 154,658
- Unique payment customers: 50,783; in current customer master: 20,136
- Currency distribution: EUR: 528,970, LTL: 27,493, (blank): 109
- Ignored flag distribution: 0: 522,215, 1: 34,357
- Ignored flag amount split: 0: 63,501,359.96, 1: 1,480,641.23
- Registration flag distribution: 0: 493,646, 1: 62,926
- Registration flag amount split: 0: 64,975,189.08, 1: 6,812.11
- Extension flag distribution: 0: 527,870, 1: 28,702
- Extension flag amount split: 0: 64,302,657.60, 1: 679,343.59
- Years: 2018: 63,836, 2020: 62,778, 2019: 61,586, 2021: 59,625, 2022: 54,248, 2023: 48,894, 2024: 48,220, 2017: 47,855, 2025: 47,746, 2026: 18,297, 2016: 11,110, 2014: 6,512, 2013: 6,407, 2011: 5,683, 2012: 5,247, 2015: 4,881, 2010: 3,583, 2009: 63

## Payment-Credit Allocations

- Allocation rows: 463,373
- Unique allocation IDs: 451,950; duplicate non-empty ID rows: 11,423
- Unique `payment_id`: 451,862
- Allocation rows with `payment_id` found in payment table: 463,373
- Unique allocation credit IDs: 86,696
- Allocation rows whose `credit_id` is in current `export_credits.id`: 144,008
- Total allocated components across all records: 63,734,856.35 in reported currency units
- Component sums across all records: `amount` currency units 48,807,175.04; `charge` currency units 683,385.22; `administrative_fee` currency units 4,576,091.02; `cinterest` currency units 232,067.99; `interest` currency units 9,264,944.59; `late_fee` currency units 125,029.07; `penalty` currency units 46,163.42
- Currency distribution: EUR: 448,974, LTL: 14,399

### Coverage of the 21,042 Issued-Loan Research Scope

- Issued loans in `export_credits.csv`: 21,042
- Issued loans with at least one allocation row: 20,403
- Issued loans without allocation rows: 639
- Completed loans in `export_credits.csv` with allocation rows: 18,438 of 18,438
- Ongoing/unpaid loans with allocation rows: 1,965
- Issued-scope allocation rows: 144,008
- Issued-scope allocation date range: 2020-01-10 to 2026-06-03
- Issued-scope allocated total: EUR 25,934,642.50
- Issued-scope component sums: `amount` EUR 20,129,310.12; `charge` EUR 20,937.70; `administrative_fee` EUR 1,942,440.24; `cinterest` EUR 41,670.99; `interest` EUR 3,767,169.29; `late_fee` EUR 33,114.16
- For issued-scope rows, payment-table `credit_id` matched allocation `credit_id` in 143,997 rows and differed in 11 rows.
- Issued-scope payment years: 2024: 28,322, 2023: 28,017, 2022: 25,504, 2025: 25,371, 2021: 20,328, 2020: 8,962, 2026: 7,504

## Payouts

- Payout rows: 21,619
- Date range: 2018-11-07 to 2026-06-03
- Total payout `amount`: 22,546,819.15 in reported currency units
- Unique payout credit IDs: 16,068
- Payout rows whose `credit_id` is in current `export_credits.id`: 10,531
- Payout status distribution: 1: 21,602, 2: 17
- Payout type distribution: 1: 16,284, 0: 5,335
- Confirmed payout rows: 21,521
- Issued-scope payout rows: 10,531
- Issued loans with payout rows: 6,130
- Issued-scope payout amount: EUR 10,397,490.30
- Issued-scope payout date range: 2020-01-10 to 2026-06-02

## SAS Scoring Files

### Credit-Level SAS Results

- Rows: 109,980
- Unique credit IDs: 109,980
- Rows matched to current `export_credits.id`: 9,391
- Matched issued credit IDs: 9,391
- Time range: 2016-03-22 to 2025-01-21
- Score value distribution: (blank): 67,192, A: 36,394, B: 3,548, ERR: 2,770, C: 76
- Score summary: min -1960, median 0, max 729

### Customer-Level SAS Results

- Rows: 10,627
- Unique customer IDs: 10,627
- Rows matched to current `export_customers.customer_id`: 1,357
- Time range: 2016-04-25 to 2025-01-21
- Score value distribution: A: 8,883, B: 1,063, ERR: 635, C: 30, (blank): 15, Skipped: 1
- Score summary: min -1960, median 290, max 699

## Practical Use

For actual repayment analysis, build a transaction panel from `payments_credits_202606081635.csv` joined to `payment_202606081636.csv`. This can support monthly repayment curves, realized cash collections, paid principal/interest/fees, delinquency-recovery timing, and realized revenue analysis for the current 21,042-loan scope after filtering on `payments_credits.credit_id`.

For disbursement/cash-out analysis, use `payouts_202606081703.csv`, but validate why it covers fewer current issued credits than the payment allocation table before using it as the sole source of original principal disbursement.
