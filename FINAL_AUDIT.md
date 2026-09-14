# Final transcript and publication audit

## Status

Nine valid rows are now in decisions.jsonl. Each has exactly `decision`, `quote`, and `anchor`. The exact quotes, native message IDs and consequential effects are shown in [STEERING_LEDGER.md](STEERING_LEDGER.md). No algorithm, thresholds, tests, verdicts or source data were changed during this audit.

Independent validation passed for all nine exact quotes and native anchors, the raw-log and attachment hashes, required-file presence, and relative links. Hash comparisons confirmed all 28 protected code, test, data, policy, dependency, result and source-instruction files are unchanged, including existing compiled files. The accepted application tests were not modified or rerun for these documentation-only changes.

The authentic native Codex JSONL log was copied without rewriting, filtering or redaction to a separate private local export. The original applicant implementation attachment was also copied unchanged. The export manifest records SHA-256 hashes and capture coverage. This is a complete snapshot of the records persisted at capture, from the first Cityflo request onward; it cannot include the not-yet-finished audit response. A final handoff that includes the entire audit turn needs a fresh byte copy after that turn finishes. Native message IDs keep the ledger anchors stable across an appended snapshot.

The raw log contains local Windows paths, email addresses and signed upload URLs. It is intentionally **outside this publication directory**. Pattern scans did not detect a literal bearer credential, recognizable API key, JWT or private key in the captured log; this does not make the full raw log suitable for public posting. No credentials or URL values are reproduced in this report. The separate private export guide explains the exact local export mechanism and its coverage limits.

## Ledger and authorship

- Explicit steering is proven for the receipt cutoff, historical primary baseline, five-minute unrounded materiality, operator exclusion and six-booking disclosure, evidence-based Route 12 treatment, numerical uncertainty/direct-verification precedence, no hardcoded outcomes, and keeping sensitivity analysis separate from policy selection.
- The 60-second freshness limit and scheduled-start anchor are recorded as **acceptance of the agent's reviewed policy**, with the preceding native agent recommendation identified for context. They are not represented as original applicant recommendations.
- The no-hardcoding quote came from the applicant's attached implementation request. Its anchor links the real native user attachment-message ID, the original file-read output ID, and the original attachment line. No invented turn number or reconstructed user message is used.
- No standalone applicant-originated entries were created for exact teleport heuristics, persistence spacing, position stress, ambiguous-trip aggregation or the exposure-first worry order. The transcript does not show those as separately originated applicant choices. Broad acceptance is not misrepresented as authorship.
- The old four placeholder rows are gone. The workflow prohibition on upload/submission was not retained as a separate analytical decision. There are no incomplete JSONL entries.

**Historical review flag (now resolved by explicit applicant request):** decision_record.md section 13 says “I keep the order.” The document's closing authorship paragraph identifies implementation judgments as the agent's, and the applicant has accepted the implementation, so there is no explicit unsupported personal-choice claim. Nevertheless, the first-person wording could be read as applicant authorship in isolation. The subsequent cleanup request authorized replacing that phrase with “The order is retained.” This replacement has now been made without changing the order or reasoning.

## Repository checks

| Check | Finding |
|---|---|
| Secrets, literal bearer tokens, API-key/JWT/private-key patterns, assigned credentials | No matches in publication text files |
| Signed upload URLs | None in publication files; present only in separate private raw log |
| Absolute Windows paths | None in publication text files; compiled cache files can embed local source paths |
| Personal information | No email addresses or applicant profile/resume content in publication text; source rider IDs are synthetic per the original brief |
| Temporary work files | No scratch scripts, raw logs or private export inside submission |
| Python caches | Six .pyc files remain in lateness/__pycache__ and tests/__pycache__; ignored by .gitignore |
| Generated outputs | Requested verdicts, evidence, sensitivity, worry order and verification log are intentional deliverables; keep them |
| Required files | CLI, dependencies, policy, five inputs, source instructions, README, decision record, verdict table, worry order and valid decisions.jsonl are present |
| Relative Markdown links | Checked for local target existence; no broken relative file links |
| Placeholders | No active incomplete ledger or implementation placeholders; references to the former draft are historical audit notes |

The attempt to remove cache files was rejected by automatic approval review: approval was required through a disabled sandbox-approval category. No cleanup deletion occurred. Existing ignore rules exclude the cache directories and .pyc files from normal Git staging. Additional ignore rules now exclude raw rollout/transcript files and .env files.

## Readiness

The subsequent cleanup initialized a local Git repository with the supplied ignore rules and resolved the first-person wording. See [LOCAL_GIT_AUDIT.md](LOCAL_GIT_AUDIT.md) for the exact publication file list and rerun results. For a directory/ZIP-based publication or gist assembled by copying files, remove or omit the six cache files manually; Git ignore rules do not sanitize an archive. The original transcript audit did not initialize a repository; the subsequent applicant-authorized cleanup did. No gist, commit or publication was created.

No Cityflo transcript upload URL was created. No transcript was uploaded and submit_assignment was not called. The raw transcript remains local and unchanged.
