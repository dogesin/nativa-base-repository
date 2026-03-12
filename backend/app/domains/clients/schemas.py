from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    company: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None
    company: str | None
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime
