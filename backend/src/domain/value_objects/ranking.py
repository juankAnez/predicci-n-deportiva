from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Ranking:
    team_id: int
    ranking_type: str
    rank: int
    points: float
    rank_date: date
    previous_rank: Optional[int] = None
    change_points: Optional[float] = None
