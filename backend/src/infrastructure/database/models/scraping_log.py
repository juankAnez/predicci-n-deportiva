from sqlalchemy import Column, Integer, String, DateTime, Text, func, Index

from src.infrastructure.database.models.base import Base


class ScrapingLogModel(Base):
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    url = Column(String(500))
    data_type = Column(String(50))
    status = Column(String(20), nullable=False)
    items_count = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_scraping_logs_status", "status"),
        Index("idx_scraping_logs_source", "source"),
    )
