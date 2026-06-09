# 30-Day Final Outcome Model Results

## Setup

The training unit is one issued loan. This run uses only rows with `eligible_30d = 1`, meaning the loan remained observable beyond the 30-day landmark. Features include conservative static borrower/loan variables and `w30d_*` window summary variables only. Terminal dates, final debt/delay fields, 60-day variables, and 90-day variables are excluded.

The sample is split by stratified random sampling into train, validation, and test sets with an approximate 60/20/20 allocation within each final-outcome class.

## Split Distribution

| Split | Class | Loans |
|---|---|---:|
| train | Clean Paid Off | 2658 |
| train | Paid Off After Delinquency | 4818 |
| train | Written Off | 16 |
| train | Sold | 238 |
| train | Other Terminal / Special Closure | 5 |
| validation | Clean Paid Off | 886 |
| validation | Paid Off After Delinquency | 1606 |
| validation | Written Off | 5 |
| validation | Sold | 79 |
| validation | Other Terminal / Special Closure | 1 |
| test | Clean Paid Off | 886 |
| test | Paid Off After Delinquency | 1606 |
| test | Written Off | 7 |
| test | Sold | 81 |
| test | Other Terminal / Special Closure | 3 |

## Metrics

| Model | Split | Accuracy | Macro F1 | Weighted F1 | Log loss |
|---|---|---:|---:|---:|---:|
| Multinomial logistic regression | validation | 0.7070 | 0.6290 | 0.7200 | 0.6890 |
| Multinomial logistic regression | test | 0.7143 | 0.5650 | 0.7261 | 0.7043 |
| Random forest | validation | 0.7610 | 0.6598 | 0.7621 | 0.4978 |
| Random forest | test | 0.7708 | 0.6739 | 0.7702 | 0.4994 |

## Test Confusion Matrix: Multinomial Logistic Regression

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 779 | 80 | 1 | 22 | 4 |
| Paid Off After Delinquency | 445 | 987 | 6 | 157 | 11 |
| Written Off | 0 | 2 | 3 | 0 | 2 |
| Sold | 1 | 3 | 1 | 76 | 0 |
| Other | 2 | 1 | 0 | 0 | 0 |

## Test Per-Class Metrics: Multinomial Logistic Regression

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 886 | 0.6349 | 0.8792 | 0.7373 |
| Paid Off After Delinquency | 1606 | 0.9199 | 0.6146 | 0.7368 |
| Written Off | 7 | 0.2727 | 0.4286 | 0.3333 |
| Sold | 81 | 0.2980 | 0.9383 | 0.4524 |
| Other Terminal / Special Closure | 3 | 0.0000 | 0.0000 |  |

## Test Confusion Matrix: Random Forest

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 700 | 183 | 1 | 2 | 0 |
| Paid Off After Delinquency | 324 | 1257 | 0 | 25 | 0 |
| Written Off | 0 | 7 | 0 | 0 | 0 |
| Sold | 1 | 46 | 0 | 34 | 0 |
| Other | 1 | 2 | 0 | 0 | 0 |

## Test Per-Class Metrics: Random Forest

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 886 | 0.6823 | 0.7901 | 0.7322 |
| Paid Off After Delinquency | 1606 | 0.8408 | 0.7827 | 0.8107 |
| Written Off | 7 | 0.0000 | 0.0000 |  |
| Sold | 81 | 0.5574 | 0.4198 | 0.4789 |
| Other Terminal / Special Closure | 3 |  | 0.0000 |  |

## Random Forest Feature Importance

| Rank | Feature | Mean decrease accuracy |
|---:|---|---:|
| 1 | `w30d_late_fee_paid` | 36.9074 |
| 2 | `customer_category_id` | 33.5520 |
| 3 | `w30d_principal_paid` | 29.8144 |
| 4 | `w30d_days_since_last_payment` | 27.6066 |
| 5 | `w30d_principal_recovery_rate` | 27.0318 |
| 6 | `w30d_days_to_first_payment` | 26.6962 |
| 7 | `w30d_payment_total` | 25.4461 |
| 8 | `w30d_payment_gap` | 20.2924 |
| 9 | `w30d_interest_paid` | 20.0059 |
| 10 | `w30d_admin_fee_paid` | 19.9544 |
| 11 | `loan_administrative_fee` | 17.8701 |
| 12 | `loan_amount` | 17.7556 |
| 13 | `contract_charge_rate` | 16.7619 |
| 14 | `loan_interest` | 16.7094 |
| 15 | `loan_charge` | 15.4677 |
| 16 | `contract_charge_per_day` | 15.2768 |
| 17 | `contract_amount_per_day` | 14.6048 |
| 18 | `loan_apr` | 14.5229 |
| 19 | `loan_period` | 13.6636 |
| 20 | `w30d_total_paid_to_due_ratio` | 13.0056 |
| 21 | `w30d_scheduled_due_principal` | 11.5521 |
| 22 | `w30d_days_to_first_payment_missing` | 10.4407 |
| 23 | `w30d_payment_count` | 10.3253 |
| 24 | `customer_age_at_loan_days` | 9.9954 |
| 25 | `w30d_days_since_last_payment_missing` | 9.8900 |

## Caveats

- `Written Off` and `Other Terminal / Special Closure` have very small sample sizes, so their per-class metrics are unstable.
- This is a first-pass baseline run, not a tuned production model.
- The random forest is used as the first tree-based baseline because gradient boosting libraries are not currently available in the local runtime.

