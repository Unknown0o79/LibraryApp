from dataclasses import dataclass
from typing import Optional


@dataclass
class Loan:
    id: Optional[int] = None
    book_id: int = 0
    reader_id: int = 0
    issue_date: str = ""
    due_date: str = ""
    return_date: Optional[str] = None
    status: str = "Выдана"