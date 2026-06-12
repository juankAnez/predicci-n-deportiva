from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.config.constants import PlayerPosition


@dataclass
class Player:
    id: Optional[int] = None
    name: str = ""
    full_name: Optional[str] = None
    team_id: Optional[int] = None
    position: Optional[PlayerPosition] = None
    position_detail: Optional[str] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    foot: Optional[str] = None
    market_value_eur: Optional[float] = None
    current_club: Optional[str] = None
    shirt_number: Optional[int] = None
    international_caps: Optional[int] = None
    international_goals: Optional[int] = None
