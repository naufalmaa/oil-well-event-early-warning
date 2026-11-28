# 0002. Split by well, test on real instances only

- **Status:** Accepted
- **Date:** 2026-11-28
- **Deciders:** Naufal (author), mentor review

## Context

P1 detects undesirable events in offshore oil wells from the Petrobras 3W dataset (v2.0.0).
The model will be used on wells it has never seen, so the evaluation must copy that situation.

Facts that shape the split:

1. **Instances from the same well are not independent.** They share a fingerprint: sensor
   calibration, operating regime, which sensors exist, typical pressure and temperature levels.
   A random split puts instances of one well in both train and test, so the model can memorise
   the well instead of learning the event. Metrics would look better than they will be in
   deployment. This is group leakage ([Kaufman et al., 2012](https://doi.org/10.1145/2382577.2382579);
   [scikit-learn, GroupShuffleSplit](https://scikit-learn.org/stable/modules/cross_validation.html#group-k-fold)).
2. **Some events are rare and live in few wells.** For example event 1 and event 6 have only a
   handful of real instances. A purely random assignment of wells could leave such an event with
   no test instance, and then we cannot say anything about it.
3. **Simulated (OLGA) and hand-drawn instances do not belong to a real well.** Their file IDs
   (`SIMULATED_00001`, `DRAWN_00001`) restart in every event folder, so they cannot be grouped
   by well, and they are not what the production engineer will see.
4. **The split is decided from metadata only.** `data/load.py::build_index` reads file names, not
   the 1.9 GB of sensor values, so the split is fast and cannot be influenced by looking at the data.

## Decision

1. **Group split by well.** Every real instance of a well goes to the same side.
2. **About 30 % of real wells go to test** (`test_size: 0.3`, `seed: 42`). With the current data this
   is 12 test wells and 28 train wells.
3. **Rare events first.** Events are processed from fewest wells to most. For each event that has at
   least two wells and no well in test yet, one of its wells is placed in test. The rest of the test
   set is filled at random up to the target size.
4. **Test is real-only.** Simulated and drawn instances get `well_id = None`, which `split.assign`
   labels `sim`. They never enter the test set. For now they are not used in training either; a later
   experiment may add them to training only.
5. **The split is frozen.** `configs/split.yaml` is produced once by `make split` and committed.
   `tests/test_leakage.py` checks that no well appears on both sides and that test contains only real
   wells. Changing the split (new seed, new data version, new code) requires a new ADR that supersedes
   this one, and all reported metrics must be recomputed.

## Consequences

**Good**

- Metrics estimate performance on unseen wells, which is how the model will be used.
- Every event with two or more wells has at least one test well.
- The test set cannot be quietly re-drawn until results look good (test-set selection leakage),
  because the committed file is the audit trail.

**Costs and risks**

- Only 12 test wells, so confidence intervals will be wide. We report 95 % bootstrap CIs resampled
  by well, not by instance.
- An event that exists in only one well cannot be tested; it is reported as "not evaluable".
- Train and test may have different event mixes; the per-event table makes this visible.
- `configs/split.yaml` lists 40 wells while the 3W paper reports 42. The data card must record the
  well count found locally and the dataset commit (`c86cc7c`) so the difference is explained.

## Alternatives considered

| Option | Why not |
|---|---|
| Random split by instance | Leaks well fingerprints, optimistic metrics. |
| Split by time (older vs newer) | Time ranges differ a lot between wells; would still mix wells. Could be a later robustness check. |
| Stratified group k-fold for the final score | Useful for model selection on train wells, but the final score keeps one frozen test set. |
| Include simulated data in test | It is not what operators see, and its IDs are not wells. |

## Event x Side Tables

| side event | test | train |
| ---  | --- | --- |
| 0     |  164   | 430 |
| 1     |    1   |   3 |
| 2     |    3   |  19 |
| 3     |    1   |  31 |
| 4     |  172   | 171 |
| 5     |    4   |   7 |
| 6     |    3   |   3 |
| 7     |    1   |  35 |
| 8     |    2   |  12 |
| 9     |   19   |  38 |
