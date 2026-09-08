import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.config import settings

logger = logging.getLogger(__name__)


def update_rankings():
    """Update FIFA and Elo rankings daily"""
    logger.info("Iniciando actualización de rankings...")
    try:
        from src.infrastructure.scraping.middleware import ScrapingManager
        from src.infrastructure.database.repositories import RankingRepository, TeamRepository

        scraper = ScrapingManager()
        ranking_repo = RankingRepository()
        team_repo = TeamRepository()

        data = scraper.scrape_rankings("all")
        logger.info(f"Scraping completado: {len(data)} rankings obtenidos")

        for entry in data:
            team = team_repo.get_by_name(entry.get("team_name", ""))
            if not team:
                team = team_repo.create(team_repo.to_domain(team_repo.model_class(name=entry["team_name"])))
            from src.domain.value_objects import Ranking
            ranking = Ranking(
                team_id=team.id,
                ranking_type=entry["ranking_type"],
                rank=entry["rank"],
                previous_rank=entry.get("previous_rank"),
                points=entry.get("points", 0),
                rank_date=datetime.now().date(),
            )
            ranking_repo.create(ranking)

        logger.info("Rankings actualizados exitosamente")
    except Exception as e:
        logger.error(f"Error actualizando rankings: {e}")


def update_matches():
    """Update recent match results"""
    logger.info("Iniciando actualización de partidos...")
    # TODO: Implement match scraping from football-data.org or similar
    logger.info("Actualización de partidos completada")


def clean_old_logs():
    """Clean scraping logs older than 30 days"""
    from src.infrastructure.database.connection import db_session
    from src.infrastructure.database.models import ScrapingLogModel

    db = db_session()
    cutoff = datetime.now() - timedelta(days=30)
    deleted = db.query(ScrapingLogModel).filter(ScrapingLogModel.created_at < cutoff).delete()
    db.commit()
    db.close()
    logger.info(f"Logs antiguos eliminados: {deleted}")


def scheduled_training():
    """Retrain models periodically"""
    logger.info("Iniciando reentrenamiento programado...")
    try:
        from src.ml.training.trainer import ModelTrainer
        from src.infrastructure.database.repositories import MatchRepository
        import pandas as pd

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
        logger.info("Reentrenamiento completado exitosamente")
    except Exception as e:
        logger.error(f"Error en reentrenamiento: {e}")


def start_scheduler():
    scheduler = BlockingScheduler()

    # Rankings: every day at 6:00 AM
    scheduler.add_job(
        update_rankings,
        CronTrigger(hour=6, minute=0),
        id="update_rankings",
        name="Actualizar rankings FIFA y Elo",
        misfire_grace_time=3600,
    )

    # Matches: every 4 hours
    scheduler.add_job(
        update_matches,
        IntervalTrigger(hours=4),
        id="update_matches",
        name="Actualizar resultados de partidos",
        misfire_grace_time=1800,
    )

    # Logs cleanup: every Sunday at 3:00 AM
    scheduler.add_job(
        clean_old_logs,
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="clean_logs",
        name="Limpiar logs antiguos",
    )

    # Model retraining: every first day of the month at 2:00 AM
    scheduler.add_job(
        scheduled_training,
        CronTrigger(day=1, hour=2, minute=0),
        id="retrain_models",
        name="Reentrenar modelos mensualmente",
        misfire_grace_time=86400,
    )

    logger.info("Scheduler iniciado. Tareas programadas activas.")
    print("=" * 50)
    print("  Scheduler de Predicción Deportiva")
    print("  Tareas activas:")
    print("    - Rankings: cada día 06:00")
    print("    - Partidos: cada 4 horas")
    print("    - Limpieza logs: domingos 03:00")
    print("    - Reentrenamiento: día 1 cada mes 02:00")
    print("=" * 50)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler detenido por el usuario")
        scheduler.shutdown()


if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    start_scheduler()
