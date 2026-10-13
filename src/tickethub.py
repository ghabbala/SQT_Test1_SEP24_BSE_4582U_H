"""
tickethub.py - TicketHub campus event ticket module (system under test).

Public API
    calculate_discount(quantity, customer_type, promo_code=None) -> Decimal   (fraction, e.g. Decimal("0.25"))
    calculate_total(quantity, customer_type, promo_code=None)    -> Decimal   (2 d.p.)
    Order(quantity, customer_type, promo_code=None)
        .state, .total, .pay(), .cancel(), .collect(), .complete_refund()
    InvalidTransitionError

See the Requirements Specification (REQ-F1 .. REQ-F7) in the project brief.
"""
from decimal import Decimal, ROUND_DOWN

UNIT_PRICE = Decimal("19.99")
MIN_QTY, MAX_QTY = 1, 10
TYPE_DISCOUNT = {
    "STUDENT": Decimal("0.20"),
    "STAFF": Decimal("0.10"),
    "PUBLIC": Decimal("0"),
}
BULK_THRESHOLD = 5
BULK_DISCOUNT = Decimal("0.05")
PROMO_CODES = {"SAVE10": Decimal("0.10")}
DISCOUNT_CAP = Decimal("0.30")


class InvalidTransitionError(Exception):
    """Raised when an event is not allowed in the order's current state."""


def _validate(quantity, customer_type, promo_code):
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise TypeError("quantity must be an integer")
    if quantity < MIN_QTY or quantity >= MAX_QTY:
        raise ValueError("quantity must be between 1 and 10")
    if customer_type not in TYPE_DISCOUNT:
        raise ValueError("unknown customer type")
    if promo_code is not None and str(promo_code).upper() not in PROMO_CODES:
        raise ValueError("invalid promo code")


def calculate_discount(quantity, customer_type, promo_code=None):
    _validate(quantity, customer_type, promo_code)
    extra = Decimal("0")
    if promo_code is not None:
        extra += PROMO_CODES[promo_code.upper()]
    if quantity > BULK_THRESHOLD:
        extra += BULK_DISCOUNT
    return min(TYPE_DISCOUNT[customer_type] + extra, DISCOUNT_CAP)


def calculate_total(quantity, customer_type, promo_code=None):
    rate = calculate_discount(quantity, customer_type, promo_code)
    gross = UNIT_PRICE * quantity
    return (gross * (1 - rate)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


_TRANSITIONS = {
    ("CREATED", "pay"): "PAID",
    ("CREATED", "cancel"): "CANCELLED",
    ("COLLECTED", "cancel"): "REFUND_PENDING",
    ("PAID", "cancel"): "CANCELLED",
    ("PAID", "collect"): "COLLECTED",
    ("REFUND_PENDING", "complete_refund"): "REFUNDED",
}


class Order:
    def __init__(self, quantity, customer_type, promo_code=None):
        self.total = calculate_total(quantity, customer_type, promo_code)
        self.state = "CREATED"

    def _fire(self, event):
        key = (self.state, event)
        if key not in _TRANSITIONS:
            raise InvalidTransitionError(f"'{event}' not allowed in state {self.state}")
        self.state = _TRANSITIONS[key]

    def pay(self):
        self._fire("pay")

    def cancel(self):
        self._fire("cancel")

    def collect(self):
        self._fire("collect")

    def complete_refund(self):
        self._fire("complete_refund")
