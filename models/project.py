# models/project.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    """Доменная модель проекта"""
    id: Optional[int]
    opo_id: int
    name: str
    description: Optional[str]
    automation_description: Optional[str]
    project_code: Optional[str]
    dpb_code: Optional[str]
    rpz_code: Optional[str]
    ifl_code: Optional[str]
    gochs_code: Optional[str]
    mpb_code: Optional[str]
