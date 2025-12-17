from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from datetime import date
from decimal import Decimal


class InvoiceCreate(BaseModel):
    invoice_date: date
    gstin_id: UUID
    customer_id: UUID


class InvoiceItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal
    rate: Decimal


class InvoiceItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: Decimal
    rate: Decimal
    taxable_value: Decimal

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: UUID
    invoice_date: date
    gstin_id: UUID
    customer_id: UUID
    status: str
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True


class InvoiceFinalizeResponse(BaseModel):
    invoice_id: UUID
    invoice_number: str
    status: str