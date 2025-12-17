from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from datetime import date


class InvoicePreviewItem(BaseModel):
    product_name: str
    hsn_sac: Optional[str]
    quantity: Decimal
    rate: Decimal
    taxable_value: Decimal


class InvoicePreviewTax(BaseModel):
    tax_type: str
    tax_rate: Decimal
    tax_amount: Decimal


class InvoicePreviewResponse(BaseModel):
    invoice_id: UUID
    invoice_number: str
    invoice_date: date

    seller_name: str
    seller_gstin: str

    customer_name: str
    customer_gstin: Optional[str]
    customer_address: str

    items: List[InvoicePreviewItem]
    taxes: List[InvoicePreviewTax]

    taxable_total: Decimal
    tax_total: Decimal
    round_off: Decimal
    grand_total: Decimal
