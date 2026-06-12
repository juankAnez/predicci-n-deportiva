from celery import Celery

from src.config import settings

celery_app = Celery(
    "prediccion_deportiva",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)


@celery_app.task(bind=True, max_retries=3)
def scrape_rankings_task(self):
    from src.infrastructure.scraping.middleware import ScrapingManager
    manager = ScrapingManager()
    return manager.scrape_rankings("all")


@celery_app.task(bind=True, max_retries=3)
def train_models_task(self):
    from src.ml.training.trainer import ModelTrainer
    import pandas as pd
    from src.infrastructure.database.repositories import MatchRepository

    match_repo = MatchRepository()
    matches = match_repo.get_all()
    match_data = [
        {
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
            "home_goals": m.home_score or 0,
            "away_goals": m.away_score or 0,
            "match_date": m.match_date,
            "result": (
                "H" if (m.home_score or 0) > (m.away_score or 0)
                else "A" if (m.away_score or 0) > (m.home_score or 0)
                else "D"
            ) if m.home_score is not None else None,
        }
        for m in matches if m.home_score is not None
    ]

    df = pd.DataFrame(match_data)
    trainer = ModelTrainer()
    X, y_goals, y_result = trainer.prepare_data(df)
    models = trainer.train_models(X, y_result, y_goals)
    trainer.save_models(models)
    return {"status": "success", "models": list(models.keys())}
