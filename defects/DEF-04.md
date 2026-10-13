# DEF-04: Promo code is accepted regardless of letter case

| Field | Content |
|---|---|
| Defect ID / title | DEF-04: Promo code is accepted regardless of letter case |
| Requirement violated | REQ-F6: the only valid promo code is SAVE10 and it is case-sensitive; any other value raises ValueError |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import calculate_total`<br>2. `calculate_total(2, 'PUBLIC', 'save10')`<br>3. `calculate_total(2, 'PUBLIC', 'Save10')` |
| Expected result | ValueError for both calls |
| Actual result | Both return 35.98, i.e. the 10% promo is applied |
| Severity | **Minor** - The discount granted equals the legitimate one, so the direct loss is small; the rule is still broken. |
| Priority | **P2 - fix before release if possible** - Becomes serious as soon as codes that differ only by case are introduced; easy fix. |
| Evidence | `test_ep_invalid_promo[TC-15-promo-wrong-case] FAILED - DID NOT RAISE ValueError` (full output: ci/run1_raw_local.log) |
| Suspected root cause | _validate() and calculate_discount() normalise the code with .upper() before looking it up. (read after execution was complete) |
| Related tests | TC-15 (fails). TC-16, TC-17, TC-18 (other invalid codes) pass. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-04") |
