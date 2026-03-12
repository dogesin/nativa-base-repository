import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class Currency(str, enum.Enum):
    USD = "usd"
    MXN = "mxn"
    EUR = "eur"
