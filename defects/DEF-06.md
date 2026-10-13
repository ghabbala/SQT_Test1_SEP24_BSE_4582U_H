# DEF-06: Cancelling a paid order goes to CANCELLED, so the refund is never started

| Field | Content |
|---|---|
| Defect ID / title | DEF-06: Cancelling a paid order goes to CANCELLED, so the refund is never started |
| Requirement violated | REQ-F7: PAID --cancel--> REFUND_PENDING (money must be returned) |
| Environment | Python 3.13.16 (local), 3.10 and 3.12 (CI matrix); pytest 9.1.1; Linux x86_64; tickethub.py sha256 71e842b280aaf5b8d75d826abef0b364b2802f491a1c20cf2056d170f722c4a3 |
| Steps to reproduce | 1. `from tickethub import Order`<br>2. `o = Order(2, 'PUBLIC'); o.pay(); o.cancel()`<br>3. `print(o.state)`<br>4. `o.complete_refund()` |
| Expected result | state REFUND_PENDING; complete_refund() then moves to REFUNDED |
| Actual result | state CANCELLED; complete_refund() raises InvalidTransitionError ('complete_refund' not allowed in state CANCELLED) |
| Severity | **Critical** - A customer who paid and cancelled keeps no ticket and never gets the money back; REFUND_PENDING and REFUNDED are unreachable by the normal path. |
| Priority | **P1 - fix before release (blocker)** - Direct financial harm to customers and legal exposure; blocks 8 further tests. |
| Evidence | `TC-46: PAID --cancel--> expected REFUND_PENDING, got CANCELLED` (full output: ci/run1_raw_local.log) |
| Suspected root cause | _TRANSITIONS maps ('PAID', 'cancel') to 'CANCELLED' instead of 'REFUND_PENDING'. (read after execution was complete) |
| Related tests | TC-46, TC-69 (fail). Blocked by it: TC-48, TC-57, TC-58, TC-59, TC-60, TC-61, TC-62, TC-63. |
| Status | Open - automated test marked xfail(strict=True, reason="DEF-06") |
