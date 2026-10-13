"""
Shared fixtures and the known-defect (xfail) policy for the TicketHub suite.

Every test carries its test case ID (TC-nn) in its pytest id, so a test's
node id always traces back to a row in test_design/test_cases.xlsx.

Known-defect policy (see README, "xfail policy"):
    Tests whose TC ID appears in KNOWN_DEFECTS are marked
    xfail(strict=True, reason="DEF-nn ...") at collection time.
      * While the defect is present the test reports XFAIL and the pipeline is green.
      * When the defect is fixed the test XPASSes, strict mode turns that into a
        FAILURE, and the pipeline goes red until the marker is removed.
    Run with --runxfail to ignore the markers and see the raw failures.
"""
import importlib
import os
import re

import pytest

# Module under test. Defaults to src/tickethub.py (put on sys.path by pyproject).
# TICKETHUB_MODULE lets the same suite be re-run against a fixed build.
th = importlib.import_module(os.environ.get("TICKETHUB_MODULE", "tickethub"))

# TC ID -> defect ID. Filled in after the first (raw) execution, Day 5.
KNOWN_DEFECTS = {
    "TC-23": "DEF-01",            # quantity 10 rejected (REQ-F1)
    "TC-26": "DEF-02",            # bulk discount not applied at exactly 5 (REQ-F4)
    "TC-28": "DEF-03",            # discount cap 30 % instead of 25 % (REQ-F4)
    "TC-15": "DEF-04",            # promo code accepted case-insensitively (REQ-F6)
    "TC-37": "DEF-05",            # promo and bulk discounts stack (REQ-F4)
    "TC-38": "DEF-05",
    "TC-39": "DEF-05, DEF-03",    # stacks to 35 %, then capped at 30 % not 25 %
    "TC-46": "DEF-06",            # PAID --cancel--> CANCELLED, not REFUND_PENDING (REQ-F7)
    "TC-48": "DEF-06",            # blocked: REFUND_PENDING unreachable
    "TC-57": "DEF-06",            # blocked
    "TC-58": "DEF-06",            # blocked
    "TC-59": "DEF-06",            # blocked
    "TC-60": "DEF-06",            # blocked: REFUNDED unreachable
    "TC-61": "DEF-06",            # blocked
    "TC-62": "DEF-06",            # blocked
    "TC-63": "DEF-06",            # blocked
    "TC-69": "DEF-06",
    "TC-54": "DEF-07",            # cancel accepted in final state COLLECTED (REQ-F7)
    "TC-68": "DEF-07",
    "TC-29": "DEF-08",            # totals truncated, not rounded half-up (REQ-F5)
    "TC-30": "DEF-08",
    "TC-31": "DEF-08",
    "TC-40": "DEF-08",
    "TC-41": "DEF-08",
}

_TC = re.compile(r"TC[-_](\d{2,3})")


def pytest_collection_modifyitems(config, items):
    for item in items:
        m = _TC.search(item.nodeid)
        if not m:
            raise pytest.UsageError(f"{item.nodeid}: every test must carry a TC ID")
        defect = KNOWN_DEFECTS.get(f"TC-{m.group(1)}")
        if defect:
            item.add_marker(pytest.mark.xfail(strict=True, reason=f"{defect} (logged)"))


@pytest.fixture
def module():
    return th
