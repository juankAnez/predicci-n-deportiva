from dataclasses import dataclass
from typing import Optional


@dataclass
class TeamStats:
    match_id: int
    team_id: int
    is_home: bool
    goals: Optional[int] = None
    xg: Optional[float] = None
    xga: Optional[float] = None
    shots_total: Optional[int] = None
    shots_on_target: Optional[int] = None
    shots_off_target: Optional[int] = None
    shots_blocked: Optional[int] = None
    corners: Optional[int] = None
    fouls: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    possession: Optional[float] = None
    passes_total: Optional[int] = None
    passes_completed: Optional[int] = None
    passing_accuracy: Optional[float] = None
    progressive_passes: Optional[int] = None
    progressive_carries: Optional[int] = None
    offsides: Optional[int] = None
    tackles: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    recoveries: Optional[int] = None
    saves: Optional[int] = None
    ppda: Optional[float] = None
    high_press_success: Optional[int] = None
    territorial_possession: Optional[float] = None
    shot_conversion_rate: Optional[float] = None
