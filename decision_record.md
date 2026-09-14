# Decision record

As-of: **2026-06-17 07:45:00 IST**. Evidence: results/evidence.json, unchanged data/*.csv and source_docs/*.md. This record commits to the operational calls produced by the CLI. No external action has been executed. Costs are expressed as booking exposure and operational consequences; neither waiting-rider counts nor rupee losses are observed.

## 1. Live knowledge precedes journey reconstruction

- **Rule:** Gate every GPS record on received_at <= as-of before any payload deduplication, quality decision or operator inference. Parse credible recorded_at as event time; no guessed clock corrections.
- **Breaking/failure case:** Route 14 / TRIP_016 has observations recorded before 07:45 but received later, starting with P-0003829 (06:57:13 device; 08:27:13 receipt). A retrospective reconstruction can look good while the live feed is blind. The rule could exclude truly available data if the server clock itself were wrong, but there is no independent clock evidence to support that exception.
- **Cost / who bears it:** A false current number could mislead the population represented by 12 bookings. A conservative call consumes ops/driver time. Retain the gate because inventing earlier knowledge violates the live task.
- **Flip evidence:** Independent audited receipt-clock correction or another location source actually available by the cutoff. Later arrivals cannot alter what ops knew then.

## 2. Event identity, timestamp defects and raw provenance

- **Rule:** Raw CSV file hash plus source row is provenance. Collapse exact seven-field non-ID event payload duplicates, not all equal ping IDs. Preserve collisions. Quarantine malformed device times and conflicting payloads at the same vehicle/event timestamp.
- **Breaking/failure case:** P-0002821 identifies a Tuesday V-05 event and a Wednesday V-11 event. The latter duplicates P-0003248's payload. A ping-ID primary key would erase a distinct event or depend on arbitrary row order. P-0001797 has `06:60:23` and cannot be reliably corrected from its nearby timestamps alone.
- **Cost / who bears it:** Losing a good GPS point can create a false gap; double-counting can manufacture persistence. This affects trust in both Route 17 history and Route 9 current evidence. Quarantining the invalid V-06 historical timestamp creates a 40-second usable-time gap, which is accepted rather than hidden by repair.
- **Flip evidence:** An authoritative unique event identifier, ingestion retry metadata, or a documented timestamp correction. Until then, retain raw evidence and explicit exclusions.

## 3. Reject impossible positions, preserve good neighbors and independent fields

- **Rule:** Use route-relative geometry with overwhelming speed/movement evidence to quarantine teleports. Do not advance the credible predecessor to a rejected point. Ordinary route offsets/speed transitions are uncertain, not automatically impossible. Negative reported speed invalidates only speed.
- **Breaking/failure case:** Route 9 P-0003148–P-0003150 are tens of km off-route with speeds of thousands of km/h. P-0003151 returns to normal; rejecting it merely for the bad predecessor transition would contaminate a good coordinate. The retained P-0003147→P-0003151 bridge is 82 seconds and about 14.35 km/h. Route 17 P-0003995 has negative speed but independently useful coordinates/time.
- **Cost / who bears it:** Keeping teleports could create a false push to 12 Route 9 bookings. Excessive rejection creates artificial stale telemetry and wastes driver goodwill. Real detours might be held as uncertain by this deliberately conservative geometry heuristic.
- **Flip evidence:** Validated diversion, corrected device clocks, route reassignment or independently confirmed positions. No such correction is supplied for the three teleport points.

## 4. Vehicle/trip association and route completeness

- **Rule:** Use unique vehicle/service date where possible; for several trips per vehicle/day require unambiguous scheduled membership. Never join GPS only on route or only on vehicle across all dates. Emit a row for every route, including NO_VERDICT where no included started trip is supported. Scheduled end does not establish completion.
- **Breaking/failure case:** Route 21 has simultaneous TRIP_018/V-03 and TRIP_019/V-09. Route-only aggregation mixes separate populations. Route 9 TRIP_013 ends exactly at 07:45; dropping it at the end boundary would erase a still-relevant route without observed arrival. On a fourth morning with overlapping same-vehicle trips, the conservative association may withhold a useful point instead of guessing.
- **Cost / who bears it:** Wrong-trip estimates can notify the wrong six-booking population on Route 21. Overly conservative joins create NO_VERDICT and investigation work. This is preferable to assigning a precise result to the wrong bus.
- **Flip evidence:** Explicit trip IDs on telemetry, dispatch/reassignment events or confirmed completion records.

## 5. Historical progress baseline anchored to scheduled start

- **Rule:** Use the two latest earlier service dates for the same route/direction. For each, interpolate elapsed time at current progress from adjacent credible forward-crossing observations, anchored to that trip's scheduled_start. No extrapolation or monotonic rewriting. Median across the two references is the point estimate; timetable-progress is a separate cross-check.
- **Breaking/failure case:** Route 12 TRIP_015 first reports at the origin at 07:15 but is scheduled at 07:05. Anchoring at first GPS would erase ten minutes. Route 21's two references yield -1.779209 and +0.463470 minutes at the latest observation: history does not even agree on the sign, though it agrees on sub-threshold operation. Recurring poor operation can be normalized by historical baselines.
- **Cost / who bears it:** Incorrect anchoring may suppress a needed message for nine Route 12 booking records. Treating historical normality as fulfilled promises could mislead six TRIP_018 bookings. Small-sample assumptions remain visible because two runs cannot calibrate reliability.
- **Flip evidence:** More credible reference runs, true stop passage/departure events, changed route geometry or authoritative revised schedules. An unsupported position produces NO_VERDICT instead of an extrapolated number.

## 6. Freshness, persistence and driver-call precedence

- **Rule:** Numerical support requires newest credible event age <=60s and three distinct observations with successive gaps <=30s. Origin-bound evidence spanning >=5 minutes after departure or unresolved service silence >5 minutes triggers CALL_DRIVER first. Stale/suspicious paths get no invented historical/timetable delay.
- **Breaking/failure case:** Route 11 P-0003518 is nine seconds old but is still near origin after 58m51s of observed scheduled-service time. Route 14's latest usable point P-0003828 is 2,886s old; Route 17's P-0004087 is 1,040s old. Route 9's 82-second quality gap shows the 60-second gate can temporarily withhold a useful estimate despite later recovery.
- **Cost / who bears it:** False freshness can mislead riders. Overreaction consumes ops time and driver/depot goodwill. Three direct-verification routes represent 36 booking records, not 36 known stranded people. The numerical cutoff is a practical cadence-based policy, not a statistically estimated optimum.
- **Flip evidence:** Current credible movement, independent location, corrected assignment or confirmed service completion. A point arriving now with an old event time does not restore freshness.

## 7. Five-minute materiality and rounding

- **Rule:** All six deficits (two references × three points) must be >=5 unrounded minutes for a push; all <5 supports HOLD if no higher-priority issue. Mixed support gives NO_VERDICT. Round the latest eligible median to nearest whole minute, halves upward, only afterward.
- **Breaking/failure case:** Route 21 references straddle zero; using only one reference would tell inconsistent stories. Both remain below even three minutes, so HOLD is defended. Route 12's latest median is 9.054793656 minutes and all six central deficits exceed 8.80 minutes. A hypothetical 4.99-minute case remains below threshold even if display rounding shows 5; tests exercise that boundary rather than falsely claiming it occurred in this extract.
- **Cost / who bears it:** A conservative threshold can suppress a useful 4.9-minute warning; an aggressive threshold burns trust with false pushes. Rounding can shift display by half a minute but cannot fix modelling error.
- **Flip evidence:** Validated service tolerances or observations/reference sensitivity crossing the chosen threshold. The 3/5/7-minute and 30/60/120s alternatives preserve the actual actions; they do not justify retuning the defaults.

## 8. Position uncertainty is not numeric precision

- **Rule:** Stress current progress by ±100m using the same reference interpolation. If materiality changes or a supported comparison becomes extrapolation, withhold the numerical action. Report the stress values without calling them a confidence interval.
- **Breaking/failure case:** Route 12's central 9-minute display can become 8 or 10 under this perturbation, but it remains above the seven-minute alternative threshold. Route 9 is close to the route endpoint; extrapolating beyond available historical progress would be inappropriate, even if the output looked reassuring. The actual tested targets remain bracketed.
- **Cost / who bears it:** Overstating minute precision encourages nine Route 12 booking holders to make plans around an uncertain figure. An overly conservative position check can withhold a useful signal. Retain the central observed progress estimate, but never describe it as a promised future arrival delay.
- **Flip evidence:** Better map matching, independent location accuracy or actual stop passage events; a perturbation changing action eligibility would make the estimate unsupported.

## 9. Promises and booking exposure remain separate

- **Rule:** Count available booking records and distinct rider IDs separately. Retain material promise-vs-schedule-reference warnings; do not repair promises to match the schedule or make them the route-level primary clock. No booking is assumed still waiting.
- **Breaking/failure case:** BKG_0190–BKG_0195 on TRIP_018 are approximately 19 minutes earlier than their schedule-derived reference; four precede departure. BKG_0184–BKG_0189 on TRIP_017 give unequal promises for the same trip/stop. R-1239 has two historical TRIP_002 bookings at different stops, illustrating why booking count is not a people count.
- **Cost / who bears it:** A historical HOLD can conceal real customer disappointment. Repairing promises would erase evidence of what riders were shown. Using every booking as a confirmed waiting rider exaggerates harm and distorts investigation priorities.
- **Flip evidence:** Boarding/cancellation records, versioned app promises, support contacts or a corrected schedule. Until then the operational table notes the promise issue and sends it to ops/product investigation, not a fabricated driver explanation.

## 10. Operator 7 scope restriction

- **Rule:** Apply excluded_operators from policy.json, infer membership only from already-available telemetry, and retain route rows/population notes. Raw source rows are never deleted. Excluded trips do not determine the operational result.
- **Breaking/failure case:** V-09/TRIP_019 has ordinary pre-cutoff cadence but is operator 7; the exclusion removes six bookings from Route 21's official assessment while V-03/TRIP_018 remains. Exclusion is not evidence that the bus is fine or its data bad.
- **Cost / who bears it:** Six of 12 Route 21 booking records are outside official coverage. A route-wide push could wrongly apply V-03's state to V-09 riders. The chosen restriction follows the explicit scope instruction at the cost of incomplete operational coverage.
- **Flip evidence:** Changed onboarding/reporting scope or an authoritative requirement to cover all vehicles. If future included trips yield conflicting numerical actions, the engine emits NO_VERDICT instead of inventing one notification number.

## 11. Route 12 contractual-zero conflict

- **Rule:** Reporting requests are configuration annotations, not measurements. Use the normal evidence-based Route 12 result and explicitly state that the contractual zero is unapplied. The engine rejects enabling operational overwrite.
- **Breaking/failure case:** HANDOFF rev. C requests zero across outputs, while TRIP_015/P-0003624 supports 8.928876 and 9.180711 minutes against the two historical references, median 9.054794; the separate timetable cross-check is 10.035137. Forcing zero would contradict the operational result.
- **Cost / who bears it:** Zero could suppress a useful warning for nine booking records; an unsupported nonzero could mislead them too. Declining zero creates a discrepancy with the contractual dashboard and a defense burden for ops/analytics. No contractual financial penalty is supplied, so none is invented.
- **Flip evidence:** Credible new operational measurements can change the operational verdict. A contractual target alone cannot. This is a deliberate departure from the literal zero convention, prioritizing the brief's trustworthy operational answer, and is not claimed as literal compliance.

## 12. Route-specific operational commitments

| Route/trip | Committed action and reproducible reason | Specific failure case/cost | Evidence that would change it |
|---|---|---|---|
| 9 / TRIP_013 | HOLD: both references and all three recent observations below five, fresh; teleports excluded | P-0003151 would be lost by naive adjacent-jump rejection. HOLD does not prove arrival; 12 bookings are only potential exposure | Credible current material progress deficit, new service issue or actual completion evidence |
| 11 / TRIP_014 | CALL_DRIVER: prolonged credible origin-bound telemetry overrides numerical arithmetic | P-0003518 may reflect a detached tracker rather than a stopped bus. Wrong assumptions about cause harm eight booked exposures or waste a call | Verified departure/current location, corrected tracker assignment or alternate service |
| 12 / TRIP_015 | PUSH_LATE 9 min: both references persist above threshold; rounding occurs last | P-0003624's minute value is position/model-sensitive. Nine bookings can be misled by presenting a progress deficit as exact ETA; forced zero hides the issue | Credible reference/current evidence crossing threshold or a service problem requiring direct verification |
| 14 / TRIP_016 | CALL_DRIVER: last available event is 48m06s old, no completion evidence | P-0003828 is not the current position; future P-0003829 cannot fix the live snapshot. Twelve booked exposures; call may ultimately reveal only a tracking fault | Current independent location, restored credible feed or confirmed completion |
| 17 / TRIP_017 | CALL_DRIVER: last available event is 17m20s old, no completion evidence | P-0004087 might be extract truncation rather than real outage. Sixteen bookings do not prove 16 people wait; promise problems have another owner | Actual service/location/completion and remaining-stop confirmation; versioned promises for app issue |
| 21 / TRIP_018 | HOLD for V-03 only: all six deficits below threshold | P-0004162's two reference deficits have different signs; both are immaterial. Six included promises are inconsistent; six excluded bookings unassessed | Material eligible deficit, changed reporting scope, corrected promise history or service issue |

## 13. Investigation order: 17, 14, 11, 12, 21, 9

- **Rule:** First direct service verification; then unresolved classification; then supported material delay; then promise/excluded-population issues; then routine monitoring. Within direct verification, order affected included booking exposure descending, then failure duration. Route ID is only a deterministic final tie-break. Rank derives from evidence, not a hardcoded route list.
- **Concrete breaking case:** This puts Route 17's 16 bookings ahead of Route 14's 12 and Route 11's eight, even though Route 11's nearly 59-minute origin-bound trace is more direct evidence of a problem and Route 14's gap is longer. Exposure-first is contestable: bookings may already have boarded or cancelled. The order is retained because all three require direct verification and, without independent rider state, booking exposure is the only complete, reproducible population signal available. It prioritizes broader potential exposure while stating that uncertainty.
- **Cost / who bears it:** Delaying the more conclusive Route 11 call could leave eight booked exposures unsupported; blindly favoring the largest booking count can chase a mere extract problem first. Three calls consume driver/depot goodwill. Route 12's nine-booking numerical warning should not be held back solely because this is the human investigation order. Route 21 needs a distinct ops/product follow-up, not an invented bus-delay push.
- **Flip evidence:** Confirmed breakdown or actual waiting riders, missed connection, emergency, completed service, acknowledged prior call or another independent incident signal. None is supplied. Such evidence would override this order rather than be hidden by the booking heuristic.

## Verification and authorship

Focused tests cover consequential causal rules and accepted-extract regression; see verification.md. Tiny floating-point differences from scalar versus vectorized projection are below 1e-8 minutes and change no output. No route verdict, delay number, ping ID or June-specific date appears in engine decision logic. Reporting policy contains the explicitly requested operator and contractual scope exceptions.

This record describes the agent's implementation judgments and the applicant-approved policy. It does not fabricate applicant quotes or transcript anchors. At implementation verification, decisions.jsonl was a pending draft. The subsequent transcript audit verified nine rows using native message IDs and attachment provenance; see STEERING_LEDGER.md. At the applicant's explicit request, section 13 now uses neutral wording; its order and reasoning are unchanged. No transcript or credentials are bundled and nothing has been submitted.
