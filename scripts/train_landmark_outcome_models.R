#!/usr/bin/env Rscript

# Train landmark models for final loan outcome prediction.
# Models:
#   1. Multinomial logistic regression baseline.
#   2. Random forest tree-ensemble baseline.

suppressPackageStartupMessages({
  library(nnet)
  library(randomForest)
})

set.seed(20260609)

DATA_PATH <- "data/modeling/loan_modeling_dataset.csv"
MODEL_DIR <- "models"
PRED_DIR <- "data/modeling"

args <- commandArgs(trailingOnly = TRUE)
window_days <- 30
if (length(args) > 0) {
  if (length(args) == 1 && grepl("^[0-9]+$", args[1])) {
    window_days <- as.integer(args[1])
  } else {
    for (i in seq_along(args)) {
      if (args[i] %in% c("--window", "-w") && i < length(args)) {
        window_days <- as.integer(args[i + 1])
      }
    }
  }
}
if (!(window_days %in% c(30, 60, 90))) {
  stop("window_days must be one of 30, 60, or 90")
}

window_tag <- paste0(window_days, "d")
window_prefix <- paste0("w", window_tag, "_")
eligible_col <- paste0("eligible_", window_tag)
REPORT_PATH <- file.path("docs", paste0("loan_outcome_", window_tag, "_model_results.md"))

dir.create(MODEL_DIR, showWarnings = FALSE, recursive = TRUE)
dir.create(PRED_DIR, showWarnings = FALSE, recursive = TRUE)
dir.create(dirname(REPORT_PATH), showWarnings = FALSE, recursive = TRUE)

safe_num <- function(x) {
  suppressWarnings(as.numeric(x))
}

is_missing_text <- function(x) {
  is.na(x) | x == "" | x == "NA"
}

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

raw <- read.csv(DATA_PATH, stringsAsFactors = FALSE, check.names = FALSE)
df <- raw[raw[[eligible_col]] == "1", , drop = FALSE]
df$target_final_outcome <- factor(df$target_final_outcome, levels = label_levels)
df <- df[!is.na(df$target_final_outcome), , drop = FALSE]

window_features <- grep(paste0("^", window_prefix), names(df), value = TRUE)
feature_cols <- c(static_features, window_features)
feature_cols <- feature_cols[feature_cols %in% names(df)]

id_cols <- c("credit_id", "customer_id")
all_cols <- c(id_cols, "target_final_outcome", feature_cols)
df <- df[, all_cols, drop = FALSE]

numeric_features <- c(
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
  "customer_age",
  "customer_income",
  "customer_dependents",
  "customer_age_at_loan_days",
  "sas_credit_score",
  window_features
)
numeric_features <- intersect(numeric_features, feature_cols)
categorical_features <- setdiff(feature_cols, numeric_features)

stratified_split <- function(y, train_frac = 0.60, val_frac = 0.20) {
  split <- rep(NA_character_, length(y))
  for (cls in levels(y)) {
    idx <- which(y == cls)
    idx <- sample(idx)
    n <- length(idx)
    n_train <- floor(n * train_frac)
    n_val <- floor(n * val_frac)
    if (n >= 3) {
      n_train <- max(1, n_train)
      n_val <- max(1, n_val)
    }
    train_idx <- idx[seq_len(n_train)]
    val_idx <- if (n_val > 0) idx[(n_train + 1):(n_train + n_val)] else integer(0)
    test_idx <- setdiff(idx, c(train_idx, val_idx))
    split[train_idx] <- "train"
    split[val_idx] <- "validation"
    split[test_idx] <- "test"
  }
  split
}

df$split <- stratified_split(df$target_final_outcome)

train_raw <- df[df$split == "train", , drop = FALSE]
val_raw <- df[df$split == "validation", , drop = FALSE]
test_raw <- df[df$split == "test", , drop = FALSE]

make_preprocess <- function(train_df) {
  numeric_medians <- list()
  missing_indicators <- character(0)
  for (col in numeric_features) {
    values <- safe_num(train_df[[col]])
    if (any(is.na(values))) {
      missing_indicators <- c(missing_indicators, col)
    }
    med <- suppressWarnings(stats::median(values, na.rm = TRUE))
    if (!is.finite(med)) {
      med <- 0
    }
    numeric_medians[[col]] <- med
  }

  categorical_levels <- list()
  for (col in categorical_features) {
    values <- train_df[[col]]
    values[is_missing_text(values)] <- "Missing"
    tab <- sort(table(values), decreasing = TRUE)
    keep <- names(tab)[seq_len(min(30, length(tab)))]
    categorical_levels[[col]] <- c(sort(unique(c(keep, "Missing", "Other"))))
  }

  list(
    numeric_features = numeric_features,
    categorical_features = categorical_features,
    numeric_medians = numeric_medians,
    missing_indicators = missing_indicators,
    categorical_levels = categorical_levels,
    label_levels = label_levels
  )
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

prep <- make_preprocess(train_raw)
train <- apply_preprocess(train_raw, prep)
validation <- apply_preprocess(val_raw, prep)
test <- apply_preprocess(test_raw, prep)

class_counts <- table(train$target_final_outcome)
class_weights <- as.numeric(sum(class_counts) / (length(class_counts) * class_counts))
names(class_weights) <- names(class_counts)
train_weights <- class_weights[as.character(train$target_final_outcome)]

model_formula <- as.formula("target_final_outcome ~ .")

multinom_model <- multinom(
  model_formula,
  data = train,
  weights = train_weights,
  decay = 1e-4,
  maxit = 300,
  trace = FALSE,
  MaxNWts = 100000
)

rf_model <- randomForest(
  model_formula,
  data = train,
  ntree = 400,
  mtry = max(2, floor(sqrt(ncol(train) - 1))),
  classwt = class_weights,
  importance = TRUE,
  na.action = na.fail
)

prob_matrix <- function(model, newdata, model_type) {
  if (model_type == "multinom") {
    probs <- predict(model, newdata = newdata, type = "probs")
  } else {
    probs <- predict(model, newdata = newdata, type = "prob")
  }
  probs <- as.matrix(probs)
  if (is.null(colnames(probs))) {
    probs <- matrix(probs, ncol = length(label_levels))
  }
  missing_cols <- setdiff(label_levels, colnames(probs))
  if (length(missing_cols) > 0) {
    add <- matrix(0, nrow = nrow(probs), ncol = length(missing_cols))
    colnames(add) <- missing_cols
    probs <- cbind(probs, add)
  }
  probs[, label_levels, drop = FALSE]
}

predict_classes <- function(probs) {
  factor(colnames(probs)[max.col(probs, ties.method = "first")], levels = label_levels)
}

classification_metrics <- function(truth, probs) {
  truth <- factor(truth, levels = label_levels)
  pred <- predict_classes(probs)
  cm <- table(truth = truth, prediction = pred)
  per_class <- data.frame(
    class = label_levels,
    support = as.integer(table(truth)[label_levels]),
    precision = NA_real_,
    recall = NA_real_,
    f1 = NA_real_
  )
  for (i in seq_along(label_levels)) {
    cls <- label_levels[i]
    tp <- cm[cls, cls]
    fp <- sum(cm[, cls]) - tp
    fn <- sum(cm[cls, ]) - tp
    precision <- ifelse(tp + fp == 0, NA_real_, tp / (tp + fp))
    recall <- ifelse(tp + fn == 0, NA_real_, tp / (tp + fn))
    f1 <- ifelse(is.na(precision) || is.na(recall) || precision + recall == 0, NA_real_, 2 * precision * recall / (precision + recall))
    per_class$precision[i] <- precision
    per_class$recall[i] <- recall
    per_class$f1[i] <- f1
  }
  eps <- 1e-15
  clipped <- pmin(pmax(probs, eps), 1 - eps)
  truth_idx <- match(as.character(truth), colnames(clipped))
  log_loss <- -mean(log(clipped[cbind(seq_along(truth_idx), truth_idx)]))
  accuracy <- mean(pred == truth)
  macro_f1 <- mean(per_class$f1, na.rm = TRUE)
  weighted_f1 <- sum(per_class$f1 * per_class$support, na.rm = TRUE) / sum(per_class$support)
  list(
    accuracy = accuracy,
    macro_f1 = macro_f1,
    weighted_f1 = weighted_f1,
    log_loss = log_loss,
    confusion = cm,
    per_class = per_class,
    pred = pred
  )
}

evaluate <- function(model, model_type, split_name, split_data, split_raw) {
  probs <- prob_matrix(model, split_data, model_type)
  metrics <- classification_metrics(split_data$target_final_outcome, probs)
  pred_df <- data.frame(
    credit_id = split_raw$credit_id,
    customer_id = split_raw$customer_id,
    split = split_name,
    actual = as.character(split_data$target_final_outcome),
    predicted = as.character(metrics$pred),
    probs,
    check.names = FALSE
  )
  list(metrics = metrics, predictions = pred_df)
}

evals <- list(
  multinom_validation = evaluate(multinom_model, "multinom", "validation", validation, val_raw),
  multinom_test = evaluate(multinom_model, "multinom", "test", test, test_raw),
  random_forest_validation = evaluate(rf_model, "rf", "validation", validation, val_raw),
  random_forest_test = evaluate(rf_model, "rf", "test", test, test_raw)
)

write.csv(evals$multinom_validation$predictions, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_multinom_validation_predictions.csv")), row.names = FALSE)
write.csv(evals$multinom_test$predictions, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_multinom_test_predictions.csv")), row.names = FALSE)
write.csv(evals$random_forest_validation$predictions, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_random_forest_validation_predictions.csv")), row.names = FALSE)
write.csv(evals$random_forest_test$predictions, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_random_forest_test_predictions.csv")), row.names = FALSE)

saveRDS(
  list(model = multinom_model, preprocess = prep, feature_cols = feature_cols),
  file.path(MODEL_DIR, paste0("loan_outcome_", window_tag, "_multinom.rds"))
)
saveRDS(
  list(model = rf_model, preprocess = prep, feature_cols = feature_cols),
  file.path(MODEL_DIR, paste0("loan_outcome_", window_tag, "_random_forest.rds"))
)

metric_row <- function(model_name, split_name, item) {
  data.frame(
    model = model_name,
    split = split_name,
    accuracy = item$metrics$accuracy,
    macro_f1 = item$metrics$macro_f1,
    weighted_f1 = item$metrics$weighted_f1,
    log_loss = item$metrics$log_loss
  )
}

metrics_summary <- rbind(
  metric_row("Multinomial logistic regression", "validation", evals$multinom_validation),
  metric_row("Multinomial logistic regression", "test", evals$multinom_test),
  metric_row("Random forest", "validation", evals$random_forest_validation),
  metric_row("Random forest", "test", evals$random_forest_test)
)
write.csv(metrics_summary, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_metrics.csv")), row.names = FALSE)

rf_importance <- importance(rf_model, type = 1)
rf_importance_df <- data.frame(
  feature = row.names(rf_importance),
  mean_decrease_accuracy = as.numeric(rf_importance[, 1]),
  row.names = NULL
)
rf_importance_df <- rf_importance_df[order(-rf_importance_df$mean_decrease_accuracy), , drop = FALSE]
write.csv(rf_importance_df, file.path(PRED_DIR, paste0("loan_outcome_", window_tag, "_random_forest_feature_importance.csv")), row.names = FALSE)

format_metric <- function(x) sprintf("%.4f", x)

cm_to_markdown <- function(cm) {
  lines <- c("| Actual \\ Predicted | Clean Paid Off | Paid Off After Delinquency | Written Off | Sold | Other |",
             "|---|---:|---:|---:|---:|---:|")
  short <- c("Clean Paid Off", "Paid Off After Delinquency", "Written Off", "Sold", "Other Terminal / Special Closure")
  row_labels <- c("Clean Paid Off", "Paid Off After Delinquency", "Written Off", "Sold", "Other")
  for (i in seq_along(short)) {
    values <- as.integer(cm[short[i], short])
    lines <- c(lines, paste0("| ", row_labels[i], " | ", paste(values, collapse = " | "), " |"))
  }
  lines
}

per_class_to_markdown <- function(per_class) {
  lines <- c("| Class | Support | Precision | Recall | F1 |", "|---|---:|---:|---:|---:|")
  for (i in seq_len(nrow(per_class))) {
    lines <- c(lines, sprintf(
      "| %s | %d | %s | %s | %s |",
      per_class$class[i],
      per_class$support[i],
      ifelse(is.na(per_class$precision[i]), "", format_metric(per_class$precision[i])),
      ifelse(is.na(per_class$recall[i]), "", format_metric(per_class$recall[i])),
      ifelse(is.na(per_class$f1[i]), "", format_metric(per_class$f1[i]))
    ))
  }
  lines
}

summary_table_lines <- c(
  "| Model | Split | Accuracy | Macro F1 | Weighted F1 | Log loss |",
  "|---|---|---:|---:|---:|---:|"
)
for (i in seq_len(nrow(metrics_summary))) {
  summary_table_lines <- c(summary_table_lines, sprintf(
    "| %s | %s | %s | %s | %s | %s |",
    metrics_summary$model[i],
    metrics_summary$split[i],
    format_metric(metrics_summary$accuracy[i]),
    format_metric(metrics_summary$macro_f1[i]),
    format_metric(metrics_summary$weighted_f1[i]),
    format_metric(metrics_summary$log_loss[i])
  ))
}

split_counts <- rbind(
  data.frame(split = "train", as.data.frame(table(train$target_final_outcome))),
  data.frame(split = "validation", as.data.frame(table(validation$target_final_outcome))),
  data.frame(split = "test", as.data.frame(table(test$target_final_outcome)))
)
names(split_counts) <- c("split", "class", "n")

split_lines <- c("| Split | Class | Loans |", "|---|---|---:|")
for (i in seq_len(nrow(split_counts))) {
  split_lines <- c(split_lines, sprintf("| %s | %s | %d |", split_counts$split[i], split_counts$class[i], split_counts$n[i]))
}

importance_lines <- c("| Rank | Feature | Mean decrease accuracy |", "|---:|---|---:|")
top_imp <- head(rf_importance_df, 25)
for (i in seq_len(nrow(top_imp))) {
  importance_lines <- c(importance_lines, sprintf("| %d | `%s` | %s |", i, top_imp$feature[i], format_metric(top_imp$mean_decrease_accuracy[i])))
}

report <- c(
  paste0("# ", window_days, "-Day Final Outcome Model Results"),
  "",
  "## Setup",
  "",
  paste0("The training unit is one issued loan. This run uses only rows with `", eligible_col, " = 1`, meaning the loan remained observable beyond the ", window_days, "-day landmark. Features include conservative static borrower/loan variables and `", window_prefix, "*` window summary variables only. Terminal dates, final debt/delay fields, and other landmark-window variables are excluded."),
  "",
  "The sample is split by stratified random sampling into train, validation, and test sets with an approximate 60/20/20 allocation within each final-outcome class.",
  "",
  "## Split Distribution",
  "",
  split_lines,
  "",
  "## Metrics",
  "",
  summary_table_lines,
  "",
  "## Test Confusion Matrix: Multinomial Logistic Regression",
  "",
  cm_to_markdown(evals$multinom_test$metrics$confusion),
  "",
  "## Test Per-Class Metrics: Multinomial Logistic Regression",
  "",
  per_class_to_markdown(evals$multinom_test$metrics$per_class),
  "",
  "## Test Confusion Matrix: Random Forest",
  "",
  cm_to_markdown(evals$random_forest_test$metrics$confusion),
  "",
  "## Test Per-Class Metrics: Random Forest",
  "",
  per_class_to_markdown(evals$random_forest_test$metrics$per_class),
  "",
  "## Random Forest Feature Importance",
  "",
  importance_lines,
  "",
  "## Caveats",
  "",
  "- `Written Off` and `Other Terminal / Special Closure` have very small sample sizes, so their per-class metrics are unstable.",
  "- This is a first-pass baseline run, not a tuned production model.",
  "- The random forest is used as the first tree-based baseline because gradient boosting libraries are not currently available in the local runtime.",
  ""
)

writeLines(report, REPORT_PATH)

cat("Rows used:", nrow(df), "\n")
cat("Train:", nrow(train), "Validation:", nrow(validation), "Test:", nrow(test), "\n")
cat("Wrote", REPORT_PATH, "\n")
print(metrics_summary)
