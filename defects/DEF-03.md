# DEF-03: Discount cap is 30% instead of 25%

| Field | Content |
|---|---|
| Defect ID / title | DEF-03: Discount cap is 30% instead of 25% |
| Requirement violated | REQ-F4: discount rate = min(type discount + additional discount, 25%) |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_discount, calculate_total`<br>2. `calculate_discount(3, 'STUDENT', 'SAVE10')`<br>3. `calculate_total(3, 'STUDENT', 'SAVE10')` |
| Expected result | rate 0.25 (20% + 10% = 30%, capped to 25%); total 44.98 (59.97 x 0.75 = 44.9775) |
| Actual result | rate 0.30; total 41.97 |
| Severity | **Major** - Every student order with SAVE10 is under-charged by 5 percentage points: direct, systematic revenue loss. |
| Priority | **P1 - fix before release** - Students are the main audience and SAVE10 will be promoted at launch. |
| Evidence | `TC-28: calculate_discount(3, 'STUDENT', 'SAVE10') expected rate 0.25, got 0.30` (full output: ci/run1_raw_local.log) |
| Suspected root cause | Constant DISCOUNT_CAP = Decimal('0.30'); the spec value is 0.25. (read after execution was complete) |
| Related tests | TC-28 (fails); TC-39 also fails partly because of it (see DEF-05). |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-03") |
