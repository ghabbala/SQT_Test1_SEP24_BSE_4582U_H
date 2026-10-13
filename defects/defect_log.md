# TicketHub defect log

Template: Appendix B. One report per distinct root cause. Execution date: 9 Oct 2026 (Day 5).

| ID | Title | Requirement | Severity | Priority | Exposing tests |
|---|---|---|---|---|---|
| DEF-01 | Maximum quantity 10 is rejected with ValueError | REQ-F1 | Major | P1 | TC-23 (fails) |
| DEF-02 | Bulk discount is not applied when exactly 5 tickets are bought | REQ-F4 | Major | P1 | TC-26 (fails) |
| DEF-03 | Discount cap is 30% instead of 25% | REQ-F4 | Major | P1 | TC-28 (fails); TC-39 also fails partly because of it (see DEF-05) |
| DEF-04 | Promo code is accepted regardless of letter case | REQ-F6 | Minor | P2 | TC-15 (fails) |
| DEF-05 | Promo discount and bulk discount are added together | REQ-F4 | Major | P1 | TC-37, TC-38, TC-39 (fail) |
| DEF-06 | Cancelling a paid order goes to CANCELLED, so the refund is never started | REQ-F7 | Critical | P1 | TC-46, TC-69 (fail) |
| DEF-07 | Cancel is accepted on a COLLECTED (final) order and starts a refund | REQ-F7 | Critical | P1 | TC-54, TC-68 (fail) |
| DEF-08 | Totals are truncated instead of rounded half-up | REQ-F5 | Minor | P2 | TC-29, TC-30, TC-31, TC-40, TC-41 (fail) |
