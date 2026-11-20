# 4 · Split strategy & leakage audit

> Decide this **before** feature engineering. The split decides whether every later number is honest.

## Split

- Strategy: (time / group / group+time / rolling-origin)
- Why:
- Diagram: `reports/figures/02-split.png`

| Set | Period | Groups (wells/machines) | Rows | Events |
|---|---|---|---|---|
| Train | | | | |
| Validation | | | | |
| Test | | | | |

## Feature availability at prediction time

| Feature | Source column(s) | Available at time t? | Notes |
|---|---|---|---|
| | | ✅ / ❌ | |

## Leakage checklist

- [ ] No test timestamp in train (`tests/test_leakage.py::test_no_time_overlap`)
- [ ] No group in both train and test (`test_no_group_overlap`)
- [ ] Rolling windows are right-aligned and closed at t (`test_features_use_only_past`)
- [ ] Scalers / imputers fitted on train only
- [ ] Label is not derivable from a feature (target leakage)
- [ ] Duplicated or near-duplicated rows checked across splits

## References

- Kaufman, Rosset & Perlich (2012), *Leakage in Data Mining*: https://www.doi.org/10.1145/2382577.2382579
- Bergmeir & Benítez (2012), CV for time series: https://research.monash.edu/en/publications/on-the-use-of-cross-validation-for-time-series-predictor-evaluati/
- scikit-learn TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
