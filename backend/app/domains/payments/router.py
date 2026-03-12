from fastapi import APIRouter, Depends, Header, Request, status

from app.domains.payments.dependencies import get_payment_service
from app.domains.payments.schemas import PaymentCreate, PaymentRead
from app.domains.payments.service import PaymentService
from app.infrastructure.stripe.webhooks import verify_webhook

router = APIRouter(tags=["Payments"])


@router.get(
    "/clients/{client_id}/payments",
    response_model=list[PaymentRead],
    tags=["Payments"],
)
def list_payments(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    service: PaymentService = Depends(get_payment_service),
):
    return service.list_payments(client_id, skip=skip, limit=limit)


@router.post(
    "/clients/{client_id}/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Payments"],
)
def create_payment(
    client_id: int,
    data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    return service.create_payment(client_id, data)


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentRead,
    tags=["Payments"],
)
def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
):
    return service.get_payment(payment_id)


@router.post("/stripe/webhook", tags=["Stripe Webhooks"])
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    service: PaymentService = Depends(get_payment_service),
):
    payload = await request.body()
    event = verify_webhook(payload, stripe_signature)
    service.handle_webhook_event(event)
    return {"status": "ok"}
