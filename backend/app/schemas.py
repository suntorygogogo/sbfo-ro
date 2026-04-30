from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ChildImpactBase(BaseModel):
    impact_year: str
    impact_period: str
    nsv_aud: Optional[str] = None
    nsv_nzd: Optional[str] = None
    volume_litres: Optional[str] = None


class ChildImpactOut(ChildImpactBase):
    id: int
    model_config = {"from_attributes": True}


class EntryBase(BaseModel):
    creation_date: Optional[str] = None
    creation_date_period: Optional[str] = None
    creation_date_year: Optional[str] = None
    add_to_forecast_by_period: Optional[str] = None
    add_to_forecast_by_year: Optional[str] = None
    division: str
    ibp_step: Optional[str] = None
    country: str
    channel: str
    sub_channel: str
    account: str
    brand: str
    brand_family: Optional[str] = None
    r_and_o: str
    probability: str
    categorisation: str
    impact_period: Optional[str] = None
    impact_year: Optional[str] = None
    nsv_aud: Optional[str] = None
    nsv_nzd: Optional[str] = None
    volume_litres: Optional[str] = None
    impact_type: Optional[str] = "NSV"
    owner: str
    modified_user: Optional[str] = None
    status: Optional[str] = "Open"
    description: Optional[str] = None


class EntryCreate(EntryBase):
    creator: Optional[str] = None
    child_impacts: Optional[List[ChildImpactBase]] = []


class EntryUpdate(EntryBase):
    child_impacts: Optional[List[ChildImpactBase]] = []


class StatusUpdateBody(BaseModel):
    status: str
    modified_user: Optional[str] = None


class EntryOut(EntryBase):
    id: int
    original_entry_id: Optional[int] = None
    version: int
    creator: Optional[str] = None
    last_modified: Optional[datetime] = None
    child_impacts: List[ChildImpactOut] = []
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    display_name: Optional[str] = None
    role: int  # 0=System Admin, 1=User, 2=Department Approver, 3=Finance Approver
    departments: Optional[List[str]] = None  # None = all; list = restricted departments (role 2 only)
    model_config = {"from_attributes": True}


class LookupOptionOut(BaseModel):
    value: str
    label: str
    model_config = {"from_attributes": True}


