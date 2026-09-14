# Local Git audit

Local repository initialized on `main`. No commits, staged files or remotes. Nothing has been published or uploaded.

## Final rerun

```sh
python -m lateness --data-dir data --as-of "2026-06-17T07:45:00+05:30" --out-dir results --sensitivity
python -m unittest discover -v
```

Both commands succeeded. **21 tests passed in 4.457 seconds**; see [results/test_results.txt](results/test_results.txt).

| Route | Unchanged verdict |
|---|---|
| 9 | HOLD |
| 11 | CALL_DRIVER |
| 12 | PUSH_LATE 9 min |
| 14 | CALL_DRIVER |
| 17 | CALL_DRIVER |
| 21 | HOLD |

All nine sensitivity combinations retain those actions. Hash comparisons confirmed source code, tests, data, policy, decisions.jsonl and the five calculation/report outputs are byte-for-byte unchanged. Only the fresh test log has its new execution duration. Section 13 now says “The order is retained”; its methodology, ranking and reasoning are unchanged. Related documentation marks that authorship flag resolved.

## Transcript and ledger

Exactly **9 ledger rows** still have the required three keys and verified verbatim quotes/native anchors. The raw native log was refreshed without alteration outside this repository. It includes the previously completed audit response and this cleanup request, with every persisted record through capture. SHA-256 and capture metadata are in the private manifest. An active response cannot be captured before it finishes; use the existing private export guide to refresh again after this cleanup turn if its final response must also be included. No manual reconstruction or redaction was performed.

## Publication boundary

All six cache files match the `__pycache__/` ignore rule and are absent from Git's tracked and candidate lists. Raw-session and rollout filename patterns and the private-export directory are ignored. The real private export is also outside the repository root. Normal `git add .` will omit these files; forced addition could override ignore rules and is not part of the proposed file set.

Pattern scans of the exact publication candidate files found no secrets, bearer/API-key/JWT/private-key patterns, signed URLs, email addresses or absolute local Windows paths. Required files exist and relative Markdown file links resolve. Git metadata and ignored compiled files are outside this publication set.

## Git status

On branch main; no commits yet. All 30 publication files are untracked, none staged:

```text
?? .gitignore
?? FINAL_AUDIT.md
?? LOCAL_GIT_AUDIT.md
?? README.md
?? STEERING_LEDGER.md
?? data/bookings.csv
?? data/gps_pings.csv
?? data/routes.csv
?? data/stops.csv
?? data/trips.csv
?? decision_record.md
?? decisions.jsonl
?? lateness/__init__.py
?? lateness/__main__.py
?? lateness/engine.py
?? lateness/reporting.py
?? policy.json
?? requirements.txt
?? results/evidence.json
?? results/sensitivity.md
?? results/test_results.txt
?? results/verdicts.csv
?? results/verdicts.md
?? results/worry_order.md
?? source_docs/BRIEF.md
?? source_docs/DATA_GUIDE.md
?? source_docs/HANDOFF.md
?? tests/__init__.py
?? tests/test_policy.py
?? verification.md
```

## Exact proposed first-commit file set

These are the files returned by `git ls-files --others --exclude-standard`; none have been committed:

```text
.gitignore
FINAL_AUDIT.md
LOCAL_GIT_AUDIT.md
README.md
STEERING_LEDGER.md
data/bookings.csv
data/gps_pings.csv
data/routes.csv
data/stops.csv
data/trips.csv
decision_record.md
decisions.jsonl
lateness/__init__.py
lateness/__main__.py
lateness/engine.py
lateness/reporting.py
policy.json
requirements.txt
results/evidence.json
results/sensitivity.md
results/test_results.txt
results/verdicts.csv
results/verdicts.md
results/worry_order.md
source_docs/BRIEF.md
source_docs/DATA_GUIDE.md
source_docs/HANDOFF.md
tests/__init__.py
tests/test_policy.py
verification.md
```

Proposed first commit message:

```text
Add Cityflo lateness analysis with verified decision ledger
```

No remote repository, gist, transcript upload URL, transcript upload or assignment submission was created.
