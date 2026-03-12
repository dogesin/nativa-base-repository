from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    role: str | None = None


class ContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    role: str | None = None


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str | None
    created_at: datetime
    updated_at: datetime
