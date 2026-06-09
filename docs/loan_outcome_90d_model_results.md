# 90-Day Final Outcome Model Results

## Setup

The training unit is one issued loan. This run uses only rows with `eligible_90d = 1`, meaning the loan remained observable beyond the 90-day landmark. Features include conservative static borrower/loan variables and `w90d_*` window summary variables only. Terminal dates, final debt/delay fields, and other landmark-window variables are excluded.

The sample is split by stratified random sampling into train, validation, and test sets with an approximate 60/20/20 allocation within each final-outcome class.

## Split Distribution

| Split | Class | Loans |
|---|---|---:|
| train | Clean Paid Off | 1138 |
| train | Paid Off After Delinquency | 2952 |
| train | Written Off | 16 |
| train | Sold | 238 |
| train | Other Terminal / Special Closure | 5 |
| validation | Clean Paid Off | 379 |
| validation | Paid Off After Delinquency | 984 |
| validation | Written Off | 5 |
| validation | Sold | 79 |
| validation | Other Terminal / Special Closure | 1 |
| test | Clean Paid Off | 381 |
| test | Paid Off After Delinquency | 985 |
| test | Written Off | 7 |
| test | Sold | 81 |
| test | Other Terminal / Special Closure | 3 |

## Metrics

| Model | Split | Accuracy | Macro F1 | Weighted F1 | Log loss |
|---|---|---:|---:|---:|---:|
| Multinomial logistic regression | validation | 0.7500 | 0.7026 | 0.7602 | 0.7230 |
| Multinomial logistic regression | test | 0.7591 | 0.6221 | 0.7696 | 0.7403 |
| Random forest | validation | 0.7997 | 0.7206 | 0.7956 | 0.4279 |
| Random forest | test | 0.7927 | 0.5717 | 0.7866 | 0.4479 |

## Test Confusion Matrix: Multinomial Logistic Regression

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 365 | 9 | 3 | 4 | 0 |
| Paid Off After Delinquency | 214 | 667 | 3 | 98 | 3 |
| Written Off | 0 | 4 | 3 | 0 | 0 |
| Sold | 2 | 8 | 0 | 71 | 0 |
| Other | 2 | 1 | 0 | 0 | 0 |

## Test Per-Class Metrics: Multinomial Logistic Regression

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 381 | 0.6261 | 0.9580 | 0.7573 |
| Paid Off After Delinquency | 985 | 0.9681 | 0.6772 | 0.7969 |
| Written Off | 7 | 0.3333 | 0.4286 | 0.3750 |
| Sold | 81 | 0.4104 | 0.8765 | 0.5591 |
| Other Terminal / Special Closure | 3 | 0.0000 | 0.0000 |  |

## Test Confusion Matrix: Random Forest

| Actual \ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |
|---|---:|---:|---:|---:|---:|
| Clean Paid Off | 258 | 123 | 0 | 0 | 0 |
| Paid Off After Delinquency | 98 | 862 | 0 | 25 | 0 |
| Written Off | 0 | 6 | 1 | 0 | 0 |
| Sold | 0 | 47 | 0 | 34 | 0 |
| Other | 0 | 3 | 0 | 0 | 0 |

## Test Per-Class Metrics: Random Forest

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Clean Paid Off | 381 | 0.7247 | 0.6772 | 0.7001 |
| Paid Off After Delinquency | 985 | 0.8280 | 0.8751 | 0.8509 |
| Written Off | 7 | 1.0000 | 0.1429 | 0.2500 |
| Sold | 81 | 0.5763 | 0.4198 | 0.4857 |
| Other Terminal / Special Closure | 3 |  | 0.0000 |  |

## Random Forest Feature Importance

| Rank | Feature | Mean decrease accuracy |
|---:|---|---:|
| 1 | `w90d_late_fee_paid` | 68.9873 |
| 2 | `customer_category_id` | 38.6442 |
| 3 | `w90d_days_to_first_payment` | 32.6290 |
| 4 | `w90d_principal_recovery_rate` | 28.4603 |
| 5 | `w90d_payment_gap` | 28.3223 |
| 6 | `w90d_payment_count` | 24.6746 |
| 7 | `w90d_total_paid_to_due_ratio` | 23.4655 |
| 8 | `w90d_principal_paid` | 23.1290 |
| 9 | `w90d_days_since_last_payment` | 20.1687 |
| 10 | `w90d_admin_fee_paid` | 19.3569 |
| 11 | `w90d_interest_paid` | 18.7675 |
| 12 | `w90d_payment_total` | 17.7745 |
| 13 | `loan_charge` | 15.9334 |
| 14 | `contract_charge_rate` | 15.7440 |
| 15 | `loan_administrative_fee` | 15.1425 |
| 16 | `loan_created_year` | 14.8410 |
| 17 | `loan_apr` | 12.9635 |
| 18 | `contract_amount_per_day` | 12.8589 |
| 19 | `loan_amount` | 12.7106 |
| 20 | `w90d_scheduled_due_principal` | 12.4650 |
| 21 | `loan_interest` | 12.2280 |
| 22 | `contract_charge_per_day` | 11.8963 |
| 23 | `loan_period` | 11.2388 |
| 24 | `w90d_scheduled_due_interest` | 11.0643 |
| 25 | `w90d_scheduled_due_total` | 10.7599 |

## Caveats

- `Written Off` and `Other Terminal / Special Closure` have very small sample sizes, so their per-class metrics are unstable.
- This is a first-pass baseline run, not a tuned production model.
- The random forest is used as the first tree-based baseline because gradient boosting libraries are not currently available in the local runtime.

