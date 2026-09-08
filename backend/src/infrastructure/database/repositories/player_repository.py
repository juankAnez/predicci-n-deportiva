from typing import List, Optional

from src.domain.entities import Player
from src.infrastructure.database.models import PlayerModel
from src.infrastructure.database.repositories.base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    model_class = PlayerModel

    def to_domain(self, model: PlayerModel) -> Player:
        return Player(
            id=model.id,
            name=model.name,
            full_name=model.full_name,
            team_id=model.team_id,
            position=model.position,
            position_detail=model.position_detail,
            date_of_birth=model.date_of_birth,
            age=model.age,
            nationality=model.nationality,
            height_cm=model.height_cm,
            weight_kg=model.weight_kg,
            foot=model.foot,
            market_value_eur=model.market_value_eur,
            current_club=model.current_club,
            shirt_number=model.shirt_number,
            international_caps=model.international_caps,
            international_goals=model.international_goals,
        )

    def to_model(self, domain: Player) -> PlayerModel:
        return PlayerModel(
            id=domain.id,
            name=domain.name,
            full_name=domain.full_name,
            team_id=domain.team_id,
            position=domain.position,
            position_detail=domain.position_detail,
            date_of_birth=domain.date_of_birth,
            age=domain.age,
            nationality=domain.nationality,
            height_cm=domain.height_cm,
            weight_kg=domain.weight_kg,
            foot=domain.foot,
            market_value_eur=domain.market_value_eur,
            current_club=domain.current_club,
            shirt_number=domain.shirt_number,
            international_caps=domain.international_caps,
            international_goals=domain.international_goals,
        )

    def get_by_team(self, team_id: int) -> List[Player]:
        models = self.db.query(PlayerModel).filter(PlayerModel.team_id == team_id).all()
        return [self.to_domain(m) for m in models]

    def get_by_name(self, name: str) -> List[Player]:
        models = self.db.query(PlayerModel).filter(PlayerModel.name.ilike(f"%{name}%")).all()
        return [self.to_domain(m) for m in models]

    def get_by_position(self, position: str) -> List[Player]:
        models = self.db.query(PlayerModel).filter(PlayerModel.position == position).all()
        return [self.to_domain(m) for m in models]
