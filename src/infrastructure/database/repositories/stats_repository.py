from typing import List, Optional

from src.domain.value_objects import TeamStats
from src.infrastructure.database.models import TeamStatsModel
from src.infrastructure.database.repositories.base import BaseRepository


class TeamStatsRepository(BaseRepository[TeamStats]):
    model_class = TeamStatsModel

    def to_domain(self, model: TeamStatsModel) -> TeamStats:
        return TeamStats(
            match_id=model.match_id,
            team_id=model.team_id,
            is_home=model.is_home,
            goals=model.goals,
            xg=model.xg,
            xga=model.xga,
            shots_total=model.shots_total,
            shots_on_target=model.shots_on_target,
            shots_off_target=model.shots_off_target,
            shots_blocked=model.shots_blocked,
            corners=model.corners,
            fouls=model.fouls,
            yellow_cards=model.yellow_cards,
            red_cards=model.red_cards,
            possession=model.possession,
            passes_total=model.passes_total,
            passes_completed=model.passes_completed,
            passing_accuracy=model.passing_accuracy,
            progressive_passes=model.progressive_passes,
            progressive_carries=model.progressive_carries,
            offsides=model.offsides,
            tackles=model.tackles,
            interceptions=model.interceptions,
            clearances=model.clearances,
            recoveries=model.recoveries,
            saves=model.saves,
            ppda=model.ppda,
            high_press_success=model.high_press_success,
            territorial_possession=model.territorial_possession,
            shot_conversion_rate=model.shot_conversion_rate,
        )

    def to_model(self, domain: TeamStats) -> TeamStatsModel:
        return TeamStatsModel(
            match_id=domain.match_id,
            team_id=domain.team_id,
            is_home=domain.is_home,
            goals=domain.goals,
            xg=domain.xg,
            xga=domain.xga,
            shots_total=domain.shots_total,
            shots_on_target=domain.shots_on_target,
            shots_off_target=domain.shots_off_target,
            shots_blocked=domain.shots_blocked,
            corners=domain.corners,
            fouls=domain.fouls,
            yellow_cards=domain.yellow_cards,
            red_cards=domain.red_cards,
            possession=domain.possession,
            passes_total=domain.passes_total,
            passes_completed=domain.passes_completed,
            passing_accuracy=domain.passing_accuracy,
            progressive_passes=domain.progressive_passes,
            progressive_carries=domain.progressive_carries,
            offsides=domain.offsides,
            tackles=domain.tackles,
            interceptions=domain.interceptions,
            clearances=domain.clearances,
            recoveries=domain.recoveries,
            saves=domain.saves,
            ppda=domain.ppda,
            high_press_success=domain.high_press_success,
            territorial_possession=domain.territorial_possession,
            shot_conversion_rate=domain.shot_conversion_rate,
        )

    def get_by_match(self, match_id: int) -> List[TeamStats]:
        models = self.db.query(TeamStatsModel).filter(TeamStatsModel.match_id == match_id).all()
        return [self.to_domain(m) for m in models]

    def get_team_stats_since(self, team_id: int, limit: int = 10) -> List[TeamStats]:
        models = (
            self.db.query(TeamStatsModel)
            .filter(TeamStatsModel.team_id == team_id)
            .order_by(TeamStatsModel.id.desc())
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]
