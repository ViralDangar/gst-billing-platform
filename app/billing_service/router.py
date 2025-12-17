from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.billing_service import service
from app.billing_service.schemas import (
    InvoiceCreate,
    InvoiceItemCreate,
    InvoiceResponse,
)

router = APIRouter(prefix="/billing/invoices", tags=["Invoices"])

@router.get("/health")
def billing_health():
    return {"service": "billing", "status": "ok"}

@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = service.create_invoice(db, payload)
    return {
        **invoice.__dict__,
        "items": [],
    }


@router.post("/{invoice_id}/items")
def add_invoice_item(
    invoice_id: UUID,
    payload: InvoiceItemCreate,
    db: Session = Depends(get_db),
):
    invoice = service.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.status != "DRAFT":
        raise HTTPException(
            status_code=400,
            detail="Cannot modify finalized invoice",
        )

    return service.add_invoice_item(db, invoice, payload)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    invoice = service.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    items = service.get_invoice_items(db, invoice_id)

    return {
        **invoice.__dict__,
        "items": items,
    }

from app.billing_service.finalize import finalize_invoice
from app.billing_service.schemas import InvoiceFinalizeResponse


@router.post(
    "/{invoice_id}/finalize",
    response_model=InvoiceFinalizeResponse,
)
def finalize_invoice_api(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        return finalize_invoice(db, invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
