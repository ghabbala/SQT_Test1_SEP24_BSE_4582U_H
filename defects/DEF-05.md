# DEF-05: Promo discount and bulk discount are added together

| Field | Content |
|---|---|
| Defect ID / title | DEF-05: Promo discount and bulk discount are added together |
| Requirement violated | REQ-F4: additional 10% if a valid promo code is supplied; otherwise 5% for 5 or more. The two never combine |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_discount, calculate_total`<br>2. `calculate_discount(7, 'PUBLIC', 'SAVE10')`<br>3. `calculate_discount(7, 'STAFF', 'SAVE10')`<br>4. `calculate_total(7, 'PUBLIC', 'SAVE10')` |
| Expected result | rates 0.10 and 0.20; total 125.94 (139.93 x 0.90 = 125.937) |
| Actual result | rates 0.15 and 0.25; total 118.94 |
| Severity | **Major** - Every promo order of 6+ tickets loses 5% revenue; contradicts the agreed policy. |
| Priority | **P1 - fix before release** - Large orders with a promo code are the most valuable orders at launch. |
| Evidence | `TC-37: calculate_discount(7, 'PUBLIC', 'SAVE10') expected rate 0.10, got 0.15` (full output: ci/run1_raw_local.log) |
| Suspected root cause | calculate_discount() accumulates both additions (extra += promo; extra += bulk) instead of if / elif. (read after execution was complete) |
| Related tests | TC-37, TC-38, TC-39 (fail). TC-39 (STUDENT) shows 0.30 because of DEF-05 and DEF-03 together. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-05") |
