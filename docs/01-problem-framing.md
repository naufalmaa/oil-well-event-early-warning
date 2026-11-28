# 1 · Problem framing: Oil-Well Event Early Warning

> Agreed 21 Nov 2026 after a framing review. Changes after this point need an ADR in `docs/decisions/`.

## Summary

Offshore wells sometimes drift into undesirable events (hydrate, scaling, sudden water increase, valve problems) that end in unplanned shut-ins and deferred production. Many of these events have a **transient phase**: a period in which the event is already developing but has not yet reached its stable, fully developed state. This project tests whether a model watching the sensors minute by minute can warn the production engineer **during that phase**, earlier than a simple threshold rule, without flooding them with false alarms.

| Question | Answer |
|---|---|
| Who uses the prediction? | **Production engineer on duty** (decision owner). Control-room operators carry out the actions the engineer decides on. |
| What decision does it change? | "Do I need to investigate this well **now**, before the event fully develops?" The alert triggers an investigation; it never triggers an automatic action. |
| What happens today without it? | Fixed-threshold alarms on individual sensors plus manual trend review. This is the **baseline** the model must beat. |
| Business goal | Fewer unplanned shut-ins and less deferred production. |
| Measurable proxies | (1) Minutes of early warning per event. (2) Alarm load per engineer per shift. Money and barrels are not claimed: 3W has no rate or cost data. |
| ML metrics (headline) | (1) **Event recall**. (2) **Median lead time** (minutes). (3) **False alarms per well-day** on normal operation. Each reported per event type with a 95% CI. Per-minute PR-AUC is secondary. |
| Cost of a false positive | Alarm fatigue and time spent investigating a healthy well. If it repeats, the engineer stops trusting the alerts. |
| Cost of a false negative | The event develops unnoticed: possible shut-in, deferred production, and equipment or safety risk. |
| Prediction time & horizon | A score **every minute**, using only the past window. Earliness is measured as **recall@lead ≥ H** for H = 1, 5, 15, 30, 60 minutes: the share of events alerted at least H minutes before the steady state. One model, several horizons in evaluation. |
| Is ML needed at all? | Unknown, and that is what this project tests. Hypothesis: fixed thresholds fire late on slowly developing events and too often on normal fluctuations. ML is justified only if it beats the baseline on lead time or recall within the same alarm budget. If it does not, that result is reported. |
| Non-goals | (1) No root-cause diagnosis. (2) No automatic control actions. (3) No real-time streaming: per-minute batch scoring on replayed data. (4) No remaining-useful-life prediction. (5) No performance claim for wells outside the 3W distribution (Petrobras fields). |
| Link to the real application | Proview. See "Transfer to Proview" below. |

## Scope of events

- The model learns a **binary** target: normal (0) vs any undesirable event (1–9), including its transient phase.
- **Lead time** is reported only for events with a labelled transient phase: 1, 2, 5, 6, 7, 8, 9.
- Events 3 (severe slugging) and 4 (flow instability) have no transient label, so they are reported as **detection delay** (minutes from event start to first alert).
- Every metric is broken down **per event type**, so the most frequent type (4) cannot hide weak results on rare ones.

## Alert rule (same for baseline and model)

- An alert fires when the score stays above the threshold for **3 consecutive minutes**.
- After an alert, the same well is silent for a **60-minute cooldown**.
- Both values live in `configs/default.yaml` and are recorded in an ADR.

## Success criteria

- **Alarm budget:** ≤ **0.1 false alarms per well-day** on normal operation. The threshold is chosen on train/validation wells to meet this budget; recall is read only after that.
  - Context: industrial alarm-management guidance (ISA-18.2, EEMUA 191) treats about one alarm per 10 minutes per operator as manageable, with nuisance alarms a small fraction of the total.
- **The model succeeds** if, within the alarm budget, either:
  1. its event recall is higher than the baseline's and the two 95% CIs do not overlap, or
  2. its median lead time is longer at similar recall.
- **Aspirational target:** event recall ≥ 0.85. A goal, not a pass/fail condition.

## Transfer to Proview

This project is a prototype of the early-warning **method**, built on public data (Petrobras 3W). The model itself does not transfer: 3W is 1-second offshore sensor data, while Proview works with daily records from onshore wells.

What transfers is the way the problem is framed and evaluated:

1. **Decision:** who acts on an alert, and what action it triggers.
2. **Metrics:** event recall, lead time, and false alarms per well-day instead of row-level accuracy.
3. **Time and horizon:** one model scored at Proview's natural interval (daily), evaluated at several horizons (e.g. 1, 7, 30 days).
4. **Validation:** split by well, alert rule with persistence and cooldown, and an explicit alarm budget.

Each of these will be matched to Proview's data, users, and operating rhythm, then developed further inside the running application.

## References

- Zinkevich, *Rules of ML*, rules #1–#4: https://developers.google.com/machine-learning/guides/rules-of-ml
- Vargas et al., *3W Dataset 2.0.0*: https://arxiv.org/abs/2507.01048v1
- Tatbul et al., *Precision and Recall for Time Series*: https://arxiv.org/abs/1803.03639
- Huyen, *Designing ML Systems*, ch. 2
- ISA-18.2 and EEMUA 191 (alarm management standards; paywalled)
