from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from src.config.constants import MatchStage


@dataclass
class Match:
    id: Optional[int] = None
    competition_id: Optional[int] = None
    season: Optional[str] = None
    stage: Optional[MatchStage] = None
    round: Optional[int] = None
    group_name: Optional[str] = None
    match_date: Optional[date] = None
    match_time: Optional[time] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_goals_ht: Optional[int] = None
    away_goals_ht: Optional[int] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    stadium: Optional[str] = None
    attendance: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[int] = None
    altitude: Optional[int] = None
    weather_condition: Optional[str] = None
    referee: Optional[str] = None

    @property
    def home_team_name(self) -> Optional[str]:
        return None  # populated by service

    @property
    def away_team_name(self) -> Optional[str]:
        return None

    @property
    def is_finished(self) -> bool:
        return self.home_score is not None and self.away_score is not None
