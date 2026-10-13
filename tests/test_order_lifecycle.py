"""
Order life-cycle tests for TicketHub (REQ-F7) - state transition testing.

Coverage targets
  * all 5 valid transitions             (all-transitions / 0-switch coverage)
  * all 19 invalid state x event pairs  (every "invalid" cell of the state table)
  * 3 event sequences of length >= 2 that end in a final state

Each test builds a fresh Order and drives it into its start state through the
shortest *legal* event path from the specification, so tests are independent
and never rely on execution order. If that path itself misbehaves, the test
stops with a "BLOCKED: precondition" message (status Blocked in the sheet).
"""
from decimal import Decimal as D

import pytest

from conftest import th

P = pytest.param
Order, InvalidTransitionError = th.Order, th.InvalidTransitionError

# Shortest legal path to each state, taken from the REQ-F7 transition table.
PATH = {
    "CREATED": [],
    "PAID": ["pay"],
    "CANCELLED": ["cancel"],
    "COLLECTED": ["pay", "collect"],
    "REFUND_PENDING": ["pay", "cancel"],
    "REFUNDED": ["pay", "cancel", "complete_refund"],
}


def order_in(state, tc):
    o = Order(2, "PUBLIC")
    for ev in PATH[state]:
        try:
            getattr(o, ev)()
        except InvalidTransitionError as exc:
            pytest.fail(f"{tc} BLOCKED: precondition failed - legal path {PATH[state]} "
                        f"to {state} was rejected at '{ev}' in state {o.state} ({exc})")
    assert o.state == state, (
        f"{tc} BLOCKED: precondition failed - path {PATH[state]} should reach "
        f"{state}, order is in {o.state}")
    return o


# ------------------------------------------------------ initial state ----
def test_TC_42_new_order_starts_created():
    """TC-42: a new order is CREATED and carries its total (REQ-F7, REQ-F5)."""
    o = Order(3, "STAFF")
    assert o.state == "CREATED", f"TC-42 REQ-F7: expected CREATED, got {o.state}"
    assert o.total == D("53.97"), f"TC-42 REQ-F5: expected total 53.97, got {o.total}"


def test_TC_43_invalid_order_not_created():
    """TC-43: Order() rejects invalid input like calculate_total (REQ-F1)."""
    with pytest.raises(ValueError):
        Order(0, "PUBLIC")


# -------------------------------------------------- valid transitions ----
@pytest.mark.parametrize("start,event,end", [
    P("CREATED", "pay", "PAID", id="TC-44-CREATED-pay"),
    P("CREATED", "cancel", "CANCELLED", id="TC-45-CREATED-cancel"),
    P("PAID", "cancel", "REFUND_PENDING", id="TC-46-PAID-cancel"),
    P("PAID", "collect", "COLLECTED", id="TC-47-PAID-collect"),
    P("REFUND_PENDING", "complete_refund", "REFUNDED", id="TC-48-REFUND_PENDING-complete_refund"),
])
def test_valid_transitions(request, start, event, end):
    """All valid transitions from the REQ-F7 table."""
    tc = request.node.callspec.id[:5]
    o = order_in(start, tc)
    getattr(o, event)()
    assert o.state == end, f"{tc} REQ-F7: {start} --{event}--> expected {end}, got {o.state}"


# ------------------------------------------------ invalid combinations ----
INVALID = [
    ("CREATED", "collect"), ("CREATED", "complete_refund"),
    ("PAID", "pay"), ("PAID", "complete_refund"),
    ("COLLECTED", "pay"), ("COLLECTED", "cancel"),
    ("COLLECTED", "collect"), ("COLLECTED", "complete_refund"),
    ("REFUND_PENDING", "pay"), ("REFUND_PENDING", "cancel"), ("REFUND_PENDING", "collect"),
    ("REFUNDED", "pay"), ("REFUNDED", "cancel"),
    ("REFUNDED", "collect"), ("REFUNDED", "complete_refund"),
    ("CANCELLED", "pay"), ("CANCELLED", "cancel"),
    ("CANCELLED", "collect"), ("CANCELLED", "complete_refund"),
]
INVALID_PARAMS = [P(s, e, id=f"TC-{49 + i}-{s}-{e}") for i, (s, e) in enumerate(INVALID)]


@pytest.mark.parametrize("start,event", INVALID_PARAMS)
def test_invalid_transitions_rejected(request, start, event):
    """Every other state/event pair raises InvalidTransitionError and leaves the state unchanged."""
    tc = request.node.callspec.id[:5]
    o = order_in(start, tc)
    with pytest.raises(InvalidTransitionError):
        getattr(o, event)()
    assert o.state == start, f"{tc} REQ-F7: state changed from {start} to {o.state} after rejected {event}"


# --------------------------------------------------------- sequences ----
def test_TC_68_sequence_pay_collect_is_final():
    """TC-68: CREATED -pay-> PAID -collect-> COLLECTED; COLLECTED is final."""
    o = Order(4, "STUDENT")
    o.pay(); o.collect()
    assert o.state == "COLLECTED", f"TC-68 REQ-F7: expected COLLECTED, got {o.state}"
    for ev in ("pay", "cancel", "collect", "complete_refund"):
        with pytest.raises(InvalidTransitionError):
            getattr(o, ev)()
        assert o.state == "COLLECTED", f"TC-68 REQ-F7: {ev} moved final state COLLECTED to {o.state}"


def test_TC_69_sequence_pay_cancel_refund():
    """TC-69: CREATED -pay-> PAID -cancel-> REFUND_PENDING -complete_refund-> REFUNDED (final)."""
    o = Order(1, "STAFF")
    trail = [o.state]
    for ev in ("pay", "cancel", "complete_refund"):
        getattr(o, ev)()
        trail.append(o.state)
    assert trail == ["CREATED", "PAID", "REFUND_PENDING", "REFUNDED"], (
        f"TC-69 REQ-F7: expected CREATED>PAID>REFUND_PENDING>REFUNDED, got {'>'.join(trail)}")
    with pytest.raises(InvalidTransitionError):
        o.pay()
    assert o.state == "REFUNDED"


def test_TC_70_rejected_event_does_not_corrupt_path():
    """TC-70: collect (rejected) -> pay -> collect still ends in COLLECTED."""
    o = Order(2, "PUBLIC")
    with pytest.raises(InvalidTransitionError):
        o.collect()
    o.pay(); o.collect()
    assert o.state == "COLLECTED", f"TC-70 REQ-F7: expected COLLECTED, got {o.state}"
