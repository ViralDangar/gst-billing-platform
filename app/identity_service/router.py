from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.identity_service import service
from app.identity_service.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    GSTINCreate,
    GSTINResponse,
)

router = APIRouter(prefix="/identity", tags=["Company & GSTIN"])


# ---------- COMPANY ----------

@router.post(
    "/company",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing = service.get_company(db)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company already exists",
        )
    return service.create_company(db, payload)


@router.get("/company", response_model=CompanyResponse)
def get_company(db: Session = Depends(get_db)):
    company = service.get_company(db)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/company", response_model=CompanyResponse)
def update_company(
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
):
    company = service.get_company(db)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return service.update_company(db, company, payload)


# ---------- GSTIN ----------

@router.post(
    "/company/{company_id}/gstins",
    response_model=GSTINResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_gstin(
    company_id: UUID,
    payload: GSTINCreate,
    db: Session = Depends(get_db),
):
    return service.create_gstin(db, company_id, payload)


@router.get(
    "/company/{company_id}/gstins",
    response_model=List[GSTINResponse],
)
def list_gstins(company_id: UUID, db: Session = Depends(get_db)):
    return service.list_gstins(db, company_id)


@router.get("/health")
def identity_health():
    return {"service": "identity", "status": "ok"}
