import uuid
from sqlalchemy.orm import Session

from app.identity_service.models import Company, GSTIN
from app.identity_service.schemas import (
    CompanyCreate,
    CompanyUpdate,
    GSTINCreate,
)


# ---------- COMPANY ----------

def create_company(db: Session, payload: CompanyCreate) -> Company:
    company = Company(
        id=uuid.uuid4(),
        name=payload.name,
        address=payload.address,
        logo_url=payload.logo_url,
        default_bank_details=payload.default_bank_details,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_company(db: Session):
    return db.query(Company).first()


def update_company(db: Session, company: Company, payload: CompanyUpdate):
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


# ---------- GSTIN ----------

def create_gstin(db: Session, company_id, payload: GSTINCreate) -> GSTIN:
    gstin = GSTIN(
        id=uuid.uuid4(),
        company_id=company_id,
        gst_number=payload.gst_number,
        state_code=payload.state_code,
    )
    db.add(gstin)
    db.commit()
    db.refresh(gstin)
    return gstin


def list_gstins(db: Session, company_id):
    return (
        db.query(GSTIN)
        .filter(GSTIN.company_id == company_id)
        .all()
    )
