# Credit Platform Data Sample Overview

Data directory: `/Users/yil1/Downloads/datasets CO-KTU workshop`
Sample size per file: first `50` data rows

This report is based on column names and sampled values only. The raw CSV files stay outside the repository.

## `export_customers.csv`

- Rows inspected: `50`
- Columns: `170`

### Business meaning

This file appears to be customer master data. Each row is a borrower/customer profile with identity/contact fields, demographics, address, employment and income information, registration source, risk/application flags, credit history counters, and aggregate repayment/loan metrics.

The natural primary key is `customer_id`, which links to loan-level files through `customer_id`.

### Column groups

- `identifiers_and_account`: `customer_id`, `category_id`, `login`, `contract_id`, `contract_code`, `uin`, `enabled`, `status`, `state`, `acc_status_id`, `admin_id`, `sub_admin_id`
- `personal_and_contact`: `email`, `email2`, `realname`, `surname`, `midname`, `midname2`, `mob_phone`, `mob_phone2`, `phone`, `work_phone`, `contact_name`, `contact_phone`, `person_code`, `birthday`, `age`, `gender`
- `address_and_region`: `city`, `county`, `parish`, `village`, `address`, `zipcode`, `city2`, `county2`, `parish2`, `village2`, `address2`, `zipcode2`, `region`, `region2`, `country`, `street`
- `employment_and_income`: `workplace`, `workplace_address`, `workplace_position`, `work_activities`, `work_status`, `work_company_code`, `company_code`, `company_name`, `employers_ids`, `income`, `dependents`, `home_status`
- `credit_history`: `credits`, `exts`, `credits_paid`, `exts_paid`, `all_paid`, `all_expired`, `last_credit_id`, `last_credit_date`, `first_credit_date`, `first_credit_paid_date`, `last_payment_date`, `last_extension_date`, `paid_credits_amount_max`
- `risk_and_limits`: `debt_limit`, `debt`, `credit_limit`, `overpaid`, `delay`, `delay_max`, `days_to_expire`, `days_from_last_loan_repayment`, `BDS_score`, `evaluation_category_id`, `fraud`, `exaction_status`, `applications_disabled`, `data_use_disabled`
- `application_and_conversion`: `applications`, `applications_rejected`, `last_rejection_date`, `last_application_date`, `activated`, `lander`, `ref`, `reg_method`, `reg_form_id`, `reg_confirm_method`, `marketing`
- `financial_aggregates`: `all_payments_amount`, `all_credits_amount_sum`, `all_credits_charge_sum`, `active_credits_amount_sum`, `reg_payments_count`, `payouts`, `active_payouts`, `active_extensions`, `current_paid_payments`, `loyalty_points`
- `audit_and_flags`: `created`, `modified`, `modified_by_customer`, `last_login_time`, `ip`, `api_user_id`, `important`, `force_change`, `sms_enabled`, `language`, `documents_attached`, `category_changed`
- `other_or_low_level_system_fields`: `temp_passw`, `passw`, `sms_mob_phone`, `sodra_confirm`, `id_number`, `passport_number`, `notes`, `login_attempts`, `reminders_disabled`, `exts_disabled`, `cleared`, `chk2`, `chk3`, `chk4`, `chk5`, `chk6`, `chk7`, `chk8`, `chk9`, `data`, `bank`, `ch_contract`, `req_blocked_until`, `flat`, `house`, `flat2`, `house2`, `person_code_attempts`, `broker_id`, `use_email2`, `last_credit_period`, `documents_attached_last_date`, `representative_ids`, `mob_phone_failed`, `mob_phone2_failed`, `chk1`, `region3`, `county3`, `parish3`, `village3`, `city3`, `address3`, `house3`, `flat3`, `zipcode3`, `investors_ids`, `street2`, `vat_rate`, `id_number_validity`, `passport_number_validity`, `last_credit_paid_period_percent`, `last_paid_credit_discount`, `credits_paid_before_term_percent`, `tax_id_number`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `customer_id` | 50/50 | 50 | 2358; 3324; 7328 |
| `category_id` | 50/50 | 6 | 1; 20; 5 |
| `login` | 50/50 | 50 | 8571323; 0275436; 7922414 |
| `contract_id` | 44/50 | 3 | 12; 11 |
| `contract_code` | 44/50 | 45 | a7c93c4928b023c98afbaa1fca33ea4c; 580f163bc394460bb3e7f41608eec4e2; 3bf3977d96a22ab429a8778978865438 |
| `uin` | 50/50 | 50 | 6c8338b273fc862d5320c0838562a2b4; b055212bab299f917cd434b13f4098bc; 9ece6bc8a9d69aa7816cde7043a9d1f3 |
| `temp_passw` | 50/50 | 50 | 432247; 366165; 781037 |
| `passw` | 50/50 | 50 | 817145536f3827934e8ae8791d612de9; a274cd19a80714241f4355a07fb65226; 26c6806d98704cc0825760141c10759f |
| `enabled` | 45/50 | 2 | 1 |
| `status` | 29/50 | 2 | 1 |
| `state` | 0/50 | 1 |  |
| `created` | 50/50 | 49 | 2021/6/5 07:13; 2023/10/12 15:14; 2020/11/21 16:05 |
| `modified` | 50/50 | 50 | 2022/1/19 16:55; 2025/2/3 10:15; 2025/9/15 08:05 |
| `email` | 50/50 | 50 | 2358.test@test.creditonline.eu; 3324.test@test.creditonline.eu; 7328.test@test.creditonline.eu |
| `realname` | 50/50 | 50 | Name2358 Midname2358 Surname2358; Name3324 Midname3324 Surname3324; Name7328 Surname7328 |
| `surname` | 0/50 | 1 |  |
| `mob_phone` | 50/50 | 50 | +370 61002358; +370 61003324; +370 61007328 |
| `mob_phone2` | 50/50 | 50 | +370 62002358; +370 62003324; +370 62007328 |
| `sms_mob_phone` | 1/50 | 2 | 1 |
| `person_code` | 50/50 | 50 | 1000002358; 1000003324; 1000007328 |
| `city` | 39/50 | 30 | _ilal_; Panev_žio_r._sav.; Vilniaus_r._sav. |
| `county` | 50/50 | 1 | Obfuscated |
| `parish` | 50/50 | 1 | Obfuscated |
| `village` | 50/50 | 1 | Obfuscated |
| `address` | 50/50 | 1 | Obfuscated 0-0 |
| `zipcode` | 50/50 | 1 | Obfuscated |
| `city2` | 12/50 | 13 | Elektr_nų sav.; Klaip_da; Plung_ |
| `county2` | 50/50 | 1 | Obfuscated |
| `parish2` | 50/50 | 1 | Obfuscated |
| `village2` | 50/50 | 1 | Obfuscated |
| `address2` | 50/50 | 1 | Obfuscated 0-0 |
| `zipcode2` | 50/50 | 1 | Obfuscated |
| `age` | 50/50 | 24 | 46; 56; 35 |
| `gender` | 50/50 | 2 | m; f |
| `debt_limit` | 3/50 | 2 | 6000 |
| `debt` | 0/50 | 1 |  |
| `force_change` | 45/50 | 2 | 1 |
| `sms_enabled` | 0/50 | 1 |  |
| `language` | 50/50 | 1 | lt |
| `sodra_confirm` | 0/50 | 1 |  |
| `workplace` | 50/50 | 1 | Obfuscated |
| `workplace_address` | 50/50 | 50 | Obfuscated 0-2358; Obfuscated 0-3324; Obfuscated 0-7328 |
| `workplace_position` | 0/50 | 1 |  |
| `id_number` | 0/50 | 1 |  |
| `passport_number` | 0/50 | 1 |  |
| `notes` | 50/50 | 1 | Obfuscated |
| `login_attempts` | 0/50 | 1 |  |
| `reminders_disabled` | 0/50 | 1 |  |
| `marketing` | 39/50 | 3 | 1; 2 |
| `exts_disabled` | 0/50 | 1 |  |
| `region` | 50/50 | 1 | Obfuscated |
| `region2` | 50/50 | 1 | Obfuscated |
| `cleared` | 0/50 | 1 |  |
| `admin_id` | 5/50 | 4 | 50; 54; 13 |
| `birthday` | 50/50 | 1 | 1990/1/1 |
| `chk2` | 9/50 | 2 | 1 |
| `chk3` | 32/50 | 2 | 1 |
| `chk4` | 0/50 | 1 |  |
| `chk5` | 0/50 | 1 |  |
| `chk6` | 0/50 | 1 |  |
| `chk7` | 0/50 | 1 |  |
| `chk8` | 0/50 | 1 |  |
| `chk9` | 0/50 | 1 |  |
| `data` | 50/50 | 1 | a:0:{} |
| `bank` | 32/50 | 5 | AB Swedbank; AB _iaulių bankas; AB SEB bankas |
| `ch_contract` | 0/50 | 1 |  |
| `ref` | 24/50 | 6 | https://www.google.com/; https://www.visikreditai.lt/paskolos-su-bloga-kredito-istorija/; https://www.google.lt/ |
| `req_blocked_until` | 1/50 | 2 | 2020/1/5 13:08 |
| `credits` | 12/50 | 4 | 1; 2; 4 |
| `exts` | 1/50 | 2 | 10 |
| `credits_paid` | 12/50 | 4 | 1; 2; 4 |
| `exts_paid` | 1/50 | 2 | 10 |
| `all_paid` | 12/50 | 5 | 1; 2; 4 |
| `all_expired` | 5/50 | 2 | 1 |
| `delay` | 0/50 | 1 |  |
| `delay_max` | 9/50 | 9 | 146; 52; 180 |
| `important` | 0/50 | 1 |  |
| `ip` | 47/50 | 33 | 88.118.51.248; 88.119.205.175; 213.190.40.74 |
| `last_credit_date` | 12/50 | 10 | 2023/3/27; 2021/10/18; 2020/1/17 |
| `dependents` | 0/50 | 1 |  |
| `home_status` | 50/50 | 1 | Obfuscated |
| `flat` | 50/50 | 1 | Obfuscated |
| `house` | 50/50 | 1 | Obfuscated |
| `flat2` | 50/50 | 1 | Obfuscated |
| `house2` | 50/50 | 1 | Obfuscated |
| `work_activities` | 0/50 | 1 |  |
| `work_status` | 0/50 | 1 |  |
| `midname` | 0/50 | 1 |  |
| `phone` | 50/50 | 1 | Obfuscated |
| `work_phone` | 50/50 | 1 | Obfuscated |
| `income` | 0/50 | 1 |  |
| `contact_name` | 50/50 | 1 | Obfuscated |
| `contact_phone` | 50/50 | 50 | +370 63002358; +370 63003324; +370 63007328 |
| `activated` | 30/50 | 31 | 2023/10/13 20:36; 2024/5/28 14:48; 2022/11/30 18:45 |
| `person_code_attempts` | 0/50 | 1 |  |
| `lander` | 35/50 | 23 | /?gclid=Cj0KCQjwnueFBhChARIsAPu3YkSEG_fTXwGYpV7ohZEQGCB-_xbOFS52l-B1Cj; /greitieji-kreditai/; /?gclid=Cj0KCQiAkuP9BRCkARIsAKGLE8WfUC5jg5P4xj8f9pIl1CyEwjq6-27HiFV_1- |
| `broker_id` | 0/50 | 1 |  |
| `reg_method` | 47/50 | 3 | 3; 1 |
| `reg_form_id` | 50/50 | 1 | 1 |
| `fraud` | 0/50 | 1 |  |
| `exaction_status` | 0/50 | 1 |  |
| `work_company_code` | 50/50 | 1 | Obfuscated |
| `BDS_score` | 0/50 | 1 |  |
| `modified_by_customer` | 10/50 | 11 | 2023/10/13 20:19; 2024/7/31 13:36; 2024/12/26 04:52 |
| `applications` | 0/50 | 1 |  |
| `applications_rejected` | 38/50 | 8 | 1; 9; 2 |
| `last_rejection_date` | 38/50 | 28 | 2025/3/27; 2023/10/16; 2025/3/28 |
| `last_application_date` | 0/50 | 1 |  |
| `api_user_id` | 32/50 | 2 | 2 |
| `evaluation_category_id` | 0/50 | 1 |  |
| `overpaid` | 1/50 | 2 | 0.46 |
| `company_code` | 0/50 | 1 |  |
| `days_to_expire` | 0/50 | 1 |  |
| `first_credit_date` | 12/50 | 8 | 2023/3/27; 2021/10/18; 2020/1/17 |
| `loyalty_points` | 0/50 | 1 |  |
| `acc_status_id` | 0/50 | 1 |  |
| `email2` | 50/50 | 50 | 2358.2.test@test.creditonline.eu; 3324.2.test@test.creditonline.eu; 7328.2.test@test.creditonline.eu |
| `use_email2` | 0/50 | 1 |  |
| `company_name` | 50/50 | 1 | Obfuscated |
| `employers_ids` | 0/50 | 1 |  |
| `reg_confirm_method` | 30/50 | 3 | payment; contract |
| `last_credit_period` | 0/50 | 1 |  |
| `first_credit_paid_date` | 12/50 | 13 | 2024/11/11; 2021/11/22; 2023/1/18 |
| `all_payments_amount` | 37/50 | 17 | 0.01; 0.11; 0.2 |
| `documents_attached` | 38/50 | 21 | 2; 13; 16 |
| `documents_attached_last_date` | 38/50 | 32 | 2022/1/19; 2025/2/3; 2025/5/9 |
| `days_from_last_loan_repayment` | 12/50 | 13 | 569; 1654; 1232 |
| `current_paid_payments` | 0/50 | 1 |  |
| `last_payment_date` | 37/50 | 31 | 2011/3/12; 2023/10/13; 2013/9/5 |
| `credit_limit` | 0/50 | 1 |  |
| `representative_ids` | 0/50 | 1 |  |
| `last_extension_date` | 0/50 | 1 |  |
| `mob_phone_failed` | 0/50 | 1 |  |
| `mob_phone2_failed` | 0/50 | 1 |  |
| `applications_disabled` | 0/50 | 1 |  |
| `data_use_disabled` | 0/50 | 1 |  |
| `chk1` | 0/50 | 1 |  |
| `all_credits_amount_sum` | 12/50 | 10 | 1000; 200; 900 |
| `all_credits_charge_sum` | 12/50 | 12 | 999.13; 157.92; 899.28 |
| `region3` | 50/50 | 1 | Obfuscated |
| `county3` | 50/50 | 1 | Obfuscated |
| `parish3` | 50/50 | 1 | Obfuscated |
| `village3` | 50/50 | 1 | Obfuscated |
| `city3` | 0/50 | 1 |  |
| `address3` | 50/50 | 1 | Obfuscated 0-0 |
| `house3` | 50/50 | 1 | Obfuscated |
| `flat3` | 50/50 | 1 | Obfuscated |
| `zipcode3` | 50/50 | 1 | Obfuscated |
| `active_credits_amount_sum` | 0/50 | 1 |  |
| `reg_payments_count` | 37/50 | 4 | 1; 2; 3 |
| `investors_ids` | 0/50 | 1 |  |
| `payouts` | 2/50 | 3 | 2; 1 |
| `active_payouts` | 0/50 | 1 |  |
| `active_extensions` | 0/50 | 1 |  |
| `country` | 50/50 | 1 | OB |
| `street` | 50/50 | 1 | Obfuscated |
| `street2` | 50/50 | 1 | Obfuscated |
| `vat_rate` | 0/50 | 1 |  |
| `id_number_validity` | 0/50 | 1 |  |
| `passport_number_validity` | 0/50 | 1 |  |
| `last_credit_id` | 12/50 | 13 | 178356; 149449; 111236 |
| `paid_credits_amount_max` | 12/50 | 9 | 1000; 200; 900 |
| `last_login_time` | 21/50 | 22 | 2023/10/13 20:56; 2025/6/6 13:20; 2023/3/30 12:53 |
| `midname2` | 50/50 | 1 | Obfuscated |
| `sub_admin_id` | 0/50 | 1 |  |
| `last_credit_paid_period_percent` | 12/50 | 12 | 99; 7; 102 |
| `last_paid_credit_discount` | 1/50 | 2 | 5 |
| `credits_paid_before_term_percent` | 12/50 | 10 | 99; 7; 100 |
| `tax_id_number` | 50/50 | 1 | Obfuscated |
| `category_changed` | 0/50 | 1 |  |

### Common naming tokens

`id` (14), `last` (12), `paid` (9), `credit` (8), `date` (8), `credits` (7), `phone` (6), `code` (5), `status` (5), `mob` (5), `number` (5), `all` (5)

## `export_credits.csv`

- Rows inspected: `50`
- Columns: `179`

### Business meaning

This file appears to be loan or credit-contract level data. Each row is a credit issued or requested by a `customer_id`, with amount, term, pricing, due dates, repayment status, delinquency/collection fields, system configuration snapshots, and audit/channel metadata.

The natural join key to customers is `customer_id`; the loan primary key appears to be `id`.

### Column groups

- `identifiers_and_links`: `id`, `customer_id`, `contract_id`, `account_number`, `number`, `outer_system_id`, `outer_credit_id`, `product_id`, `investor_id`, `broker_id`, `employer_id`, `representative_id`
- `loan_terms_and_pricing`: `amount`, `issued_amount`, `period`, `charge`, `administrative_fee`, `insurance`, `interest`, `apr`, `tax_apr`, `cinterest`, `creditline_amount`, `virtual_amount`, `discount`, `discount_code`
- `dates_and_lifecycle`: `created`, `registered`, `modified`, `expire`, `paid`, `s_date`, `s_expire`, `stop_date`, `transfer_date`, `termination_date`, `withdraw_date`, `confirm_code_date`, `admin_start_time`
- `repayment_and_balance`: `debt`, `s_debt`, `r_debt`, `residual_amount`, `overpaid`, `p_amount`, `s_payment`, `s_paid_number`, `l_pay`, `l_amount`, `balance_order_id`
- `delinquency_and_collection`: `penalty`, `late_fee`, `late_fee_corr`, `late_fee_limit`, `current_delay`, `max_delay`, `dc_contact`, `dc_contact_date`, `court_date`, `sold`, `writeoff`, `writeoff_a`, `urgency`
- `configuration_fields`: `cfg_penalty`, `cfg_penalty_delay`, `cfg_late_fee`, `cfg_late_fee_start`, `cfg_late_fee_stop`, `cfg_interest_apr`, `cfg_interest_start`, `cfg_interest_stop`, `cfg_interest_mode`, `cfg_bailiff`, `cfg_sais`, `cfg_court`
- `structured_or_text_fields`: `schedule`, `o_schedule`, `description`, `comments`, `reason`, `ref`, `lander`, `features_id`, `plist_options`
- `audit_channel_and_flags`: `confirmed`, `conditions_accepted`, `solvency_checked`, `credit_ip`, `credit_domain`, `api_user_id`, `admin_id`, `office_id`, `currency`, `c_currency`, `bank`, `e_sign`, `archive`, `category_changed`
- `other_or_low_level_system_fields`: `confirm_code`, `extends_id`, `cfg_late_fee_mode`, `extend`, `cfg_withdrawn`, `o_charge`, `use_grid`, `writeoff_l`, `writeoff_p`, `important`, `late_fee_corr_d`, `ret`, `special`, `l_interest`, `l_late_fee`, `l_percent`, `insurance_ext`, `acts_id`, `tax1`, `tax2`, `l_tax1`, `l_tax2`, `l_cinterest`, `cfg_einsurance_start`, `cfg_einsurance_stop`, `einsurance`, `origin_id`, `late_fee_stop_d`, `plist_id`, `tax3`, `tax4`, `tax5`, `l_tax3`, `l_tax4`, `l_tax5`, `admin_office_id`, `cfg_upt_covering`, `o_administrative_fee`, `o_insurance`, `o_interest`, `tax6`, `tax7`, `l_tax6`, `l_tax7`, `ar`, `tax8`, `tax9`, `tax10`, `tax11`, `tax12`, `late_fee_timer`, `l_tax8`, `l_tax9`, `l_tax10`, `l_tax11`, `l_tax12`, `l_s_amount`, `l_s_interest`, `c_ar`, `ret_cancel`, `deposit_ids`, `plist_interest`, `plist_o_interest`, `transfer_admin_id`, `l_s_administrative_fee`, `ret_adm_fee_mode`, `creditline_mode`, `schedule_type`, `l_administrative_fee`, `l_penalty`, `plist_administrative_fee`, `r_charge`, `confirm_code_admin`, `ret_start`, `dc_contact_person`, `dc_contact_admin_id`, `debt_service_to_income_ratio`, `ret_canceled`, `plist_insurance`, `account_owner_name`, `expire_wd`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `id` | 50/50 | 50 | 110115; 110139; 110150 |
| `customer_id` | 50/50 | 49 | 45709; 45717; 45720 |
| `admin_id` | 50/50 | 4 | 16; 37; 35 |
| `created` | 50/50 | 50 | 2020-01-02 17:56:38; 2020-01-02 18:20:03; 2020-01-03 10:00:35 |
| `period` | 50/50 | 12 | 1080; 90; 600 |
| `charge` | 50/50 | 27 | 999.44; 449.64; 16.16 |
| `amount` | 50/50 | 12 | 1000.00; 450.00; 100.00 |
| `expire` | 50/50 | 31 | 2022-12-17; 2020-04-02; 2021-08-25 |
| `account_number` | 50/50 | 49 | LT040000000000045709; LT790000000000045717; LT950000000000045720 |
| `description` | 50/50 | 20 | internetApi; changed (180,500.00); internetApi; changed (1080,850.00); internetApi; changed (90,200.00) |
| `confirmed` | 50/50 | 1 | 1 |
| `debt` | 0/50 | 1 |  |
| `paid` | 43/50 | 44 | 2022-12-09 14:27:00; 2022-01-10 16:04:00; 2020-02-05 08:31:00 |
| `penalty` | 0/50 | 1 |  |
| `overpaid` | 0/50 | 1 |  |
| `late_fee` | 31/50 | 30 | 3.33; 0.06; 19.57 |
| `registered` | 50/50 | 50 | 2020-01-02 13:18:01; 2020-01-02 17:01:04; 2020-01-02 19:57:14 |
| `confirm_code` | 0/50 | 1 |  |
| `comments` | 50/50 | 1 | Obfuscated |
| `extends_id` | 0/50 | 1 |  |
| `cfg_penalty` | 0/50 | 1 |  |
| `cfg_penalty_delay` | 0/50 | 1 |  |
| `cfg_late_fee` | 50/50 | 1 | 0.050000 |
| `cfg_late_fee_start` | 50/50 | 1 | 1 |
| `cfg_late_fee_stop` | 50/50 | 1 | 180 |
| `cfg_late_fee_mode` | 0/50 | 1 |  |
| `cfg_bailiff` | 50/50 | 1 | 2 |
| `cfg_sais` | 50/50 | 1 | 40 |
| `cfg_court` | 50/50 | 1 | 180 |
| `contract_id` | 50/50 | 1 | 11 |
| `administrative_fee` | 50/50 | 28 | 432.00; 194.40; 3.60 |
| `insurance` | 0/50 | 1 |  |
| `interest` | 50/50 | 28 | 567.44; 255.24; 12.56 |
| `extend` | 0/50 | 1 |  |
| `schedule` | 50/50 | 42 | a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-01";s:3:"day";d:30;s:1:"o";s:7; a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-01";s:3:"day";d:30;s:1:"o";s:6; a:3:{i:0;a:7:{s:4:"date";s:10:"2020-02-02";s:3:"day";d:30;s:1:"o";s:6: |
| `s_expire` | 7/50 | 8 | 2020-05-05; 2020-09-02; 2020-10-05 |
| `s_debt` | 7/50 | 8 | 1604.76; 1353.63; 517.33 |
| `cfg_withdrawn` | 0/50 | 1 |  |
| `o_charge` | 50/50 | 27 | 999.44; 449.64; 16.16 |
| `p_amount` | 48/50 | 49 | 1999.44; 905.00; 108.88 |
| `writeoff` | 0/50 | 1 |  |
| `writeoff_a` | 0/50 | 1 |  |
| `broker_id` | 9/50 | 3 | 13; 16 |
| `use_grid` | 0/50 | 1 |  |
| `writeoff_l` | 0/50 | 1 |  |
| `writeoff_p` | 0/50 | 1 |  |
| `important` | 0/50 | 1 |  |
| `late_fee_corr_d` | 0/50 | 1 |  |
| `late_fee_corr` | 0/50 | 1 |  |
| `cfg_interest_apr` | 0/50 | 1 |  |
| `cfg_interest_start` | 0/50 | 1 |  |
| `cfg_interest_stop` | 50/50 | 1 | 1825 |
| `apr` | 50/50 | 23 | 68.04; 68.02; 151.67 |
| `ret` | 25/50 | 26 | 2020-02-09; 2020-01-24; 2020-01-10 |
| `l_pay` | 48/50 | 49 | 2022-12-09 14:27:00; 2022-01-10 16:04:00; 2020-02-05 08:31:00 |
| `r_debt` | 7/50 | 8 | 1604.76; 1353.63; 517.33 |
| `special` | 0/50 | 1 |  |
| `l_amount` | 7/50 | 8 | 927.73; 871.86; 340.58 |
| `l_interest` | 6/50 | 7 | 475.15; 283.41; 106.99 |
| `l_late_fee` | 5/50 | 6 | 18.44; 6.25; 16.34 |
| `l_percent` | 0/50 | 1 |  |
| `insurance_ext` | 0/50 | 1 |  |
| `acts_id` | 0/50 | 1 |  |
| `sold` | 7/50 | 4 | 2021-06-16; 2021-12-14; 2022-12-20 |
| `tax1` | 0/50 | 1 |  |
| `tax2` | 0/50 | 1 |  |
| `l_tax1` | 0/50 | 1 |  |
| `l_tax2` | 0/50 | 1 |  |
| `discount_code` | 0/50 | 1 |  |
| `bank` | 46/50 | 4 | 7300; 7044; 4010 |
| `office_id` | 0/50 | 1 |  |
| `l_cinterest` | 5/50 | 6 | 20.24; 4.51; 35.60 |
| `cfg_einsurance_start` | 0/50 | 1 |  |
| `cfg_einsurance_stop` | 0/50 | 1 |  |
| `einsurance` | 0/50 | 1 |  |
| `origin_id` | 0/50 | 1 |  |
| `late_fee_stop_d` | 5/50 | 6 | 2020-09-08; 2020-10-20; 2020-10-01 |
| `late_fee_limit` | 0/50 | 1 |  |
| `plist_id` | 50/50 | 1 | 51 |
| `tax3` | 0/50 | 1 |  |
| `tax4` | 0/50 | 1 |  |
| `tax5` | 0/50 | 1 |  |
| `l_tax3` | 0/50 | 1 |  |
| `l_tax4` | 0/50 | 1 |  |
| `l_tax5` | 0/50 | 1 |  |
| `reason` | 50/50 | 4 | [1]: EUCB; [28]: GRT; [27]: Išrašas; [10]: Skambutis; [3]: Sodra; [1]: EUCB; [28]: GRT; [10]: Skambutis; [3]: Sodra; [1]: EUCB; [28]: GRT; [21]: Lojalus; [10]: Skambutis |
| `s_date` | 50/50 | 40 | 2022-12-17; 2020-03-03; 2021-08-25 |
| `admin_office_id` | 0/50 | 1 |  |
| `cfg_upt_covering` | 0/50 | 1 |  |
| `solvency_checked` | 0/50 | 1 |  |
| `currency` | 50/50 | 1 | EUR |
| `c_currency` | 50/50 | 1 | EUR |
| `o_administrative_fee` | 50/50 | 28 | 432.00; 194.40; 3.60 |
| `o_insurance` | 0/50 | 1 |  |
| `o_interest` | 50/50 | 28 | 567.44; 255.24; 12.56 |
| `tax6` | 0/50 | 1 |  |
| `tax7` | 0/50 | 1 |  |
| `l_tax6` | 0/50 | 1 |  |
| `l_tax7` | 0/50 | 1 |  |
| `dc_contact` | 30/50 | 6 | 5; 7; 4 |
| `ar` | 50/50 | 27 | 32.41; 32.36; 74.87 |
| `max_delay` | 31/50 | 26 | 267; 3; 379 |
| `cfg_interest_mode` | 0/50 | 1 |  |
| `number` | 50/50 | 2 | 1; 2 |
| `court_date` | 10/50 | 8 | 2021-09-30; 2021-05-18; 2021-11-15 |
| `admin_start_time` | 49/50 | 50 | 2020-01-02 16:50:04; 2020-01-02 18:00:32; 2020-01-02 19:59:47 |
| `api_user_id` | 49/50 | 2 | 2 |
| `credit_ip` | 50/50 | 47 | 90.131.43.161; 84.15.184.163; 188.69.209.115 |
| `issued_amount` | 1/50 | 2 | 146.58 |
| `tax8` | 0/50 | 1 |  |
| `tax9` | 0/50 | 1 |  |
| `tax10` | 0/50 | 1 |  |
| `tax11` | 0/50 | 1 |  |
| `tax12` | 0/50 | 1 |  |
| `late_fee_timer` | 0/50 | 1 |  |
| `tax_apr` | 0/50 | 1 |  |
| `cinterest` | 31/50 | 31 | 2.03; 0.19; 32.43 |
| `l_tax8` | 0/50 | 1 |  |
| `l_tax9` | 0/50 | 1 |  |
| `l_tax10` | 0/50 | 1 |  |
| `l_tax11` | 0/50 | 1 |  |
| `l_tax12` | 0/50 | 1 |  |
| `credit_domain` | 50/50 | 2 | kreditucentras.lt; www.kreditucentras.lt |
| `balance_order_id` | 50/50 | 1 | 1 |
| `investor_id` | 0/50 | 1 |  |
| `outer_system_id` | 0/50 | 1 |  |
| `outer_credit_id` | 0/50 | 1 |  |
| `o_schedule` | 50/50 | 42 | a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-01";s:3:"day";d:30;s:1:"o";s:7; a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-01";s:3:"day";d:30;s:1:"o";s:6; a:3:{i:0;a:7:{s:4:"date";s:10:"2020-02-02";s:3:"day";d:30;s:1:"o";s:6: |
| `stop_date` | 0/50 | 1 |  |
| `l_s_amount` | 7/50 | 8 | 927.73; 871.86; 340.58 |
| `l_s_interest` | 6/50 | 7 | 475.15; 283.41; 106.99 |
| `dc_contact_date` | 0/50 | 1 |  |
| `c_ar` | 0/50 | 1 |  |
| `ret_cancel` | 0/50 | 1 |  |
| `urgency` | 0/50 | 1 |  |
| `transfer_date` | 46/50 | 46 | 2020-01-02 18:18:44; 2020-01-02 18:20:50; 2020-01-03 10:28:00 |
| `deposit_ids` | 0/50 | 1 |  |
| `plist_interest` | 50/50 | 12 | 2.665000; 6.164384; 6.110000 |
| `plist_o_interest` | 50/50 | 12 | 2.665000; 6.164384; 6.110000 |
| `transfer_admin_id` | 0/50 | 1 |  |
| `employer_id` | 0/50 | 1 |  |
| `current_delay` | 26/50 | 21 | 267; 3; 379 |
| `l_s_administrative_fee` | 6/50 | 7 | 163.20; 187.60; 69.76 |
| `virtual_amount` | 0/50 | 1 |  |
| `confirm_code_date` | 0/50 | 1 |  |
| `ret_adm_fee_mode` | 0/50 | 1 |  |
| `creditline_mode` | 0/50 | 1 |  |
| `creditline_amount` | 0/50 | 1 |  |
| `schedule_type` | 0/50 | 1 |  |
| `s_payment` | 7/50 | 8 | 1604.76; 1353.63; 517.33 |
| `s_paid_number` | 43/50 | 12 | 36; 3; 20 |
| `l_administrative_fee` | 6/50 | 7 | 163.20; 187.60; 69.76 |
| `l_penalty` | 0/50 | 1 |  |
| `features_id` | 0/50 | 1 |  |
| `plist_administrative_fee` | 50/50 | 28 | 432.000000; 194.400000; 3.600000 |
| `ref` | 27/50 | 11 | https://www.google.com/; android-app://com.google.android.gm; https://www.google.co.uk/ |
| `lander` | 0/50 | 1 |  |
| `e_sign` | 0/50 | 1 |  |
| `modified` | 50/50 | 2 | 2026-06-04 13:04:13; 2026-06-04 13:04:14 |
| `representative_id` | 0/50 | 1 |  |
| `r_charge` | 50/50 | 45 | 999.44; 449.64; 8.63 |
| `confirm_code_admin` | 0/50 | 1 |  |
| `residual_amount` | 0/50 | 1 |  |
| `ret_start` | 25/50 | 26 | 2020-02-04; 2020-01-24; 2020-01-10 |
| `dc_contact_person` | 0/50 | 1 |  |
| `conditions_accepted` | 50/50 | 1 | 1 |
| `termination_date` | 0/50 | 1 |  |
| `withdraw_date` | 0/50 | 1 |  |
| `dc_contact_admin_id` | 30/50 | 4 | 33; 45; 20 |
| `debt_service_to_income_ratio` | 50/50 | 49 | 30.440000; 39.650000; 15.040000 |
| `ret_canceled` | 0/50 | 1 |  |
| `plist_options` | 0/50 | 1 |  |
| `plist_insurance` | 0/50 | 1 |  |
| `product_id` | 0/50 | 1 |  |
| `account_owner_name` | 0/50 | 1 |  |
| `discount` | 1/50 | 2 | 5 |
| `archive` | 0/50 | 1 |  |
| `category_changed` | 0/50 | 1 |  |
| `expire_wd` | 0/50 | 1 |  |

### Common naming tokens

`l` (24), `id` (22), `fee` (17), `cfg` (17), `late` (11), `interest` (10), `amount` (8), `s` (8), `date` (8), `admin` (6), `o` (6), `plist` (6)

## `export_credits_rejected.csv`

- Rows inspected: `50`
- Columns: `27`

### Business meaning

This file appears to contain rejected credit applications. It has requested amount/period/pricing, rejection reason, rejection date, channel fields, and some serialized application data.

It can be useful for modeling approval/rejection outcomes when combined with accepted credits and customer information.

### Column groups

- `identifiers_and_links`: `id`, `customer_id`, `extends_id`, `plist_id`, `broker_id`, `investor_id`, `features_id`
- `date_time_and_lifecycle`: `created`, `expire`, `rejection_date`, `admin_start_time`, `modification_date`
- `other_fields`: `period`, `charge`, `amount`, `account_number`, `reason`, `admin_name`, `data`, `offer`, `currency`, `discount_code`, `lander`, `dc_contact`, `compressed`, `c_data`, `important`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `id` | 50/50 | 50 | 30823; 49581; 110081 |
| `customer_id` | 50/50 | 44 | 18011; 24509; 45698 |
| `created` | 50/50 | 49 | 2016/11/7 10:40; 2017/8/11 11:04; 2020/1/1 13:33 |
| `period` | 50/50 | 10 | 540; 360; 90 |
| `charge` | 50/50 | 32 | 179; 351; 585 |
| `amount` | 50/50 | 15 | 200; 600; 1000 |
| `expire` | 50/50 | 29 | 2018/5/1; 2018/8/6; 2020/12/27 |
| `account_number` | 2/50 | 2 | LT140000000000045723 |
| `reason` | 50/50 | 33 | api; [20]: EUCB (isip 0/ paj 900); [29]: GRT; [23]: Kita  (gavo kitur); [8]; timeout |
| `admin_name` | 41/50 | 6 | Lina.Skarbaliute; crontab; Kristina |
| `extends_id` | 0/50 | 1 |  |
| `data` | 0/50 | 1 |  |
| `offer` | 0/50 | 1 |  |
| `rejection_date` | 50/50 | 41 | 2016/12/13 10:06; 2017/8/11 11:19; 2020/1/2 08:26 |
| `currency` | 50/50 | 1 | EUR |
| `admin_start_time` | 33/50 | 34 | 2020/1/2 07:55; 2020/1/2 10:46; 2020/1/2 11:06 |
| `plist_id` | 50/50 | 2 | 44; 51 |
| `broker_id` | 16/50 | 2 | 13 |
| `discount_code` | 0/50 | 1 |  |
| `lander` | 0/50 | 1 |  |
| `dc_contact` | 0/50 | 1 |  |
| `compressed` | 40/50 | 2 | 1 |
| `c_data` | 0/50 | 1 |  |
| `investor_id` | 0/50 | 1 |  |
| `features_id` | 0/50 | 1 |  |
| `important` | 0/50 | 1 |  |
| `modification_date` | 2/50 | 2 | 2026/6/4 13:07 |

### Common naming tokens

`id` (7), `admin` (2), `data` (2), `date` (2), `customer` (1), `created` (1), `period` (1), `charge` (1), `amount` (1), `expire` (1), `account` (1), `number` (1)

## `export_credit_ext_requests.csv`

- Rows inspected: `50`
- Columns: `26`

### Business meaning

This file appears to contain extension or rollover requests for existing credits. Each row links a `customer_id` to a `credit_id` and records request/completion dates, extension period, price, status, and confirmation metadata.

It can be used to study refinancing/extension behavior after credit origination.

### Column groups

- `identifiers_and_links`: `id`, `customer_id`, `credit_id`, `investor_id`, `outer_system_id`, `outer_credit_id`, `api_user_id`, `admin_id`, `creation_admin_id`, `extension_id`
- `date_time_and_lifecycle`: `request_date`, `complete_date`, `confirm_code_date`, `expire_date`
- `other_fields`: `period`, `price`, `discount_code`, `o_price`, `credit_domain`, `amount`, `confirm_code`, `confirm_code_sent`, `lander`, `evaluation_status`, `application_status`, `application_confirmed`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `id` | 50/50 | 50 | 12526; 12557; 12565 |
| `customer_id` | 50/50 | 34 | 45743; 45800; 45885 |
| `credit_id` | 50/50 | 50 | 110219; 110385; 110593 |
| `request_date` | 50/50 | 50 | 2020/2/3 08:21; 2020/2/6 16:47; 2020/2/7 11:15 |
| `period` | 50/50 | 11 | 90; 150; 180 |
| `complete_date` | 47/50 | 48 | 2020/2/3 08:21; 2020/2/6 16:47; 2020/2/7 11:15 |
| `price` | 50/50 | 33 | 48.51; 75.5; 59.5 |
| `discount_code` | 0/50 | 1 |  |
| `o_price` | 0/50 | 1 |  |
| `credit_domain` | 0/50 | 1 |  |
| `investor_id` | 0/50 | 1 |  |
| `outer_system_id` | 0/50 | 1 |  |
| `outer_credit_id` | 0/50 | 1 |  |
| `amount` | 0/50 | 1 |  |
| `confirm_code` | 0/50 | 1 |  |
| `confirm_code_date` | 0/50 | 1 |  |
| `confirm_code_sent` | 0/50 | 1 |  |
| `lander` | 0/50 | 1 |  |
| `expire_date` | 3/50 | 4 | 2020/5/2 14:12; 2020/5/9 08:01; 2020/5/31 13:27 |
| `evaluation_status` | 0/50 | 1 |  |
| `api_user_id` | 0/50 | 1 |  |
| `admin_id` | 0/50 | 1 |  |
| `application_status` | 0/50 | 1 |  |
| `creation_admin_id` | 0/50 | 1 |  |
| `application_confirmed` | 0/50 | 1 |  |
| `extension_id` | 0/50 | 1 |  |

### Common naming tokens

`id` (10), `date` (4), `code` (4), `credit` (3), `confirm` (3), `price` (2), `outer` (2), `status` (2), `admin` (2), `application` (2), `customer` (1), `request` (1)

## `export_creditline_paydays.csv`

- Rows inspected: `50`
- Columns: `14`

### Business meaning

This file appears to contain payday snapshots for credit-line style products. It links `customer_id` and `credit_id` to monthly-like `date` rows with delay, debt, reduction, returned amount, active flag, max delay, discount, and modified time.

This is the most explicit separate time-series table found in the folder, though it is much smaller than the main credit table.

### Column groups

- `identifiers_and_links`: `id`, `customer_id`, `credit_id`
- `date_time_and_lifecycle`: `date`, `create_date`, `modified`
- `other_fields`: `delay`, `debt`, `reduction`, `ret`, `active`, `protection`, `max_delay`, `discount`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `id` | 50/50 | 50 | 2; 3; 4 |
| `customer_id` | 50/50 | 4 | 68610; 68625; 68498 |
| `credit_id` | 50/50 | 4 | 186350; 186367; 185995 |
| `date` | 50/50 | 17 | 2023-10-01; 2023-11-01; 2023-12-01 |
| `create_date` | 0/50 | 1 |  |
| `delay` | 0/50 | 1 |  |
| `debt` | 0/50 | 1 |  |
| `reduction` | 0/50 | 1 |  |
| `ret` | 0/50 | 1 |  |
| `active` | 50/50 | 1 | 1 |
| `protection` | 50/50 | 50 | 2023-10-01186350; 2023-11-01186350; 2023-12-01186350 |
| `max_delay` | 0/50 | 1 |  |
| `discount` | 0/50 | 1 |  |
| `modified` | 0/50 | 1 |  |

### Common naming tokens

`id` (3), `date` (2), `delay` (2), `customer` (1), `credit` (1), `create` (1), `debt` (1), `reduction` (1), `ret` (1), `active` (1), `protection` (1), `max` (1)

## `export_credits_decisions.csv`

- Rows inspected: `50`
- Columns: `7`

### Business meaning

This file appears to contain underwriting or approval decision details for credits. It links to loans through `credit_id` and stores serialized decision signals plus approver/confirmer IDs and approval/confirmation dates.

The `decision_info` and `info` fields likely need parsing before they are useful as model features.

### Column groups

- `identifiers_and_links`: `credit_id`, `approver_id`, `confirmer_id`
- `date_time_and_lifecycle`: `approve_date`, `confirm_date`
- `other_fields`: `decision_info`, `info`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `credit_id` | 50/50 | 50 | 110115; 110139; 110150 |
| `decision_info` | 50/50 | 4 | a:5:{i:0;a:2:{i:0;s:4:"EUCB";i:2;s:1:"1";}i:1;a:2:{i:0;s:3:"GRT";i:2;s; a:4:{i:0;a:2:{i:0;s:4:"EUCB";i:2;s:1:"1";}i:1;a:2:{i:0;s:3:"GRT";i:2;s |
| `info` | 0/50 | 1 |  |
| `approver_id` | 0/50 | 1 |  |
| `confirmer_id` | 0/50 | 1 |  |
| `approve_date` | 0/50 | 1 |  |
| `confirm_date` | 0/50 | 1 |  |

### Common naming tokens

`id` (3), `info` (2), `date` (2), `credit` (1), `decision` (1), `approver` (1), `confirmer` (1), `approve` (1), `confirm` (1)

## `credits_schedules_all.csv`

- Rows inspected: `50`
- Columns: `14`

### Business meaning

This file appears to be an expanded installment schedule table. Each row is one planned installment for a credit, linked by `customer_id` and `credit_id`.

Although it has `paid_*`, `pay_status`, and `pay_delay` columns, a full streamed scan found those fields are all zero in this export, so it does not currently behave like actual payment-history data.

### Column groups

- `identifiers_and_links`: `customer_id`, `credit_id`
- `date_time_and_lifecycle`: `pay_date`, `paid_administrative_fee`, `paid_interest`, `paid_amount`
- `other_fields`: `﻿id`, `pay_number`, `pay_administrative_fee`, `pay_interest`, `pay_amount`, `pay_sum`, `pay_status`, `pay_delay`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `﻿id` | 50/50 | 50 | 1; 2; 3 |
| `customer_id` | 50/50 | 15 | 2575; 2025; 7269 |
| `credit_id` | 50/50 | 15 | 16524; 16395; 16405 |
| `pay_number` | 50/50 | 6 | 1; 2; 3 |
| `pay_date` | 50/50 | 34 | 2014-01-12; 2014-02-12; 2014-01-04 |
| `pay_administrative_fee` | 0/50 | 1 |  |
| `pay_interest` | 50/50 | 44 | 37.80; 19.76; 94.50 |
| `pay_amount` | 50/50 | 48 | 190.98; 209.02; 477.44 |
| `pay_sum` | 50/50 | 14 | 228.78; 571.94; 112.99 |
| `paid_administrative_fee` | 0/50 | 1 |  |
| `paid_interest` | 0/50 | 1 |  |
| `paid_amount` | 0/50 | 1 |  |
| `pay_status` | 0/50 | 1 |  |
| `pay_delay` | 0/50 | 1 |  |

### Common naming tokens

`pay` (8), `paid` (3), `id` (2), `administrative` (2), `fee` (2), `interest` (2), `amount` (2), `﻿id` (1), `customer` (1), `credit` (1), `number` (1), `date` (1)

## `export (tables combined).csv`

- Rows inspected: `50`
- Columns: `357`

### Business meaning

This file appears to be a pre-joined wide export that combines customer, credit, payday, decision, and extension-request fields into one table.

It may be convenient for quick EDA, but for clean modeling it is usually safer to understand the source tables first and then build a deliberate analytical table.

### Column groups

- `identifiers_and_links`: `customer_id`, `category_id`, `contract_id`, `admin_id`, `broker_id`, `reg_form_id`, `api_user_id`, `evaluation_category_id`, `acc_status_id`, `last_credit_id`, `sub_admin_id`, `id`, `extends_id`, `acts_id`, `office_id`, `origin_id`, `plist_id`, `admin_office_id`, `balance_order_id`, `investor_id`, `outer_system_id`, `outer_credit_id`, `transfer_admin_id`, `employer_id`, `features_id`, `representative_id`, `dc_contact_admin_id`, `product_id`, `cp_payday_id`, `cp_credit_id`, `cd_credit_id`, `credit_id`, `creation_admin_id`, `extension_id`
- `date_time_and_lifecycle`: `created`, `modified`, `credits_paid`, `exts_paid`, `all_paid`, `all_expired`, `last_credit_date`, `modified_by_customer`, `applications_rejected`, `last_rejection_date`, `last_application_date`, `overpaid`, `days_to_expire`, `first_credit_date`, `last_credit_period`, `first_credit_paid_date`, `documents_attached_last_date`, `days_from_last_loan_repayment`, `current_paid_payments`, `last_payment_date`, `last_extension_date`, `last_credit_id`, `paid_credits_amount_max`, `last_login_time`, `last_credit_paid_period_percent`, `last_paid_credit_discount`, `credits_paid_before_term_percent`, `expire`, `paid`, `registered`, `cfg_late_fee_start`, `cfg_late_fee_stop`, `s_expire`, `cfg_withdrawn`, `cfg_interest_start`, `cfg_interest_stop`, `cfg_einsurance_start`, `cfg_einsurance_stop`, `late_fee_stop_d`, `s_date`, `court_date`, `admin_start_time`, `late_fee_timer`, `stop_date`, `dc_contact_date`, `transfer_date`, `transfer_admin_id`, `confirm_code_date`, `s_paid_number`, `ret_start`, `termination_date`, `withdraw_date`, `expire_wd`, `request_date`, `complete_date`, `expire_date`, `rejection_date`, `modification_date`
- `other_fields`: `login`, `contract_code`, `uin`, `temp_passw`, `passw`, `enabled`, `status`, `state`, `email`, `realname`, `surname`, `mob_phone`, `mob_phone2`, `sms_mob_phone`, `person_code`, `city`, `county`, `parish`, `village`, `address`, `zipcode`, `city2`, `county2`, `parish2`, `village2`, `address2`, `zipcode2`, `age`, `gender`, `debt_limit`, `debt`, `force_change`, `sms_enabled`, `language`, `sodra_confirm`, `workplace`, `workplace_address`, `workplace_position`, `id_number`, `passport_number`, `notes`, `login_attempts`, `reminders_disabled`, `marketing`, `exts_disabled`, `region`, `region2`, `cleared`, `birthday`, `chk2`, `chk3`, `chk4`, `chk5`, `chk6`, `chk7`, `chk8`, `chk9`, `data`, `bank`, `ch_contract`, `ref`, `req_blocked_until`, `credits`, `exts`, `delay`, `delay_max`, `important`, `ip`, `dependents`, `home_status`, `flat`, `house`, `flat2`, `house2`, `work_activities`, `work_status`, `midname`, `phone`, `work_phone`, `income`, `contact_name`, `contact_phone`, `activated`, `person_code_attempts`, `lander`, `reg_method`, `fraud`, `exaction_status`, `work_company_code`, `BDS_score`, `applications`, `company_code`, `loyalty_points`, `email2`, `use_email2`, `company_name`, `employers_ids`, `reg_confirm_method`, `all_payments_amount`, `documents_attached`, `credit_limit`, `representative_ids`, `mob_phone_failed`, `mob_phone2_failed`, `applications_disabled`, `data_use_disabled`, `chk1`, `all_credits_amount_sum`, `all_credits_charge_sum`, `region3`, `county3`, `parish3`, `village3`, `city3`, `address3`, `house3`, `flat3`, `zipcode3`, `active_credits_amount_sum`, `reg_payments_count`, `investors_ids`, `payouts`, `active_payouts`, `active_extensions`, `country`, `street`, `street2`, `vat_rate`, `id_number_validity`, `passport_number_validity`, `midname2`, `tax_id_number`, `category_changed`, `period`, `charge`, `amount`, `account_number`, `description`, `confirmed`, `penalty`, `late_fee`, `confirm_code`, `comments`, `cfg_penalty`, `cfg_penalty_delay`, `cfg_late_fee`, `cfg_late_fee_mode`, `cfg_bailiff`, `cfg_sais`, `cfg_court`, `administrative_fee`, `insurance`, `interest`, `extend`, `schedule`, `s_debt`, `o_charge`, `p_amount`, `writeoff`, `writeoff_a`, `use_grid`, `writeoff_l`, `writeoff_p`, `late_fee_corr_d`, `late_fee_corr`, `cfg_interest_apr`, `apr`, `ret`, `l_pay`, `r_debt`, `special`, `l_amount`, `l_interest`, `l_late_fee`, `l_percent`, `insurance_ext`, `sold`, `tax1`, `tax2`, `l_tax1`, `l_tax2`, `discount_code`, `l_cinterest`, `einsurance`, `late_fee_limit`, `tax3`, `tax4`, `tax5`, `l_tax3`, `l_tax4`, `l_tax5`, `reason`, `cfg_upt_covering`, `solvency_checked`, `currency`, `c_currency`, `o_administrative_fee`, `o_insurance`, `o_interest`, `tax6`, `tax7`, `l_tax6`, `l_tax7`, `dc_contact`, `ar`, `max_delay`, `cfg_interest_mode`, `number`, `credit_ip`, `issued_amount`, `tax8`, `tax9`, `tax10`, `tax11`, `tax12`, `tax_apr`, `cinterest`, `l_tax8`, `l_tax9`, `l_tax10`, `l_tax11`, `l_tax12`, `credit_domain`, `o_schedule`, `l_s_amount`, `l_s_interest`, `c_ar`, `ret_cancel`, `urgency`, `deposit_ids`, `plist_interest`, `plist_o_interest`, `current_delay`, `l_s_administrative_fee`, `virtual_amount`, `ret_adm_fee_mode`, `creditline_mode`, `creditline_amount`, `schedule_type`, `s_payment`, `l_administrative_fee`, `l_penalty`, `plist_administrative_fee`, `e_sign`, `r_charge`, `confirm_code_admin`, `residual_amount`, `dc_contact_person`, `conditions_accepted`, `debt_service_to_income_ratio`, `ret_canceled`, `plist_options`, `plist_insurance`, `account_owner_name`, `discount`, `archive`, `cd_decision_info`, `price`, `o_price`, `confirm_code_sent`, `evaluation_status`, `application_status`, `application_confirmed`, `admin_name`, `offer`, `compressed`, `c_data`

### Sample value profile

| column | filled in sample | unique in sample | examples |
|---|---:|---:|---|
| `customer_id` | 45/50 | 22 | 2358; 3324; 7328 |
| `category_id` | 50/50 | 6 | 1; 20; 5 |
| `login` | 50/50 | 26 | 8571323; 0275436; 7922414 |
| `contract_id` | 18/50 | 3 | 12; 11 |
| `contract_code` | 49/50 | 26 | a7c93c4928b023c98afbaa1fca33ea4c; 580f163bc394460bb3e7f41608eec4e2; 3bf3977d96a22ab429a8778978865438 |
| `uin` | 50/50 | 26 | 6c8338b273fc862d5320c0838562a2b4; b055212bab299f917cd434b13f4098bc; 9ece6bc8a9d69aa7816cde7043a9d1f3 |
| `temp_passw` | 50/50 | 26 | 432247; 366165; 781037 |
| `passw` | 50/50 | 26 | 817145536f3827934e8ae8791d612de9; a274cd19a80714241f4355a07fb65226; 26c6806d98704cc0825760141c10759f |
| `enabled` | 40/50 | 2 | 1 |
| `status` | 37/50 | 2 | 1 |
| `state` | 0/50 | 1 |  |
| `created` | 45/50 | 46 | 2021-06-05 07:16:44; 2023-10-13 20:19:49; 2024-07-31 13:36:20 |
| `modified` | 18/50 | 6 | 2026-06-04 13:05:29; 2026-06-04 13:04:56; 2026-06-04 13:04:15 |
| `email` | 50/50 | 26 | 2358.test@test.creditonline.eu; 3324.test@test.creditonline.eu; 7328.test@test.creditonline.eu |
| `realname` | 50/50 | 26 | Name2358 Midname2358 Surname2358; Name3324 Midname3324 Surname3324; Name7328 Surname7328 |
| `surname` | 0/50 | 1 |  |
| `mob_phone` | 50/50 | 26 | +370 61002358; +370 61003324; +370 61007328 |
| `mob_phone2` | 50/50 | 26 | +370 62002358; +370 62003324; +370 62007328 |
| `sms_mob_phone` | 0/50 | 1 |  |
| `person_code` | 50/50 | 26 | 1000002358; 1000003324; 1000007328 |
| `city` | 43/50 | 18 | Šilalė; Panevėžio r. sav.; Vilniaus r. sav. |
| `county` | 50/50 | 1 | Obfuscated |
| `parish` | 50/50 | 1 | Obfuscated |
| `village` | 50/50 | 1 | Obfuscated |
| `address` | 50/50 | 1 | Obfuscated 0-0 |
| `zipcode` | 50/50 | 1 | Obfuscated |
| `city2` | 12/50 | 5 | Elektrėnų sav.; Klaipėda; Plungė |
| `county2` | 50/50 | 1 | Obfuscated |
| `parish2` | 50/50 | 1 | Obfuscated |
| `village2` | 50/50 | 1 | Obfuscated |
| `address2` | 50/50 | 1 | Obfuscated 0-0 |
| `zipcode2` | 50/50 | 1 | Obfuscated |
| `age` | 50/50 | 16 | 46; 56; 35 |
| `gender` | 50/50 | 2 | m; f |
| `debt_limit` | 1/50 | 2 | 6000 |
| `debt` | 0/50 | 2 |  |
| `force_change` | 40/50 | 2 | 1 |
| `sms_enabled` | 0/50 | 1 |  |
| `language` | 50/50 | 1 | lt |
| `sodra_confirm` | 0/50 | 1 |  |
| `workplace` | 50/50 | 1 | Obfuscated |
| `workplace_address` | 50/50 | 26 | Obfuscated 0-2358; Obfuscated 0-3324; Obfuscated 0-7328 |
| `workplace_position` | 0/50 | 1 |  |
| `id_number` | 0/50 | 1 |  |
| `passport_number` | 0/50 | 1 |  |
| `notes` | 50/50 | 1 | Obfuscated |
| `login_attempts` | 0/50 | 1 |  |
| `reminders_disabled` | 0/50 | 1 |  |
| `marketing` | 36/50 | 3 | 1; 2 |
| `exts_disabled` | 0/50 | 1 |  |
| `region` | 50/50 | 1 | Obfuscated |
| `region2` | 50/50 | 1 | Obfuscated |
| `cleared` | 0/50 | 1 |  |
| `admin_id` | 0/50 | 1 |  |
| `birthday` | 50/50 | 1 | 1990-01-01 |
| `chk2` | 27/50 | 2 | 1 |
| `chk3` | 43/50 | 2 | 1 |
| `chk4` | 0/50 | 1 |  |
| `chk5` | 0/50 | 1 |  |
| `chk6` | 0/50 | 1 |  |
| `chk7` | 0/50 | 1 |  |
| `chk8` | 0/50 | 1 |  |
| `chk9` | 0/50 | 1 |  |
| `data` | 0/50 | 1 |  |
| `bank` | 18/50 | 4 | 7044; 7300; 4010 |
| `ch_contract` | 0/50 | 1 |  |
| `ref` | 17/50 | 2 | https://www.google.com/ |
| `req_blocked_until` | 0/50 | 1 |  |
| `credits` | 18/50 | 2 | 1 |
| `exts` | 0/50 | 1 |  |
| `credits_paid` | 18/50 | 2 | 1 |
| `exts_paid` | 0/50 | 1 |  |
| `all_paid` | 18/50 | 2 | 1 |
| `all_expired` | 1/50 | 2 | 1 |
| `delay` | 0/50 | 1 |  |
| `delay_max` | 11/50 | 4 | 146; 52; 180 |
| `important` | 0/50 | 2 |  |
| `ip` | 48/50 | 21 | 88.118.51.248; 88.119.205.175; 213.190.40.74 |
| `last_credit_date` | 18/50 | 6 | 2023-03-27; 2021-10-18; 2020-01-17 |
| `dependents` | 0/50 | 1 |  |
| `home_status` | 50/50 | 1 | Obfuscated |
| `flat` | 50/50 | 1 | Obfuscated |
| `house` | 50/50 | 1 | Obfuscated |
| `flat2` | 50/50 | 1 | Obfuscated |
| `house2` | 50/50 | 1 | Obfuscated |
| `work_activities` | 0/50 | 1 |  |
| `work_status` | 0/50 | 1 |  |
| `midname` | 0/50 | 1 |  |
| `phone` | 50/50 | 1 | Obfuscated |
| `work_phone` | 50/50 | 1 | Obfuscated |
| `income` | 0/50 | 1 |  |
| `contact_name` | 50/50 | 1 | Obfuscated |
| `contact_phone` | 50/50 | 26 | +370 63002358; +370 63003324; +370 63007328 |
| `activated` | 38/50 | 15 | 2023-10-13 20:36:16; 2024-05-28 14:48:54; 2022-11-30 18:45:01 |
| `person_code_attempts` | 0/50 | 1 |  |
| `lander` | 0/50 | 1 |  |
| `broker_id` | 12/50 | 4 | 70; 13 |
| `reg_method` | 48/50 | 3 | 3; 1 |
| `reg_form_id` | 50/50 | 1 | 1 |
| `fraud` | 0/50 | 1 |  |
| `exaction_status` | 0/50 | 1 |  |
| `work_company_code` | 50/50 | 1 | Obfuscated |
| `BDS_score` | 0/50 | 1 |  |
| `modified_by_customer` | 27/50 | 9 | 2023-10-13 20:19:49; 2024-07-31 13:36:20; 2024-12-26 04:52:02 |
| `applications` | 0/50 | 1 |  |
| `applications_rejected` | 45/50 | 6 | 1; 9; 2 |
| `last_rejection_date` | 45/50 | 15 | 2025-03-27; 2023-10-16; 2025-03-28 |
| `last_application_date` | 0/50 | 1 |  |
| `api_user_id` | 0/50 | 1 |  |
| `evaluation_category_id` | 0/50 | 1 |  |
| `overpaid` | 0/50 | 2 |  |
| `company_code` | 0/50 | 1 |  |
| `days_to_expire` | 0/50 | 1 |  |
| `first_credit_date` | 18/50 | 6 | 2023-03-27; 2021-10-18; 2020-01-17 |
| `loyalty_points` | 0/50 | 1 |  |
| `acc_status_id` | 0/50 | 1 |  |
| `email2` | 50/50 | 26 | 2358.2.test@test.creditonline.eu; 3324.2.test@test.creditonline.eu; 7328.2.test@test.creditonline.eu |
| `use_email2` | 0/50 | 1 |  |
| `company_name` | 50/50 | 1 | Obfuscated |
| `employers_ids` | 0/50 | 1 |  |
| `reg_confirm_method` | 38/50 | 3 | payment; contract |
| `last_credit_period` | 0/50 | 1 |  |
| `first_credit_paid_date` | 18/50 | 6 | 2024-11-11; 2021-11-22; 2023-01-18 |
| `all_payments_amount` | 45/50 | 10 | 0.01; 0.11; 0.20 |
| `documents_attached` | 40/50 | 15 | 2; 13; 16 |
| `documents_attached_last_date` | 40/50 | 16 | 2022-01-19; 2025-02-03; 2025-05-09 |
| `days_from_last_loan_repayment` | 18/50 | 6 | 569; 1654; 1232 |
| `current_paid_payments` | 0/50 | 1 |  |
| `last_payment_date` | 45/50 | 20 | 2011-03-12; 2023-10-13; 2013-09-05 |
| `credit_limit` | 0/50 | 1 |  |
| `representative_ids` | 0/50 | 1 |  |
| `last_extension_date` | 0/50 | 1 |  |
| `mob_phone_failed` | 0/50 | 1 |  |
| `mob_phone2_failed` | 0/50 | 1 |  |
| `applications_disabled` | 0/50 | 1 |  |
| `data_use_disabled` | 0/50 | 1 |  |
| `chk1` | 0/50 | 1 |  |
| `all_credits_amount_sum` | 18/50 | 5 | 1000.00; 200.00; 900.00 |
| `all_credits_charge_sum` | 18/50 | 6 | 999.13; 157.92; 899.28 |
| `region3` | 50/50 | 1 | Obfuscated |
| `county3` | 50/50 | 1 | Obfuscated |
| `parish3` | 50/50 | 1 | Obfuscated |
| `village3` | 50/50 | 1 | Obfuscated |
| `city3` | 0/50 | 1 |  |
| `address3` | 50/50 | 1 | Obfuscated 0-0 |
| `house3` | 50/50 | 1 | Obfuscated |
| `flat3` | 50/50 | 1 | Obfuscated |
| `zipcode3` | 50/50 | 1 | Obfuscated |
| `active_credits_amount_sum` | 0/50 | 1 |  |
| `reg_payments_count` | 45/50 | 4 | 1; 2; 3 |
| `investors_ids` | 0/50 | 1 |  |
| `payouts` | 0/50 | 1 |  |
| `active_payouts` | 0/50 | 1 |  |
| `active_extensions` | 0/50 | 1 |  |
| `country` | 50/50 | 1 | OB |
| `street` | 50/50 | 1 | Obfuscated |
| `street2` | 50/50 | 1 | Obfuscated |
| `vat_rate` | 0/50 | 1 |  |
| `id_number_validity` | 0/50 | 1 |  |
| `passport_number_validity` | 0/50 | 1 |  |
| `last_credit_id` | 18/50 | 6 | 178356; 149449; 111236 |
| `paid_credits_amount_max` | 18/50 | 5 | 1000.00; 200.00; 900.00 |
| `last_login_time` | 34/50 | 12 | 2023-10-13 20:56:02; 2025-06-06 13:20:53; 2023-03-30 12:53:38 |
| `midname2` | 50/50 | 1 | Obfuscated |
| `sub_admin_id` | 0/50 | 1 |  |
| `last_credit_paid_period_percent` | 18/50 | 5 | 99; 7; 102 |
| `last_paid_credit_discount` | 0/50 | 1 |  |
| `credits_paid_before_term_percent` | 18/50 | 5 | 99; 7; 100 |
| `tax_id_number` | 50/50 | 1 | Obfuscated |
| `category_changed` | 0/50 | 2 |  |
| `id` | 45/50 | 46 | 141380; 187694; 204174 |
| `period` | 45/50 | 20 | 90; 300; 720 |
| `charge` | 41/50 | 31 | 48.51; 267.80; 1999.60 |
| `amount` | 44/50 | 20 | 300.00; 550.00; 2000.00 |
| `expire` | 45/50 | 44 | 2021-09-03; 2024-08-14; 2024-11-01 |
| `account_number` | 18/50 | 10 | LT790000000000002358; LT400000000000007328; LT230000000000008216 |
| `description` | 18/50 | 6 | internetApi; changed (90,300.00); internetApi; changed (1020,800.00); internetApi; changed (930,300.00) |
| `confirmed` | 18/50 | 2 | 1 |
| `paid` | 18/50 | 6 | 2024-11-11 10:04:00; 2021-11-22 19:30:00; 2023-01-18 17:02:00 |
| `penalty` | 0/50 | 2 |  |
| `late_fee` | 11/50 | 5 | 10.11; 10.25; 2.12 |
| `registered` | 18/50 | 6 | 2023-03-27 12:12:02; 2021-10-18 13:27:24; 2020-01-17 16:50:24 |
| `confirm_code` | 0/50 | 1 |  |
| `comments` | 18/50 | 2 | Obfuscated |
| `extends_id` | 0/50 | 2 |  |
| `cfg_penalty` | 0/50 | 1 |  |
| `cfg_penalty_delay` | 0/50 | 1 |  |
| `cfg_late_fee` | 18/50 | 2 | 0.050000 |
| `cfg_late_fee_start` | 18/50 | 2 | 1 |
| `cfg_late_fee_stop` | 18/50 | 2 | 180 |
| `cfg_late_fee_mode` | 0/50 | 2 |  |
| `cfg_bailiff` | 18/50 | 2 | 2 |
| `cfg_sais` | 18/50 | 2 | 40 |
| `cfg_court` | 18/50 | 2 | 180 |
| `administrative_fee` | 18/50 | 6 | 177.20; 38.40; 388.80 |
| `insurance` | 0/50 | 2 |  |
| `interest` | 18/50 | 6 | 821.93; 119.52; 510.48 |
| `extend` | 0/50 | 2 |  |
| `schedule` | 18/50 | 6 | a:20:{i:0;a:7:{s:4:"date";s:10:"2023-04-26";s:3:"day";d:30;s:1:"o";s:7; a:16:{i:0;a:7:{s:4:"date";s:10:"2021-11-17";s:3:"day";d:30;s:1:"o";s:6; a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-16";s:3:"day";d:30;s:1:"o";s:6 |
| `s_expire` | 0/50 | 2 |  |
| `s_debt` | 0/50 | 2 |  |
| `cfg_withdrawn` | 0/50 | 2 |  |
| `o_charge` | 18/50 | 6 | 999.20; 157.92; 899.28 |
| `p_amount` | 18/50 | 6 | 1730.05; 219.40; 1819.28 |
| `writeoff` | 0/50 | 2 |  |
| `writeoff_a` | 0/50 | 2 |  |
| `use_grid` | 0/50 | 2 |  |
| `writeoff_l` | 0/50 | 2 |  |
| `writeoff_p` | 0/50 | 2 |  |
| `late_fee_corr_d` | 0/50 | 2 |  |
| `late_fee_corr` | 0/50 | 2 |  |
| `cfg_interest_apr` | 0/50 | 2 |  |
| `cfg_interest_start` | 0/50 | 2 |  |
| `cfg_interest_stop` | 18/50 | 2 | 1825 |
| `apr` | 18/50 | 6 | 136.47; 150.61; 68.02 |
| `ret` | 6/50 | 3 | 2021-11-27 |
| `l_pay` | 18/50 | 6 | 2024-11-11 10:04:00; 2021-11-22 19:30:00; 2023-01-18 17:02:00 |
| `r_debt` | 0/50 | 2 |  |
| `special` | 0/50 | 1 |  |
| `l_amount` | 0/50 | 2 |  |
| `l_interest` | 0/50 | 2 |  |
| `l_late_fee` | 0/50 | 2 |  |
| `l_percent` | 0/50 | 2 |  |
| `insurance_ext` | 0/50 | 2 |  |
| `acts_id` | 0/50 | 2 |  |
| `sold` | 0/50 | 2 |  |
| `tax1` | 0/50 | 2 |  |
| `tax2` | 0/50 | 2 |  |
| `l_tax1` | 0/50 | 2 |  |
| `l_tax2` | 0/50 | 2 |  |
| `discount_code` | 0/50 | 1 |  |
| `office_id` | 0/50 | 2 |  |
| `l_cinterest` | 0/50 | 2 |  |
| `cfg_einsurance_start` | 0/50 | 2 |  |
| `cfg_einsurance_stop` | 0/50 | 2 |  |
| `einsurance` | 0/50 | 2 |  |
| `origin_id` | 0/50 | 2 |  |
| `late_fee_stop_d` | 0/50 | 2 |  |
| `late_fee_limit` | 0/50 | 2 |  |
| `plist_id` | 45/50 | 5 | 51; 55; 57 |
| `tax3` | 0/50 | 2 |  |
| `tax4` | 0/50 | 2 |  |
| `tax5` | 0/50 | 2 |  |
| `l_tax3` | 0/50 | 2 |  |
| `l_tax4` | 0/50 | 2 |  |
| `l_tax5` | 0/50 | 2 |  |
| `reason` | 45/50 | 31 | timeout; [4]: Sodra NEDIRBA; [32]: Klientas persigalvojo (NEBEDOMINA) |
| `s_date` | 18/50 | 6 | 2024-03-21; 2021-12-17; 2023-01-01 |
| `admin_office_id` | 0/50 | 2 |  |
| `cfg_upt_covering` | 0/50 | 2 |  |
| `solvency_checked` | 0/50 | 2 |  |
| `currency` | 45/50 | 2 | EUR |
| `c_currency` | 18/50 | 2 | EUR |
| `o_administrative_fee` | 18/50 | 6 | 240.00; 38.40; 388.80 |
| `o_insurance` | 0/50 | 2 |  |
| `o_interest` | 18/50 | 6 | 759.20; 119.52; 510.48 |
| `tax6` | 0/50 | 2 |  |
| `tax7` | 0/50 | 2 |  |
| `l_tax6` | 0/50 | 2 |  |
| `l_tax7` | 0/50 | 2 |  |
| `dc_contact` | 0/50 | 2 |  |
| `ar` | 18/50 | 5 | 74.32; 74.62; 32.39 |
| `max_delay` | 11/50 | 5 | 146; 52; 180 |
| `cfg_interest_mode` | 0/50 | 2 |  |
| `number` | 18/50 | 2 | 1 |
| `court_date` | 10/50 | 4 | 2024-03-06; 2021-11-10 |
| `admin_start_time` | 34/50 | 36 | 2023-10-16 09:09:06; 2024-05-28 14:52:18; 2022-11-30 18:51:13 |
| `credit_ip` | 18/50 | 6 | 90.131.45.231; 84.15.183.10; 88.119.138.252 |
| `issued_amount` | 0/50 | 2 |  |
| `tax8` | 0/50 | 2 |  |
| `tax9` | 0/50 | 2 |  |
| `tax10` | 0/50 | 2 |  |
| `tax11` | 0/50 | 2 |  |
| `tax12` | 0/50 | 2 |  |
| `late_fee_timer` | 0/50 | 2 |  |
| `tax_apr` | 0/50 | 2 |  |
| `cinterest` | 11/50 | 5 | 11.76; 9.75; 1.30 |
| `l_tax8` | 0/50 | 2 |  |
| `l_tax9` | 0/50 | 2 |  |
| `l_tax10` | 0/50 | 2 |  |
| `l_tax11` | 0/50 | 2 |  |
| `l_tax12` | 0/50 | 2 |  |
| `credit_domain` | 0/50 | 1 |  |
| `balance_order_id` | 18/50 | 2 | 1 |
| `investor_id` | 0/50 | 2 |  |
| `outer_system_id` | 0/50 | 1 |  |
| `outer_credit_id` | 0/50 | 1 |  |
| `o_schedule` | 18/50 | 6 | a:20:{i:0;a:7:{s:4:"date";s:10:"2023-04-26";s:3:"day";d:30;s:1:"o";s:7; a:16:{i:0;a:7:{s:4:"date";s:10:"2021-11-17";s:3:"day";d:30;s:1:"o";s:6; a:36:{i:0;a:7:{s:4:"date";s:10:"2020-02-16";s:3:"day";d:30;s:1:"o";s:6 |
| `stop_date` | 0/50 | 2 |  |
| `l_s_amount` | 0/50 | 2 |  |
| `l_s_interest` | 0/50 | 2 |  |
| `dc_contact_date` | 0/50 | 2 |  |
| `c_ar` | 0/50 | 2 |  |
| `ret_cancel` | 0/50 | 2 |  |
| `urgency` | 0/50 | 2 |  |
| `transfer_date` | 18/50 | 6 | 2023-03-27 15:16:10; 2021-10-18 14:42:58; 2020-01-17 19:34:28 |
| `deposit_ids` | 0/50 | 1 |  |
| `plist_interest` | 18/50 | 5 | 6.110000; 6.135000; 2.665000 |
| `plist_o_interest` | 18/50 | 5 | 6.110000; 6.135000; 2.665000 |
| `transfer_admin_id` | 15/50 | 4 | 58; 46 |
| `employer_id` | 0/50 | 2 |  |
| `current_delay` | 11/50 | 5 | 146; 52; 180 |
| `l_s_administrative_fee` | 0/50 | 2 |  |
| `virtual_amount` | 0/50 | 2 |  |
| `confirm_code_date` | 0/50 | 1 |  |
| `ret_adm_fee_mode` | 0/50 | 2 |  |
| `creditline_mode` | 0/50 | 2 |  |
| `creditline_amount` | 0/50 | 2 |  |
| `schedule_type` | 0/50 | 2 |  |
| `s_payment` | 0/50 | 2 |  |
| `s_paid_number` | 18/50 | 4 | 20; 16; 36 |
| `l_administrative_fee` | 0/50 | 2 |  |
| `l_penalty` | 0/50 | 2 |  |
| `features_id` | 0/50 | 2 |  |
| `plist_administrative_fee` | 18/50 | 6 | 240.000000; 38.400000; 388.800000 |
| `e_sign` | 0/50 | 1 |  |
| `representative_id` | 0/50 | 2 |  |
| `r_charge` | 18/50 | 6 | 708.18; 19.40; 899.28 |
| `confirm_code_admin` | 0/50 | 2 |  |
| `residual_amount` | 0/50 | 2 |  |
| `ret_start` | 6/50 | 3 | 2021-11-22 |
| `dc_contact_person` | 0/50 | 2 |  |
| `conditions_accepted` | 18/50 | 2 | 1 |
| `termination_date` | 0/50 | 2 |  |
| `withdraw_date` | 0/50 | 2 |  |
| `dc_contact_admin_id` | 11/50 | 3 | 45 |
| `debt_service_to_income_ratio` | 18/50 | 6 | 19.920000; 39.520000; 39.670000 |
| `ret_canceled` | 0/50 | 2 |  |
| `plist_options` | 1/50 | 2 | {"pricelist":"51"} |
| `plist_insurance` | 0/50 | 2 |  |
| `product_id` | 0/50 | 2 |  |
| `account_owner_name` | 0/50 | 1 |  |
| `discount` | 0/50 | 2 |  |
| `archive` | 0/50 | 2 |  |
| `expire_wd` | 0/50 | 2 |  |
| `cp_payday_id` | 0/50 | 1 |  |
| `cp_credit_id` | 0/50 | 1 |  |
| `cd_credit_id` | 18/50 | 6 | 178356; 149449; 111236 |
| `cd_decision_info` | 18/50 | 3 | a:4:{i:0;a:2:{i:0;s:4:"EUCB";i:2;s:1:"1";}i:1;a:2:{i:0;s:3:"GRT";i:2;s; a:5:{i:0;a:2:{i:0;s:4:"EUCB";i:2;s:1:"1";}i:1;a:2:{i:0;s:3:"GRT";i:2;s |
| `credit_id` | 0/50 | 1 |  |
| `request_date` | 0/50 | 1 |  |
| `complete_date` | 0/50 | 1 |  |
| `price` | 0/50 | 1 |  |
| `o_price` | 0/50 | 1 |  |
| `confirm_code_sent` | 0/50 | 1 |  |
| `expire_date` | 0/50 | 1 |  |
| `evaluation_status` | 0/50 | 1 |  |
| `application_status` | 0/50 | 1 |  |
| `creation_admin_id` | 0/50 | 1 |  |
| `application_confirmed` | 0/50 | 1 |  |
| `extension_id` | 0/50 | 1 |  |
| `admin_name` | 39/50 | 15 | crontab; Kornelija.D; Deimante |
| `offer` | 0/50 | 2 |  |
| `rejection_date` | 45/50 | 45 | 2025-03-27 19:46:07; 2023-10-16 09:10:44; 2025-03-28 09:56:07 |
| `compressed` | 28/50 | 3 | 1 |
| `c_data` | 0/50 | 1 |  |
| `modification_date` | 18/50 | 15 | 2026-06-04 13:07:50; 2026-06-04 13:08:44; 2026-06-04 13:08:41 |

### Common naming tokens

`id` (37), `l` (24), `date` (21), `fee` (17), `cfg` (17), `credit` (14), `last` (12), `amount` (12), `paid` (11), `late` (11), `code` (10), `interest` (10)
