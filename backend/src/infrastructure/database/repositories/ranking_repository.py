from datetime import date
from typing import List, Optional

from sqlalchemy import and_

from src.domain.value_objects import Ranking
from src.infrastructure.database.models import RankingModel
from src.infrastructure.database.repositories.base import BaseRepository


class RankingRepository(BaseRepository[Ranking]):
    model_class = RankingModel

    def to_domain(self, model: RankingModel) -> Ranking:
        return Ranking(
            team_id=model.team_id,
            ranking_type=model.ranking_type,
            rank=model.rank,
            previous_rank=model.previous_rank,
            points=model.points,
            change_points=model.change_points,
            rank_date=model.rank_date,
        )

    def to_model(self, domain: Ranking) -> RankingModel:
        return RankingModel(
            team_id=domain.team_id,
            ranking_type=domain.ranking_type,
            rank=domain.rank,
            previous_rank=domain.previous_rank,
            points=domain.points,
            change_points=domain.change_points,
            rank_date=domain.rank_date,
        )

    def get_latest_by_team(self, team_id: int, ranking_type: str = "fifa") -> Optional[Ranking]:
        model = (
            self.db.query(RankingModel)
            .filter(
                and_(
                    RankingModel.team_id == team_id,
                    RankingModel.ranking_type == ranking_type,
                )
            )
            .order_by(RankingModel.rank_date.desc())
            .first()
        )
        return self.to_domain(model) if model else None

    def get_latest_rankings(self, ranking_type: str = "fifa", limit: int = 100) -> List[Ranking]:
        latest_date = (
            self.db.query(RankingModel.rank_date)
            .filter(RankingModel.ranking_type == ranking_type)
            .order_by(RankingModel.rank_date.desc())
            .first()
        )
        if not latest_date:
            return []
        models = (
            self.db.query(RankingModel)
            .filter(
                and_(
                    RankingModel.ranking_type == ranking_type,
                    RankingModel.rank_date == latest_date[0],
                )
            )
            .order_by(RankingModel.rank)
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_team_ranking_history(self, team_id: int, ranking_type: str = "fifa", limit: int = 20) -> List[Ranking]:
        models = (
            self.db.query(RankingModel)
            .filter(
                and_(
                    RankingModel.team_id == team_id,
                    RankingModel.ranking_type == ranking_type,
                )
            )
            .order_by(RankingModel.rank_date.desc())
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_ranking_at_date(self, team_id: int, date: date, ranking_type: str = "fifa") -> Optional[Ranking]:
        model = (
            self.db.query(RankingModel)
            .filter(
                and_(
                    RankingModel.team_id == team_id,
                    RankingModel.ranking_type == ranking_type,
                    RankingModel.rank_date <= date,
                )
            )
            .order_by(RankingModel.rank_date.desc())
            .first()
        )
        return self.to_domain(model) if model else None
