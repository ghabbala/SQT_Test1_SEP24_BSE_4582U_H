"""
Non-functional checks (REQ-N1 as rewritten in the requirements review, REQ-N2).

These are unit-level smoke checks only. REQ-N2 (500 concurrent users) needs a
deployed system and a load tool and is out of scope this week; TC-71 is a
single-process early-warning proxy, not evidence that REQ-N2 is met.
"""
import time

import pytest

from conftest import th


@pytest.mark.perf
def test_TC_71_latency_smoke_p95():
    """TC-71: p95 of 2,000 sequential calculate_total calls < 10 ms (REQ-N1 rewritten)."""
    samples = []
    for i in range(2000):
        t0 = time.perf_counter()
        th.calculate_total(1 + i % 9, ("STUDENT", "STAFF", "PUBLIC")[i % 3])
        samples.append(time.perf_counter() - t0)
    samples.sort()
    p95_ms = samples[int(0.95 * len(samples))] * 1000
    assert p95_ms < 10, f"TC-71 REQ-N1: p95 latency expected < 10 ms, measured {p95_ms:.3f} ms"


@pytest.mark.parametrize("args,field", [
    pytest.param((0, "PUBLIC"), "quantity", id="TC-72a-msg-quantity"),
    pytest.param((1, "student"), "customer type", id="TC-72b-msg-customer-type"),
    pytest.param((1, "PUBLIC", "BAD"), "promo", id="TC-72c-msg-promo"),
])
def test_TC_72_error_message_names_field(args, field):
    """TC-72: every validation error message names the offending field (REQ-N1 rewritten)."""
    with pytest.raises((ValueError, TypeError)) as info:
        th.calculate_total(*args)
    assert field in str(info.value).lower(), (
        f"TC-72 REQ-N1: error message should name '{field}', got: {info.value}")
