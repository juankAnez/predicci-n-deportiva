from typing import List, Optional

from src.domain.entities import Competition
from src.infrastructure.database.models import CompetitionModel
from src.infrastructure.database.repositories.base import BaseRepository


class CompetitionRepository(BaseRepository[Competition]):
    model_class = CompetitionModel

    def to_domain(self, model: CompetitionModel) -> Competition:
        return Competition(
            id=model.id,
            name=model.name,
            short_name=model.short_name,
            type=model.type,
            confederation=model.confederation,
            season=model.season,
            start_date=model.start_date,
            end_date=model.end_date,
        )

    def to_model(self, domain: Competition) -> CompetitionModel:
        return CompetitionModel(
            id=domain.id,
            name=domain.name,
            short_name=domain.short_name,
            type=domain.type,
            confederation=domain.confederation,
            season=domain.season,
            start_date=domain.start_date,
            end_date=domain.end_date,
        )

    def get_by_name(self, name: str) -> Optional[Competition]:
        model = self.db.query(CompetitionModel).filter(CompetitionModel.name == name).first()
        return self.to_domain(model) if model else None

    def get_by_type(self, type: str) -> List[Competition]:
        models = self.db.query(CompetitionModel).filter(CompetitionModel.type == type).all()
        return [self.to_domain(m) for m in models]

    def get_by_season(self, season: str) -> List[Competition]:
        models = self.db.query(CompetitionModel).filter(CompetitionModel.season == season).all()
        return [self.to_domain(m) for m in models]
