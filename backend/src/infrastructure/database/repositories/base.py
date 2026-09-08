from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import db_session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, db: Optional[Session] = None):
        self.db = db or db_session()

    @abstractmethod
    def to_domain(self, model: Any) -> T:
        pass

    @abstractmethod
    def to_model(self, domain: T) -> Any:
        pass

    def get_all(self) -> List[T]:
        models = self.db.query(self.model_class).all()
        return [self.to_domain(m) for m in models]

    def get_by_id(self, id: int) -> Optional[T]:
        model = self.db.query(self.model_class).filter(self.model_class.id == id).first()
        return self.to_domain(model) if model else None

    def create(self, domain: T) -> T:
        model = self.to_model(domain)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self.to_domain(model)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        model = self.db.query(self.model_class).filter(self.model_class.id == id).first()
        if not model:
            return None
        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.db.commit()
        self.db.refresh(model)
        return self.to_domain(model)

    def delete(self, id: int) -> bool:
        model = self.db.query(self.model_class).filter(self.model_class.id == id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(self.model_class).count()

    def execute_raw(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        result = self.db.execute(text(query), params or {})
        return [dict(row._mapping) for row in result]
