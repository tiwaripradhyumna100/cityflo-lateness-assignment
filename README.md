# Cityflo operational lateness slice

A small offline Python command that loads five CSVs, reconstructs the information available at an as-of timestamp, compares credible route progress with two earlier service dates, and returns one operational verdict row per route. It uses pandas and NumPy only. It does not contact Cityflo, notify riders, call drivers, upload transcripts or submit the assignment.

## Run

Python 3.11 or newer is recommended. From this directory:

```sh
python -m pip install -r requirements.txt
python -m lateness --data-dir data --as-of "2026-06-17T07:45:00+05:30" --out-dir results --sensitivity
python -m unittest discover -v
```

`--as-of` requires a timezone offset; it is converted to IST for service-date matching. Naive timestamps are rejected, not guessed. For a fresh fourth morning, supply a directory with the same five files and its new as-of timestamp. Keep at least two prior service dates in the input for numerical reference support. No June-specific date or expected action is in the engine.

Optional flags:

- `--policy path/to/policy.json`: explicit thresholds and reporting scope. Default: the policy.json beside this README.
- `--out-dir path`: generated CSV, JSON and Markdown; must be outside the input directory.
- `--sensitivity`: also run the nine combinations of 3/5/7-minute materiality and 30/60/120-second freshness. The selected output policy is not retuned.

The input CSVs are bundled unchanged. `source_docs/` contains the original brief, handoff and data guide. File hashes and source CSV record line numbers are recorded in the output evidence. New as-of/data inputs replace the generated results only, not raw inputs.

## Project structure

```text
submission/
  lateness/
    __main__.py        CLI
    engine.py          ingestion, quality, geometry, reference timing, decisions
    reporting.py       CSV/JSON/Markdown and investigation order
  tests/test_policy.py focused synthetic and accepted-extract regression tests
  policy.json         explicit scope/thresholds; contractual request annotation
  requirements.txt
  data/               five unchanged source CSVs
  source_docs/        original assignment instructions
  results/
    verdicts.csv      exactly one row per route; route/verdict/note plus context
    verdicts.md       readable verdict table and three-observation calculations
    evidence.json     unrounded evidence, raw provenance, exclusions and warnings
    worry_order.md    generated, defended investigation order
    sensitivity.md    nine threshold combinations
  decision_record.md  rules, failure cases, costs and evidence that would flip calls
  decisions.jsonl     nine verified applicant decisions with native transcript IDs
  STEERING_LEDGER.md  exact quotes, provenance, consequences and authorship caveats
  FINAL_AUDIT.md      publication and transcript verification audit
  verification.md    local run and comparison record
```

## Data model and information boundary

Routes and stops are reference tables. Trips refer to route and vehicle. Bookings refer to trip and boarding stop. GPS has no trip ID: for a unique vehicle/service-date pair it belongs to that trip, including post-schedule telemetry. If a vehicle has multiple trips that day, only an unambiguous scheduled interval is assigned; overlapping/ambiguous records are quarantined rather than guessed. Booking-to-trip-to-GPS is not flattened for counts, avoiding multiplication of rider exposure.

Every GPS row first passes `received_at <= as_of`. Later payloads do not influence deduplication, quality, operator mapping or calculations. The source file hash and excluded-row count are provenance/inventory only. Device time must parse and not be later than receipt. Invalid times are preserved in audit records without correction.

The event payload is all seven non-ID GPS fields. Exact payload duplicates are collapsed with raw-row provenance retained; reused ping IDs do not erase distinct events. Unequal payloads at the same vehicle/event time are quarantined. Latitude/longitude must be finite and globally valid. Negative or implausible reported speed invalidates the speed field, not independently credible coordinates.

Overwhelming geometry/movement evidence identifies teleports without any ping-ID list: an offset above 50km combined with reported speed above 1,000km/h, or an offset above 500m combined with movement above 1,000km/h from the last credible predecessor. The last credible predecessor does not advance to a rejected point, allowing a valid return to survive. More ordinary deviations (over 500m, or implied movement over 120km/h) are retained as uncertain evidence and excluded from trusted location estimates, not asserted to be impossible. These rules reproduce the accepted three rejected points; they are conservative heuristics, not a learned road model.

## Numerical policy

- Project positions onto the ordered stop polyline using a local planar approximation; do not rewrite progress to be monotonic.
- Select the two most recent earlier service dates for the same route and direction. Require one eligible reference trip per date; when there are several, use the same vehicle only if that resolves the ambiguity. Otherwise withhold the reference. Earlier calendar dates are not hardcoded.
- At each target progress, use the first forward crossing between adjacent credible historical observations and interpolate elapsed time from **scheduled_start**. No extrapolation. Reference brackets must be no longer than 60 seconds. The accepted extract's brackets are 17–23 seconds and unambiguous.
- Deficit = current event-time elapsed from scheduled_start minus historical elapsed at the same progress. Calculate each reference separately and take their median. This is a historical **progress-time deficit**, not a predicted arrival ETA. Negative values are preserved.
- Newest credible event must be no older than 60 seconds. The latest three distinct credible observations must have successive gaps <=30 seconds. The oldest supporting point need not itself be within 60 seconds; the freshness gate is on the newest.
- Both references, on all three observations, must show >=5 unrounded minutes to permit a push. All below five supports HOLD, absent a more important service issue. Straddling the threshold yields NO_VERDICT.
- Round an eligible push's latest median to the nearest whole minute, halves upward. Rounding never makes 4.99 minutes eligible.
- A ±100m progress stress check must not reverse materiality or require extrapolation. This exposes uncertainty without retuning the selected policy. It can change the rounded display without changing the action.
- The timetable cross-check uses scheduled runtime times distance fraction and is separate from the historical baseline.

CALL_DRIVER takes precedence for persistent origin-bound evidence lasting at least five minutes after scheduled departure, or usable-event silence over five minutes on a known, unresolved service. Fresh but origin-bound GPS is not evidence of a healthy departure. Stale/suspicious routes do not receive manufactured numerical delays. Shorter staleness or unsupported history yields NO_VERDICT. Scheduled_end alone does not prove completion.

## Reporting scope and aggregation

`policy.json` excludes operator 7 explicitly, retaining raw rows and excluded booking context. It also records Route 12's contractual request for zero as an **unapplied reporting conflict**. The operational algorithm never returns a configured delay number. Enabling an operational override raises an error. Route identifiers appear only in reporting configuration and tests/documents, never in verdict logic.

For each route, evaluate started trips on the as-of service date. Keep a route row even if no trip is eligible. For multiple included trips: any justified CALL_DRIVER takes precedence; all HOLD yields HOLD; otherwise return NO_VERDICT with trip-specific evidence rather than inventing one route-wide push number. The supplied Route 21 reduces to one included trip after the explicit exclusion. Any future scoped push would require targeting the evaluated trip's riders; no notification transport is implemented.

## Results on the supplied snapshot

The exact required operational view is in [results/verdicts.md](results/verdicts.md), with machine-readable rows in [results/verdicts.csv](results/verdicts.csv).

| Route | Operational verdict |
|---|---|
| 9 | HOLD |
| 11 | CALL_DRIVER |
| 12 | PUSH_LATE 9 min |
| 14 | CALL_DRIVER |
| 17 | CALL_DRIVER |
| 21 | HOLD |

All nine requested threshold combinations preserve these actions. Latest unrounded medians are approximately -0.995149 minutes (9), 9.054794 (12), and -0.657869 (21). Other routes have no numerical delay due to direct-verification precedence. The accepted calculations are reproduced within 1e-8 minutes; tiny scalar/vector floating-point differences do not change any decision.

Investigation order: **17, 14, 11, 12, 21, 9**. The generated worry_order.md explains the rule and costs. This is a choice about human investigation, not an assertion that notifications must wait for three calls.

## Limitations and submission status

- Only two reference runs per route; their spread is not a calibrated confidence interval. A progress deficit is not an arrival guarantee. Route 12's ±100m stress medians can round to 8–10 minutes although the action remains material.
- Geometry follows stops, not actual roads. The engine does not infer robust detours, device truth or actual boarding/arrival. Conservative uncertain-position handling can create an information gap.
- Schedules and promise versions have no ingestion/revision history. Reference schema errors fail visibly. Invalid booking fields are reported separately. There are no boarding/cancellation/completion events: exposure means booking records, not confirmed stranded riders.
- Multi-trip association is deliberately conservative; ambiguous overlaps and numerically incompatible route populations yield NO_VERDICT. Ended-but-unconfirmed trips remain in scope for the service day. Very old completed services are not automatically recognized from schedule alone.
- No cloud infrastructure, database, ML model, dashboard, external API or message sender is required.
- `decisions.jsonl` now contains nine verified rows. [STEERING_LEDGER.md](STEERING_LEDGER.md) documents exact quotes and native transcript IDs, including the provenance chain for the applicant's attached implementation request. The authentic raw log is stored separately for private review, outside this publication directory. It contains personal/local metadata and signed upload URLs and must not be included in a public repository. Nothing has been uploaded or submitted. See [FINAL_AUDIT.md](FINAL_AUDIT.md) for the audit and the resolved authorship wording. See [LOCAL_GIT_AUDIT.md](LOCAL_GIT_AUDIT.md) for the final rerun and publication file list.
