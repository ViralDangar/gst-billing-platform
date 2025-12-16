from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., example="Steel Rod")
    hsn_sac: Optional[str] = Field(None, example="7214")
    gst_rate: Decimal = Field(..., example=18.0)
    unit: Optional[str] = Field(None, example="KG")
    base_price: Optional[Decimal] = Field(None, example=100.00)


class ProductUpdate(BaseModel):
    name: Optional[str]
    hsn_sac: Optional[str]
    gst_rate: Optional[Decimal]
    unit: Optional[str]
    base_price: Optional[Decimal]
    is_active: Optional[bool]


class ProductResponse(BaseModel):
    id: UUID
    name: str
    hsn_sac: Optional[str]
    gst_rate: Decimal
    unit: Optional[str]
    base_price: Optional[Decimal]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str = Field(..., example="ABC Traders")
    gstin: Optional[str] = Field(None, example="27ABCDE1234F1Z5")
    state: str = Field(..., example="Maharashtra")
    address: str
    is_b2b: bool = True


class CustomerUpdate(BaseModel):
    name: Optional[str]
    gstin: Optional[str]
    state: Optional[str]
    address: Optional[str]
    is_b2b: Optional[bool]
    is_active: Optional[bool]


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    gstin: Optional[str]
    state: str
    address: str
    is_b2b: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True