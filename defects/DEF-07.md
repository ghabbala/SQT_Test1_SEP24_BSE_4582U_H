# DEF-07: Cancel is accepted on a COLLECTED (final) order and starts a refund

| Field | Content |
|---|---|
| Defect ID / title | DEF-07: Cancel is accepted on a COLLECTED (final) order and starts a refund |
| Requirement violated | REQ-F7: COLLECTED is a final state; every non-listed state/event pair raises InvalidTransitionError and leaves the state unchanged |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import Order`<br>2. `o = Order(2, 'PUBLIC'); o.pay(); o.collect(); o.cancel()`<br>3. `print(o.state)`<br>4. `o.complete_refund(); print(o.state)` |
| Expected result | o.cancel() raises InvalidTransitionError; state stays COLLECTED |
| Actual result | No exception; state becomes REFUND_PENDING, and complete_refund() then gives REFUNDED |
| Severity | **Critical** - A buyer can collect tickets, attend, and still be refunded: a fraud route and a direct loss on every abuse. |
| Priority | **P1 - fix before release (blocker)** - With DEF-06 present this is the only path that reaches REFUNDED, so it will be found and used. |
| Evidence | `test_invalid_transitions_rejected[TC-54-COLLECTED-cancel] FAILED - DID NOT RAISE InvalidTransitionError` (full output: ci/run1_raw_local.log) |
| Suspected root cause | _TRANSITIONS contains an extra entry ('COLLECTED', 'cancel') -> 'REFUND_PENDING'. (read after execution was complete) |
| Related tests | TC-54, TC-68 (fail). The other 17 invalid-pair tests that could run pass. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-07") |
