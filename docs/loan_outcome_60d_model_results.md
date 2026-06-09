# 60-Day Final Outcome Model Results

## Setup

The training unit is one issued loan. This run uses only rows with `eligible_60d = 1`, meaning the loan remained observable beyond the 60-day landmark. Features include conservative static borrower/loan variables and `w60d_*` window summary variables only. Terminal dates, final debt/delay fields, and other landmark-window variables are excluded.

The sample is split by stratified random sampling into train, validation, and test sets with an approximate 60/20/20 allocation within each final-outcome class.

## Split Distribution

| Split | Class | Loans |
|---|---|---:|
| train | Clean Paid Off | 1672 |
| train | Paid Off After Delinquency | 3500 |
| train | Written Off | 16 |
| train | Sold | 238 |
| train | Other Terminal / Special Closure | 5 |
| validation | Clean Paid Off | 557 |
| validation | Paid Off After Delinquency | 1166 |
| validation | Written Off | 5 |
| validation | Sold | 79 |
| validation | Other Terminal / Special Closure | 1 |
| test | Clean Paid Off | 559 |
| test | Paid Off After Delinquency | 1168 |
| test | Written Off | 7 |
| test | Sold | 81 |
| test | Other Terminal / Special Closure | 3 |

## Metrics

| Model | Split | Accuracy | Macro F1 | Weighted F1 | Log loss |
|---|---|---:|---:|---:|---:|
| Multinomial logistic regression | validation | 0.7412 | 0.5813 | 0.7511 | 0.6736 |
| Multinomial logistic regression | test | 0.7475 | 0.5534 | 0.7561 | 0.6150 |
| Random forest | validation | 0.7871 | 0.6133 | 0.7859 | 0.4519 |
| Random forest | test | 0.7959 | 0.6967 | 0.7926 | 0.4699 |

## Test Confusion Matrix: Multinomial Logistic Regression

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 517 | 35 | 1 | 5 | 1 |
| Paid Off After Delinquency | 286 | 761 | 2 | 115 | 4 |
| Written Off | 2 | 2 | 3 | 0 | 0 |
| Sold | 3 | 1 | 0 | 77 | 0 |
| Other | 1 | 1 | 0 | 0 | 1 |

## Test Per-Class Metrics: Multinomial Logistic Regression

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 559 | 0.6391 | 0.9249 | 0.7558 |
| Paid Off After Delinquency | 1168 | 0.9513 | 0.6515 | 0.7734 |
| Written Off | 7 | 0.5000 | 0.4286 | 0.4615 |
| Sold | 81 | 0.3909 | 0.9506 | 0.5540 |
| Other Terminal / Special Closure | 3 | 0.1667 | 0.3333 | 0.2222 |

## Test Confusion Matrix: Random Forest

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 441 | 118 | 0 | 0 | 0 |
| Paid Off After Delinquency | 178 | 973 | 0 | 17 | 0 |
| Written Off | 1 | 6 | 0 | 0 | 0 |
| Sold | 6 | 42 | 0 | 33 | 0 |
| Other | 2 | 1 | 0 | 0 | 0 |

## Test Per-Class Metrics: Random Forest

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 559 | 0.7022 | 0.7889 | 0.7430 |
| Paid Off After Delinquency | 1168 | 0.8535 | 0.8330 | 0.8432 |
| Written Off | 7 |  | 0.0000 |  |
| Sold | 81 | 0.6600 | 0.4074 | 0.5038 |
| Other Terminal / Special Closure | 3 |  | 0.0000 |  |

## Random Forest Feature Importance

| Rank | Feature | Mean decrease accuracy |
|---:|---|---:|
| 1 | `w60d_late_fee_paid` | 56.6689 |
| 2 | `w60d_days_to_first_payment` | 42.4564 |
| 3 | `customer_category_id` | 34.9206 |
| 4 | `w60d_principal_recovery_rate` | 30.2994 |
| 5 | `w60d_days_since_last_payment` | 27.6093 |
| 6 | `w60d_payment_gap` | 26.5494 |
| 7 | `w60d_payment_count` | 23.9343 |
| 8 | `w60d_principal_paid` | 23.8380 |
| 9 | `w60d_payment_total` | 20.8564 |
| 10 | `w60d_admin_fee_paid` | 20.2828 |
| 11 | `w60d_interest_paid` | 19.7624 |
| 12 | `w60d_total_paid_to_due_ratio` | 19.4378 |
| 13 | `loan_administrative_fee` | 16.4660 |
| 14 | `contract_charge_rate` | 15.1740 |
| 15 | `loan_charge` | 15.0299 |
| 16 | `contract_amount_per_day` | 14.8607 |
| 17 | `loan_interest` | 14.5960 |
| 18 | `contract_charge_per_day` | 14.3399 |
| 19 | `w60d_scheduled_due_interest` | 14.0414 |
| 20 | `loan_amount` | 13.6274 |
| 21 | `loan_apr` | 13.1472 |
| 22 | `loan_created_year` | 12.3146 |
| 23 | `w60d_scheduled_due_total` | 11.7395 |
| 24 | `loan_period` | 11.6140 |
| 25 | `w60d_scheduled_due_principal` | 10.9850 |

## Caveats

- `Written Off` and `Other Terminal / Special Closure` have very small sample sizes, so their per-class metrics are unstable.
- This is a first-pass baseline run, not a tuned production model.
- The random forest is used as the first tree-based baseline because gradient boosting libraries are not currently available in the local runtime.

