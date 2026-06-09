#!/usr/bin/env Rscript

# Monte Carlo SHAP-style explanation for the 60-day random-forest model.
# The computation is restricted to the most important RF features to keep the
# explanation tractable and focused.

suppressPackageStartupMessages({
  library(randomForest)
})

set.seed(20260609)

DATA_PATH <- "data/modeling/loan_modeling_dataset.csv"
MODEL_PATH <- "models/loan_outcome_60d_random_forest.rds"
TEST_PRED_PATH <- "data/modeling/loan_outcome_60d_random_forest_test_predictions.csv"
IMPORTANCE_PATH <- "data/modeling/loan_outcome_60d_random_forest_feature_importance.csv"
OUT_SUMMARY <- "data/modeling/loan_outcome_60d_random_forest_shap_summary.csv"
OUT_SAMPLE <- "data/modeling/loan_outcome_60d_random_forest_shap_sample.csv"

label_levels <- c(
  "Clean Paid Off",
  "Paid Off After Delinquency",
  "Written Off",
  "Sold",
  "Other Terminal / Special Closure"
)

static_features <- c(
  "loan_created_year",
  "loan_created_month",
  "contract_charge_rate",
  "contract_amount_per_day",
  "contract_charge_per_day",
  "loan_amount",
  "loan_period",
  "loan_charge",
  "loan_administrative_fee",
  "loan_interest",
  "loan_insurance",
  "loan_apr",
  "loan_schedule",
  "loan_product_id",
  "loan_creditline_mode",
  "loan_schedule_type",
  "customer_age",
  "customer_gender",
  "customer_income",
  "customer_dependents",
  "customer_home_status",
  "customer_work_status",
  "customer_work_activities",
  "customer_region",
  "customer_category_id",
  "customer_age_at_loan_days",
  "sas_credit_score",
  "sas_credit_score_value"
)

safe_num <- function(x) {
  suppressWarnings(as.numeric(x))
}

is_missing_text <- function(x) {
  is.na(x) | x == "" | x == "NA"
}

numeric_mode <- function(x) {
  tab <- sort(table(x), decreasing = TRUE)
  names(tab)[1]
}

apply_preprocess <- function(input_df, prep) {
  out <- data.frame(target_final_outcome = input_df$target_final_outcome)
  row.names(out) <- row.names(input_df)

  for (col in prep$numeric_features) {
    values <- safe_num(input_df[[col]])
    if (col %in% prep$missing_indicators) {
      out[[paste0(col, "_missing")]] <- as.integer(is.na(values))
    }
    values[is.na(values)] <- prep$numeric_medians[[col]]
    out[[col]] <- values
  }

  for (col in prep$categorical_features) {
    values <- input_df[[col]]
    values[is_missing_text(values)] <- "Missing"
    levels_allowed <- prep$categorical_levels[[col]]
    values[!(values %in% levels_allowed)] <- "Other"
    out[[col]] <- factor(values, levels = levels_allowed)
  }
  out$target_final_outcome <- factor(out$target_final_outcome, levels = prep$label_levels)
  out
}

make_baseline <- function(x_data) {
  baseline <- x_data[1, , drop = FALSE]
  for (col in names(x_data)) {
    if (is.factor(x_data[[col]])) {
      val <- numeric_mode(x_data[[col]])
      baseline[[col]] <- factor(val, levels = levels(x_data[[col]]))
    } else {
      val <- stats::median(x_data[[col]], na.rm = TRUE)
      if (!is.finite(val)) val <- 0
      baseline[[col]] <- val
    }
  }
  baseline
}

replicate_baseline <- function(baseline, n) {
  out <- baseline[rep(1, n), , drop = FALSE]
  row.names(out) <- NULL
  out
}

predict_prob <- function(model, newdata) {
  probs <- as.matrix(predict(model, newdata = newdata, type = "prob"))
  missing_cols <- setdiff(label_levels, colnames(probs))
  if (length(missing_cols) > 0) {
    add <- matrix(0, nrow = nrow(probs), ncol = length(missing_cols))
    colnames(add) <- missing_cols
    probs <- cbind(probs, add)
  }
  probs[, label_levels, drop = FALSE]
}

approx_shap_one <- function(model, baseline, x_interest, features, n_perm = 60) {
  p <- length(features)
  coalition_rows <- vector("list", n_perm * (p + 1))
  meta <- data.frame(perm = integer(), step = integer(), feature = character(), stringsAsFactors = FALSE)
  idx <- 1
  for (m in seq_len(n_perm)) {
    current <- baseline
    coalition_rows[[idx]] <- current
    meta <- rbind(meta, data.frame(perm = m, step = 0, feature = "", stringsAsFactors = FALSE))
    idx <- idx + 1
    for (feature in sample(features, p)) {
      current[[feature]] <- x_interest[[feature]]
      coalition_rows[[idx]] <- current
      meta <- rbind(meta, data.frame(perm = m, step = meta$step[nrow(meta)] + 1, feature = feature, stringsAsFactors = FALSE))
      idx <- idx + 1
    }
  }
  coalitions <- do.call(rbind, coalition_rows)
  probs <- predict_prob(model, coalitions)

  shap <- matrix(0, nrow = p, ncol = length(label_levels))
  row.names(shap) <- features
  colnames(shap) <- label_levels
  for (m in seq_len(n_perm)) {
    rows <- which(meta$perm == m)
    for (j in 2:length(rows)) {
      feature <- meta$feature[rows[j]]
      delta <- probs[rows[j], ] - probs[rows[j - 1], ]
      shap[feature, ] <- shap[feature, ] + delta
    }
  }
  shap / n_perm
}

saved <- readRDS(MODEL_PATH)
rf_model <- saved$model
prep <- saved$preprocess

raw <- read.csv(DATA_PATH, stringsAsFactors = FALSE, check.names = FALSE)
df <- raw[raw$eligible_60d == "1", , drop = FALSE]
df$target_final_outcome <- factor(df$target_final_outcome, levels = label_levels)

w60_features <- grep("^w60d_", names(df), value = TRUE)
feature_cols <- c(static_features, w60_features)
feature_cols <- feature_cols[feature_cols %in% names(df)]
df <- df[, c("credit_id", "customer_id", "target_final_outcome", feature_cols), drop = FALSE]

test_preds <- read.csv(TEST_PRED_PATH, stringsAsFactors = FALSE, check.names = FALSE)
test_ids <- test_preds$credit_id
test_raw <- df[df$credit_id %in% test_ids, , drop = FALSE]
test_raw <- test_raw[match(test_ids, test_raw$credit_id), , drop = FALSE]
processed <- apply_preprocess(test_raw, prep)
x_full <- processed[, setdiff(names(processed), "target_final_outcome"), drop = FALSE]

importance <- read.csv(IMPORTANCE_PATH, stringsAsFactors = FALSE)
top_features <- importance$feature[seq_len(min(20, nrow(importance)))]
top_features <- top_features[top_features %in% names(x_full)]

sample_ids <- c()
for (cls in label_levels) {
  cls_ids <- test_raw$credit_id[as.character(test_raw$target_final_outcome) == cls]
  if (length(cls_ids) > 0) {
    sample_ids <- c(sample_ids, sample(cls_ids, min(length(cls_ids), ifelse(cls %in% c("Written Off", "Other Terminal / Special Closure"), 7, 8))))
  }
}
sample_ids <- unique(sample_ids)
sample_idx <- match(sample_ids, test_raw$credit_id)
sample_idx <- sample_idx[!is.na(sample_idx)]

baseline <- make_baseline(x_full)

sample_rows <- list()
summary_rows <- list()
counter <- 1
cat("SHAP sample observations:", length(sample_idx), "\n")
cat("Features:", paste(top_features, collapse = ", "), "\n")
for (row_i in sample_idx) {
  x_interest <- x_full[row_i, , drop = FALSE]
  shap_values <- approx_shap_one(rf_model, baseline, x_interest, top_features, n_perm = 60)
  for (feature in row.names(shap_values)) {
    for (cls in colnames(shap_values)) {
      sample_rows[[counter]] <- data.frame(
        credit_id = test_raw$credit_id[row_i],
        actual = as.character(test_raw$target_final_outcome[row_i]),
        feature = feature,
        class = cls,
        shap_value = shap_values[feature, cls],
        stringsAsFactors = FALSE
      )
      counter <- counter + 1
    }
  }
}

sample_df <- do.call(rbind, sample_rows)
write.csv(sample_df, OUT_SAMPLE, row.names = FALSE)

agg <- aggregate(
  shap_value ~ feature + class,
  data = sample_df,
  FUN = function(x) c(mean_shap = mean(x), mean_abs_shap = mean(abs(x)))
)
summary_df <- data.frame(
  feature = agg$feature,
  class = agg$class,
  mean_shap = agg$shap_value[, "mean_shap"],
  mean_abs_shap = agg$shap_value[, "mean_abs_shap"],
  row.names = NULL
)
summary_df <- summary_df[order(summary_df$class, -summary_df$mean_abs_shap), , drop = FALSE]
write.csv(summary_df, OUT_SUMMARY, row.names = FALSE)

cat("Wrote", OUT_SUMMARY, "\n")
cat("Wrote", OUT_SAMPLE, "\n")
