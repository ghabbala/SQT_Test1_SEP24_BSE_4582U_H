# DEF-08: Totals are truncated instead of rounded half-up

| Field | Content |
|---|---|
| Defect ID / title | DEF-08: Totals are truncated instead of rounded half-up |
| Requirement violated | REQ-F5: total rounded half-up to two decimal places |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_total`<br>2. `calculate_total(3, 'STUDENT')`<br>3. `calculate_total(5, 'PUBLIC', 'SAVE10')` |
| Expected result | 47.98 (59.97 x 0.80 = 47.976) and 89.96 (99.95 x 0.90 = 89.955, exact half rounds up) |
| Actual result | 47.97 and 89.95 |
| Severity | **Minor** - At most 0.01 per order, in the customer's favour, but totals disagree with receipts and reconciliation. |
| Priority | **P2 - fix before release if possible** - Explicit financial requirement and a one-line fix; low customer impact. |
| Evidence | `TC-30: calculate_total(3, 'STUDENT', None) expected 47.98, got 47.97` (full output: ci/run1_raw_local.log) |
| Suspected root cause | calculate_total() quantizes with ROUND_DOWN instead of ROUND_HALF_UP. (read after execution was complete) |
| Related tests | TC-29, TC-30, TC-31, TC-40, TC-41 (fail). Totals whose 3rd decimal is < 5 (e.g. TC-33) pass. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-08") |
