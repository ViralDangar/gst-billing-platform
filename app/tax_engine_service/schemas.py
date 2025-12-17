from pydantic import BaseModel
from uuid import UUID


class TaxCalculationRequest(BaseModel):
    invoice_id: UUID


class TaxCalculationResponse(BaseModel):
    invoice_id: UUID
    taxable_total: float
    tax_total: float
    grand_total: float
