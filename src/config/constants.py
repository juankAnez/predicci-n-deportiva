from enum import Enum


class CompetitionType(str, Enum):
    WORLD_CUP = "world_cup"
    CONTINENTAL_CUP = "continental_cup"
    LEAGUE = "league"
    CUP = "cup"
    FRIENDLY = "friendly"
    QUALIFIER = "qualifier"


class MatchStage(str, Enum):
    GROUP = "group"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    THIRD_PLACE = "third_place"
    FINAL = "final"
    PLAYOFF = "playoff"


class Confederation(str, Enum):
    UEFA = "UEFA"
    CONMEBOL = "CONMEBOL"
    CONCACAF = "CONCACAF"
    CAF = "CAF"
    AFC = "AFC"
    OFC = "OFC"


class PlayerPosition(str, Enum):
    GOALKEEPER = "GK"
    DEFENDER = "DEF"
    MIDFIELDER = "MID"
    FORWARD = "FWD"


class RankingType(str, Enum):
    FIFA = "fifa"
    ELO = "elo"


class PredictionResult(str, Enum):
    HOME_WIN = "H"
    DRAW = "D"
    AWAY_WIN = "A"


class InjurySeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class ScrapingStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class ModelStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


# K-Factors for Elo ratings
ELO_K_FACTOR_DEFAULT = 32
ELO_K_FACTOR_KNOCKOUT = 48
ELO_K_FACTOR_FRIENDLY = 20
ELO_HOME_ADVANTAGE = 70
ELO_ALTITUDE_BONUS = 25
ELO_FATIGUE_PENALTY = 5

# Default feature windows
DEFAULT_WINDOWS = [5, 10, 20]

# Competition importance weights
COMPETITION_IMPORTANCE = {
    CompetitionType.WORLD_CUP: 100,
    CompetitionType.CONTINENTAL_CUP: 85,
    CompetitionType.CUP: 70,
    CompetitionType.LEAGUE: 60,
    CompetitionType.QUALIFIER: 50,
    CompetitionType.FRIENDLY: 20,
}

# Stage multipliers for importance
STAGE_MULTIPLIER = {
    MatchStage.GROUP: 1.0,
    MatchStage.ROUND_OF_16: 1.3,
    MatchStage.QUARTER_FINAL: 1.5,
    MatchStage.SEMI_FINAL: 1.8,
    MatchStage.THIRD_PLACE: 1.0,
    MatchStage.FINAL: 2.0,
    MatchStage.PLAYOFF: 1.2,
}
