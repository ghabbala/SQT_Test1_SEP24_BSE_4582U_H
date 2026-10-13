# DEF-01: Maximum quantity 10 is rejected with ValueError

| Field | Content |
|---|---|
| Defect ID / title | DEF-01: Maximum quantity 10 is rejected with ValueError |
| Requirement violated | REQ-F1: quantity is a whole number from 1 to 10 inclusive |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_total, Order`<br>2. `calculate_total(10, 'PUBLIC')`<br>3. `Order(10, 'PUBLIC')` |
| Expected result | 189.91 (10 x 19.99 = 199.90; bulk 5% -> 189.905 -> half-up 189.91); Order is created |
| Actual result | ValueError: quantity must be between 1 and 10 (from both calls). Quantity 9 and 11 behave as specified. |
| Severity | **Major** - The largest legal order cannot be placed at all; a customer buying 10 tickets is refused. |
| Priority | **P1 - fix before release** - Visible at checkout for group bookings on launch day; trivial to fix and retest. |
| Evidence | `test_bva_quantity_range[TC-23-qty-10] FAILED - ValueError: quantity must be between 1 and 10` (full output: ci/run1_raw_local.log) |
| Suspected root cause | _validate() tests quantity >= MAX_QTY instead of quantity > MAX_QTY (off-by-one on the upper limit). (read after execution was complete) |
| Related tests | TC-23 (fails). Found by three-value BVA; EP (TC-01) alone would not find it. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-01") |
