from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.tax_engine_service.schemas import (
    TaxCalculationRequest,
    TaxCalculationResponse,
)
from app.tax_engine_service.service import calculate_gst

router = APIRouter(prefix="/tax", tags=["Tax Engine"])


@router.post(
    "/calculate",
    response_model=TaxCalculationResponse,
)
def calculate_tax(payload: TaxCalculationRequest, db: Session = Depends(get_db)):
    try:
        return calculate_gst(db, payload.invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
