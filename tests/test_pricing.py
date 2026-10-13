"""
Pricing tests for TicketHub (REQ-F1 .. REQ-F6).

Designed from Appendix A only (black-box). Expected values were calculated by
hand from the specification; workings are in test_design/test_cases.xlsx.

Money is compared as decimal.Decimal built from *strings*, never floats:
binary floating point cannot represent 19.99 exactly (19.99 == 19.989999...),
so a float comparison could pass or fail for reasons that have nothing to do
with the pricing rules. An exact Decimal comparison also catches 1-cent
rounding errors that a tolerance (pytest.approx) would hide.
"""
from decimal import Decimal as D

import pytest

from conftest import th

P = pytest.param


def _check_total(tc, req, q, ctype, promo, exp_total):
    got = th.calculate_total(q, ctype, promo)
    assert isinstance(got, D), f"{tc} {req}: total must be a Decimal, got {type(got).__name__}"
    assert got == D(exp_total), (
        f"{tc} {req}: calculate_total({q!r}, {ctype!r}, {promo!r}) "
        f"expected {exp_total}, got {got}")


def _check_rate(tc, req, q, ctype, promo, exp_rate):
    got = th.calculate_discount(q, ctype, promo)
    assert got == D(exp_rate), (
        f"{tc} {req}: calculate_discount({q!r}, {ctype!r}, {promo!r}) "
        f"expected rate {exp_rate}, got {got}")


def _check_raises(tc, req, exc, q, ctype, promo=None):
    with pytest.raises(exc) as info:
        th.calculate_total(q, ctype, promo)
    assert type(info.value) is exc, (
        f"{tc} {req}: expected exactly {exc.__name__}, got {type(info.value).__name__}")


# ---------------------------------------------------------------- C1 · EP ----
# Valid-class representatives: one value from the middle of each valid class.
@pytest.mark.parametrize("q,ctype,promo,exp", [
    P(3, "PUBLIC", None, "59.97", id="TC-01-qty-valid-3"),
    P(2, "STUDENT", None, "31.98", id="TC-08-type-STUDENT"),
    P(2, "STAFF", None, "35.98", id="TC-09-type-STAFF"),
    P(2, "PUBLIC", "SAVE10", "35.98", id="TC-14-promo-SAVE10"),
])
def test_ep_valid_classes(request, q, ctype, promo, exp):
    """EP valid classes for quantity, customer type and promo code."""
    tc = request.node.callspec.id[:5]
    _check_total(tc, "REQ-F1/F2/F6", q, ctype, promo, exp)


# Invalid quantity classes, one at a time; other inputs valid.
@pytest.mark.parametrize("q,exc", [
    P(-5, ValueError, id="TC-02-qty-below-range"),
    P(15, ValueError, id="TC-03-qty-above-range"),
    P(2.5, TypeError, id="TC-04-qty-float"),
    P("3", TypeError, id="TC-05-qty-string"),
    P(None, TypeError, id="TC-06-qty-None"),
    P(True, TypeError, id="TC-07-qty-bool"),
])
def test_ep_invalid_quantity(request, q, exc):
    """EP invalid quantity classes (REQ-F1)."""
    _check_raises(request.node.callspec.id[:5], "REQ-F1", exc, q, "PUBLIC")


@pytest.mark.parametrize("ctype", [
    P("student", id="TC-10-type-lowercase"),
    P("ALUMNI", id="TC-11-type-unknown"),
    P("", id="TC-12-type-empty"),
    P(None, id="TC-13-type-None"),
])
def test_ep_invalid_customer_type(request, ctype):
    """EP invalid customer type classes (REQ-F2)."""
    _check_raises(request.node.callspec.id[:5], "REQ-F2", ValueError, 2, ctype)


@pytest.mark.parametrize("promo", [
    P("save10", id="TC-15-promo-wrong-case"),
    P("BADCODE", id="TC-16-promo-unknown"),
    P("", id="TC-17-promo-empty"),
    P("SAVE10 ", id="TC-18-promo-trailing-space"),
])
def test_ep_invalid_promo(request, promo):
    """EP invalid promo code classes (REQ-F6)."""
    _check_raises(request.node.callspec.id[:5], "REQ-F6", ValueError, 2, "PUBLIC", promo)


# --------------------------------------------------------------- C2 · BVA ----
# Three-value BVA on the quantity range [1, 10] (PUBLIC, no promo).
@pytest.mark.parametrize("q,exp", [
    P(0, ValueError, id="TC-19-qty-0"),
    P(1, "19.99", id="TC-20-qty-1"),
    P(2, "39.98", id="TC-21-qty-2"),
    P(9, "170.91", id="TC-22-qty-9"),
    P(10, "189.91", id="TC-23-qty-10"),
    P(11, ValueError, id="TC-24-qty-11"),
])
def test_bva_quantity_range(request, q, exp):
    """BVA on quantity limits 1 and 10 (REQ-F1, REQ-F3, REQ-F5)."""
    tc = request.node.callspec.id[:5]
    if exp is ValueError:
        _check_raises(tc, "REQ-F1", ValueError, q, "PUBLIC")
    else:
        _check_total(tc, "REQ-F1", q, "PUBLIC", None, exp)


# Three-value BVA on the bulk threshold (quantity >= 5), PUBLIC, no promo.
@pytest.mark.parametrize("q,rate,exp", [
    P(4, "0", "79.96", id="TC-25-bulk-4"),
    P(5, "0.05", "94.95", id="TC-26-bulk-5"),
    P(6, "0.05", "113.94", id="TC-27-bulk-6"),
])
def test_bva_bulk_threshold(request, q, rate, exp):
    """BVA on the bulk-discount threshold of 5 tickets (REQ-F4)."""
    tc = request.node.callspec.id[:5]
    _check_rate(tc, "REQ-F4", q, "PUBLIC", None, rate)
    _check_total(tc, "REQ-F4/F5", q, "PUBLIC", None, exp)


# ---------------------------------------------------- C3 · Decision table ----
# One test per collapsed rule R1..R9; quantities 3 and 7 are off-boundary.
@pytest.mark.parametrize("q,ctype,promo,rate,exp", [
    P(3, "STUDENT", "SAVE10", "0.25", "44.98", id="TC-28-R1-student-promo-cap"),
    P(7, "STUDENT", None, "0.25", "104.95", id="TC-29-R2-student-bulk"),
    P(3, "STUDENT", None, "0.20", "47.98", id="TC-30-R3-student-none"),
    P(3, "STAFF", "SAVE10", "0.20", "47.98", id="TC-31-R4-staff-promo"),
    P(7, "STAFF", None, "0.15", "118.94", id="TC-32-R5-staff-bulk"),
    P(3, "STAFF", None, "0.10", "53.97", id="TC-33-R6-staff-none"),
    P(3, "PUBLIC", "SAVE10", "0.10", "53.97", id="TC-34-R7-public-promo"),
    P(7, "PUBLIC", None, "0.05", "132.93", id="TC-35-R8-public-bulk"),
    P(3, "PUBLIC", None, "0", "59.97", id="TC-36-R9-public-none"),
])
def test_decision_table_rules(request, q, ctype, promo, rate, exp):
    """Collapsed decision table for the discount rule (REQ-F4, REQ-F5)."""
    tc = request.node.callspec.id[:5]
    _check_rate(tc, "REQ-F4", q, ctype, promo, rate)
    _check_total(tc, "REQ-F5", q, ctype, promo, exp)


# Promo and bulk both present: promo wins, discounts never combine.
@pytest.mark.parametrize("ctype,rate,exp", [
    P("PUBLIC", "0.10", "125.94", id="TC-37-nostack-public"),
    P("STAFF", "0.20", "111.94", id="TC-38-nostack-staff"),
    P("STUDENT", "0.25", "104.95", id="TC-39-nostack-student"),
])
def test_promo_and_bulk_never_combine(request, ctype, rate, exp):
    """Cause-effect constraint: promo excludes bulk (REQ-F4)."""
    tc = request.node.callspec.id[:5]
    _check_rate(tc, "REQ-F4", 7, ctype, "SAVE10", rate)
    _check_total(tc, "REQ-F5", 7, ctype, "SAVE10", exp)


# ------------------------------------------------------ REQ-F5 rounding ----
# EP on the third decimal of the unrounded total: < 5 (TC-33), = 5, > 5.
@pytest.mark.parametrize("q,ctype,promo,exp", [
    P(5, "PUBLIC", "SAVE10", "89.96", id="TC-40-round-exact-half"),   # 89.955
    P(4, "STAFF", "SAVE10", "63.97", id="TC-41-round-above-half"),    # 63.968
])
def test_rounding_half_up(request, q, ctype, promo, exp):
    """Totals are rounded half-up to 2 d.p. (REQ-F5)."""
    _check_total(request.node.callspec.id[:5], "REQ-F5", q, ctype, promo, exp)
