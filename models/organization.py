# models/organization.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Organization:
    """Доменная модель организации"""
    id: Optional[int]
    name: str
    full_name: str
    org_form: str
    head_position: Optional[str]
    head_name: Optional[str]
    legal_address: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    license_number: Optional[str]
    license_date: Optional[date]
    ind_safety_system: Optional[str]
    prod_control: Optional[str]
    accident_investigation: Optional[str]
    rescue_contract: Optional[str]
    rescue_certificate: Optional[str]
    fire_contract: Optional[str]
    emergency_certificate: Optional[str]
    material_reserves: Optional[str]
    financial_reserves: Optional[str]



