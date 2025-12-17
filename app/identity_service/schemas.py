from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


# ---------- COMPANY ----------

class CompanyCreate(BaseModel):
    name: str
    address: str
    logo_url: Optional[str] = None
    default_bank_details: Optional[dict] = None


class CompanyUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    default_bank_details: Optional[dict]


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    logo_url: Optional[str]
    default_bank_details: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- GSTIN ----------

class GSTINCreate(BaseModel):
    gst_number: str = Field(..., example="27ABCDE1234F1Z5")
    state_code: str = Field(..., example="27")


class GSTINResponse(BaseModel):
    id: UUID
    gst_number: str
    state_code: str
    created_at: datetime

    class Config:
        from_attributes = True
