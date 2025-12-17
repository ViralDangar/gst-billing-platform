from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.accounting_service.service import create_sales_voucher

router = APIRouter(prefix="/accounting", tags=["Accounting"])


@router.get("/health")
def accounting_health():
    return {"service": "accounting", "status": "ok"}
    
@router.post("/vouchers/from-invoice/{invoice_id}")
def create_voucher_from_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        voucher = create_sales_voucher(db, invoice_id)
        return {
            "voucher_id": voucher.id,
            "reference_invoice_id": voucher.reference_invoice_id,
            "voucher_type": voucher.voucher_type,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))