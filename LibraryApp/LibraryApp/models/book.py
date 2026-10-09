from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    isbn: str = ""
    genre: str = ""
    year: Optional[int] = None
    publisher: str = ""
    quantity: int = 1
    available: int = 1