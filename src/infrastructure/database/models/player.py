from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, func

from src.infrastructure.database.models.base import Base


class PlayerModel(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    full_name = Column(String(300))
    team_id = Column(Integer, ForeignKey("teams.id"))
    position = Column(String(30))
    position_detail = Column(String(50))
    date_of_birth = Column(Date)
    age = Column(Integer)
    nationality = Column(String(100))
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    foot = Column(String(10))
    market_value_eur = Column(Float)
    current_club = Column(String(200))
    shirt_number = Column(Integer)
    international_caps = Column(Integer)
    international_goals = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
