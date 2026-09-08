from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Date, func

from src.infrastructure.database.models.base import Base


class ModelVersionModel(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    model_type = Column(String(50))
    parameters = Column(String)  # JSON
    metrics = Column(String)  # JSON
    training_date = Column(DateTime, default=func.now())
    training_data_range_start = Column(Date)
    training_data_range_end = Column(Date)
    data_hash = Column(String(64))
    model_file_path = Column(String(300))
    feature_list = Column(String)  # JSON
    feature_count = Column(Integer)
    status = Column(String(20), default="active")
    is_ensemble = Column(Boolean, default=False)
    parent_models = Column(String)  # JSON
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    log_loss = Column(Float)
    brier_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
