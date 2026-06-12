from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session = scoped_session(SessionLocal)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from src.infrastructure.database.models.base import Base
    Base.metadata.create_all(bind=engine)
