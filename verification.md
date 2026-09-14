# Local verification

Verified against the supplied snapshot at `2026-06-17T07:45:00+05:30`.

## Commands

From the submission directory, using Python with the requirements installed:

```sh
python -m lateness --data-dir data --as-of "2026-06-17T07:45:00+05:30" --out-dir results --sensitivity
python -m unittest discover -v
```

The CLI completed successfully. The test run passed **21 tests in 4.161 seconds**; the captured output is [results/test_results.txt](results/test_results.txt).

## Results and independent checks

- Exactly six route rows were generated: 9 HOLD, 11 CALL_DRIVER, 12 PUSH_LATE 9 min, 14 CALL_DRIVER, 17 CALL_DRIVER, 21 HOLD.
- All three current observations' reference deficits, medians and timetable cross-checks were compared with the accepted calculation evidence. The maximum absolute difference was **7.055689366097795e-12 minutes**, attributable to floating-point arithmetic. There is no material discrepancy.
- An independent cutoff check physically removed all **651 GPS records received after the cutoff** from a temporary input copy. Every route's evidence and action remained identical, ignoring source line numbers shifted by removing records. Original inputs were not changed.
- SHA-256 checks confirmed all five bundled CSVs are byte-for-byte identical to the original downloaded CSVs and agree with the hashes recorded in evidence.json.
- All nine combinations of 3/5/7-minute materiality and 30/60/120-second freshness preserved the six actions. The selected policy was not adjusted.
- Synthetic tests exercise other dates and route IDs, scheduled-start anchoring, receipt boundaries and future-payload poisoning, duplicate identities/payloads, malformed clocks, valid returns after teleports, negative speed, freshness/persistence boundaries, stale and origin-bound precedence, missing references, operator exclusions, conflicting reporting requests, rounding, and multiple-trip aggregation.

The generated investigation order is **17 → 14 → 11 → 12 → 21 → 9**. Its rationale and tradeoffs are recorded in [results/worry_order.md](results/worry_order.md).

## Remaining limits

Two historical runs do not establish a calibrated normal-travel distribution. Stop-polyline geometry is approximate; Route 12's position stress changes rounded delay to 8–10 minutes while preserving its material-lateness action. Booking counts do not establish actual waiting, boarding, cancellation or completion. Ambiguous future trip populations are handled conservatively.

At the implementation-verification stage, decisions.jsonl was explicitly pending quote/anchor verification and no transcript had been exported. The subsequent audit verified nine ledger rows and made an unchanged local raw-log snapshot outside the publication directory. See FINAL_AUDIT.md and STEERING_LEDGER.md. No application upload, assignment submission, notification or driver call was performed.
