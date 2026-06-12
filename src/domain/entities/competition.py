from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.config.constants import CompetitionType


@dataclass
class Competition:
    id: Optional[int] = None
    name: str = ""
    short_name: Optional[str] = None
    type: Optional[CompetitionType] = None
    confederation: Optional[str] = None
    season: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
