from dataclasses import dataclass
from typing import Optional


@dataclass
class Reader:
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    email: str = ""
    registration_date: str = ""