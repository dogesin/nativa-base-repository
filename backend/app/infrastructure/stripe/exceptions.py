from fastapi import HTTPException, status


class StripeError(HTTPException):
    def __init__(self, detail: str = "Payment processing error"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class CardDeclinedError(StripeError):
    def __init__(self):
        super().__init__(detail="Card was declined")


class InvalidWebhookSignatureError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook signature",
        )
