from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


# ---------- COMPANY ----------

class CompanyCreate(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None  # State code
    pincode: Optional[str] = None
    mobile_number: Optional[str] = None  # phone in UI
    email_id: Optional[str] = None  # email in UI
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    mobile_number: Optional[str]
    email_id: Optional[str]
    bank_name: Optional[str]
    bank_branch: Optional[str]
    account_holder_name: Optional[str]
    account_number: Optional[str]
    ifsc_code: Optional[str]


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    mobile_number: Optional[str]
    email_id: Optional[str]
    bank_name: Optional[str]
    bank_branch: Optional[str]
    account_holder_name: Optional[str]
    account_number: Optional[str]
    ifsc_code: Optional[str]
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


# ---------- COMBINED COMPANY + GSTIN (For UI) ----------

class CompanyWithGSTINResponse(BaseModel):
    """Combined company and GSTIN details for UI forms."""
    # Company fields
    id: UUID
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None  # mapped from mobile_number
    email: Optional[str] = None  # mapped from email_id

    # GSTIN fields (from first GSTIN)
    gstin: Optional[str] = None
    pan: Optional[str] = None

    # Bank details
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None

    created_at: datetime
