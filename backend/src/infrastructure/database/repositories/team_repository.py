from typing import List, Optional

from src.domain.entities import Team
from src.infrastructure.database.models import TeamModel
from src.infrastructure.database.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    model_class = TeamModel

    def to_domain(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            full_name=model.full_name,
            code=model.code,
            country=model.country,
            confederation=model.confederation,
            founded_year=model.founded_year,
            logo_url=model.logo_url,
        )

    def to_model(self, domain: Team) -> TeamModel:
        return TeamModel(
            id=domain.id,
            name=domain.name,
            full_name=domain.full_name,
            code=domain.code,
            country=domain.country,
            confederation=domain.confederation,
            founded_year=domain.founded_year,
            logo_url=domain.logo_url,
        )

    def get_by_name(self, name: str) -> Optional[Team]:
        model = self.db.query(TeamModel).filter(TeamModel.name == name).first()
        return self.to_domain(model) if model else None

    def get_by_code(self, code: str) -> Optional[Team]:
        model = self.db.query(TeamModel).filter(TeamModel.code == code).first()
        return self.to_domain(model) if model else None

    def get_by_confederation(self, confederation: str) -> List[Team]:
        models = self.db.query(TeamModel).filter(TeamModel.confederation == confederation).all()
        return [self.to_domain(m) for m in models]

    def search(self, query: str) -> List[Team]:
        models = self.db.query(TeamModel).filter(TeamModel.name.ilike(f"%{query}%")).all()
        return [self.to_domain(m) for m in models]

    def upsert(self, team: Team) -> Team:
        existing = self.get_by_name(team.name)
        if existing:
            return self.update(existing.id, {
                "full_name": team.full_name,
                "code": team.code,
                "country": team.country,
                "confederation": team.confederation,
                "founded_year": team.founded_year,
                "logo_url": team.logo_url,
            })
        return self.create(team)
