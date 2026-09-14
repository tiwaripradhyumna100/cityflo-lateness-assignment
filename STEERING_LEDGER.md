# Verified steering ledger

9 rows are verified against the authentic native Codex transcript. Each JSONL row has exactly `decision`, `quote`, and `anchor`.

The raw log and the unchanged applicant attachment are kept outside this publication directory in a private local export. They are not reconstructed messages and are not bundled for repository publication.

Anchors use existing native `payload.id` values. For inline text, `/payload/content/0/text` and zero-based Unicode character offsets `[start,end)` locate the exact excerpt after JSON decoding. Record numbers below are lookup aids for the captured file; native IDs remain the primary anchors. JSON escaping in decisions.jsonl preserves backslashes, CR/LF and other original message characters.

The implementation request was supplied as an attachment. Its row uses the native user attachment-message ID, original file-read output ID and the original attachment line. Both records exist in the raw log, and the unchanged file is preserved beside it. This is an attachment provenance chain, not a fabricated inline message or turn number.

## 1. Enforce received_at <= as_of before live GPS evidence is used.

Exact applicant quote (original Markdown escapes retained):

```text
2. Apply received\_at <= as\_of before using GPS evidence.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [414,472)`
**Snapshot record:** 492
**Why consequential:** Prevents late-arriving Route 14 records from creating knowledge unavailable at the live cutoff. This reiterates the earlier applicant proposal.

## 2. Use historical route-progress timing as the primary clock, the timetable as a cross-check, and bookings as separate rider-impact context.

Exact applicant quote (original Markdown escapes retained):

```text
Use historical route-progress timing from June 15 and 16 as the primary lateness baseline where credible current GPS exists.
Use the published schedule as a cross-check.
Do not use rider promised\_eta as the primary route lateness clock because the data contains material promise inconsistencies.
Use bookings primarily for rider-impact context.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b7c-abf7-7bb3-a392-9185fc7579b2 | /payload/content/0/text | chars [1165,1513)`
**Snapshot record:** 456
**Why consequential:** Chooses the lateness definition and prevents inconsistent promises from becoming the route clock. The applicant subsequently accepted the reviewed policy; scheduled-start anchoring was an agent refinement, not claimed as applicant-originated here.

## 3. Accept the agent-reviewed working policy, including its recommended 60-second newest-observation freshness limit and scheduled-start-relative historical baseline.

Exact applicant quote (original Markdown escapes retained):

```text
I accept the decision policy in decision\_policy\_review\.md as the working policy for this assignment.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [0,103)`
**Snapshot record:** 492
**Why consequential:** This is acceptance of agent recommendations, not a claim the applicant invented the numbers. The preceding agent recommendation is proven at payload.id=msg_0eb2ff3b81e7a954016aa6c90f89b887d0ae92ef1e9eb9ad31, raw JSONL record 485; it explicitly states the 60-second limit and scheduled-start anchor. These gates determine whether a numerical result is defensible.

## 4. Apply five-minute unrounded materiality and round only after eligibility.

Exact applicant quote (original Markdown escapes retained):

```text
11. Apply the 5-minute unrounded materiality rule.
12. Apply rounding only after eligibility.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [1061,1154)`
**Snapshot record:** 492
**Why consequential:** Prevents a rounded 4.99-minute estimate from becoming eligible for a push and commits to the materiality boundary.

## 5. Restrict the official Route 21 assessment to TRIP_018/V-03 under the operator-7 handoff exclusion and disclose six excluded TRIP_019 bookings.

Exact applicant quote (original Markdown escapes retained):

```text
- official calculation must use TRIP\_018 / V-03 only;
- exclude TRIP\_019 / V-09 under the handoff rule;
- explicitly report that six TRIP\_019 bookings are outside the official assessment.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [1236,1426)`
**Snapshot record:** 492
**Why consequential:** Keeps the included route population visible without implying coverage of the other six bookings. Operator 7 is named explicitly in the earlier applicant proposal at payload.id=msg_01a09b7c-abf7-7bb3-a392-9185fc7579b2; this later instruction names the exact included and excluded trips.

## 6. Use the ordinary evidence-based Route 12 result rather than force zero, while disclosing the contractual-zero conflict.

Exact applicant quote (original Markdown escapes retained):

```text
- calculate it normally from evidence;
- do not force zero;
- show what result the ordinary policy produces;
- separately state the HANDOFF rev. C contractual-zero conflict.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [1443,1616)`
**Snapshot record:** 492
**Why consequential:** Preserves the material operational signal instead of suppressing it for contractual reporting. The later implementation attachment explicitly carries this treatment into the operational output.

## 7. Preserve unknown numerical lateness and apply accepted CALL_DRIVER precedence for unresolved service/telemetry problems.

Exact applicant quote (original Markdown escapes retained):

```text
- do not manufacture lateness numbers merely because historical comparison is mathematically possible;
- test whether CALL\_DRIVER takes precedence under the accepted policy.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [1645,1819)`
**Snapshot record:** 492
**Why consequential:** Prevents mathematically possible historical comparisons from becoming misleading current delay numbers for Routes 11, 14 and 17. The quote requests testing precedence under the already accepted policy, rather than hardcoding three calls.

## 8. Require source-derived, generic implementation without hardcoded route verdicts, delay values, ping IDs or June 17 outcomes.

Exact applicant quote (original Markdown escapes retained):

```text
The implementation must reproduce the accepted policy and calculations from the source CSVs. Do not hardcode route verdicts, route-specific delay numbers, GPS ping IDs, or the June 17 results.
```

**Anchor:** `raw_session.jsonl | applicant payload.id=msg_01a09b90-84cc-7ee1-83c5-ff0208562035 | attached pasted-text.txt line 5 | original file-read payload.id=ctco_01a09b90-d73e-76d2-9baa-c2befd917eb6`
**Snapshot record:** 568
**Why consequential:** Makes the fourth-morning exercise meaningful. The quote is applicant-authored attachment content, proven by the native user attachment message and original file-read output, not agent-authored tool commentary. The unchanged attachment is preserved beside the raw log.

## 9. Keep the selected policy fixed during sensitivity analysis rather than tune it to preferred labels.

Exact applicant quote (original Markdown escapes retained):

```text
The sensitivity analysis must not change the already-selected policy just to obtain preferred labels.
```

**Anchor:** `raw_session.jsonl | payload.id=msg_01a09b83-c944-7771-b984-b2bb03f83343 | /payload/content/0/text | chars [2057,2158)`
**Snapshot record:** 492
**Why consequential:** Prevents retrospective threshold selection to manufacture the expected route actions.

## Authorship and omissions

The 60-second limit and scheduled-start anchor were agent recommendations explicitly accepted through the working-policy message. They are represented as adoption, not applicant invention. No separate invented quote saying “I choose 60 seconds” is used.

No applicant-originated rows are asserted for the exact teleport heuristics, 30-second persistence spacing, ±100m stress, ambiguous-trip aggregation, or exposure-first worry order. Those are described in the decision record as agent implementation judgments within the accepted work. Overall implementation approval does not make them originally applicant-authored.

The four old placeholder rows were replaced, not retained. Their broad working-policy, operator-exclusion and zero-conflict subjects are supported above. The upload/submission boundary is real but omitted from the final analytical ledger because it is a workflow control rather than a route-decision rule. No minimum ledger count is assumed.

The earlier audit flagged section 13’s first-person wording as potentially ambiguous. At the applicant’s explicit cleanup request, it now says “The order is retained.” The order and reasoning are unchanged. The native acceptance of the implementation does not establish who originally devised that ordering.

No transcript upload URL was requested, no transcript was uploaded, and no Cityflo submission was made.
