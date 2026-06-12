from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from src.config.constants import Confederation


@dataclass
class Team:
    id: Optional[int] = None
    name: str = ""
    full_name: Optional[str] = None
    code: Optional[str] = None
    country: Optional[str] = None
    confederation: Optional[Confederation] = None
    founded_year: Optional[int] = None
    logo_url: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Team):
            return False
        return self.name == other.name
