# DEF-02: Bulk discount is not applied when exactly 5 tickets are bought

| Field | Content |
|---|---|
| Defect ID / title | DEF-02: Bulk discount is not applied when exactly 5 tickets are bought |
| Requirement violated | REQ-F4: additional 5% if the quantity is 5 or more |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_discount, calculate_total`<br>2. `calculate_discount(5, 'PUBLIC')`<br>3. `calculate_total(5, 'PUBLIC')` |
| Expected result | rate 0.05; total 94.95 (99.95 x 0.95 = 94.9525) |
| Actual result | rate 0; total 99.95. Quantity 6 correctly gets 0.05. |
| Severity | **Major** - Every buyer of exactly 5 tickets is overcharged 5% (4.99-5.00 per order), against the published policy. |
| Priority | **P1 - fix before release** - Overcharging customers is a consumer-trust and refund issue; 5 is a common group size. |
| Evidence | `TC-26: calculate_discount(5, 'PUBLIC', None) expected rate 0.05, got 0` (full output: ci/run1_raw_local.log) |
| Suspected root cause | calculate_discount() uses quantity > BULK_THRESHOLD instead of >=. (read after execution was complete) |
| Related tests | TC-26 (fails). TC-25 and TC-27 either side of the threshold pass. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-02") |
