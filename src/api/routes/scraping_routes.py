from flask import Blueprint, jsonify, request

from src.infrastructure.database.models import ScrapingLogModel
from src.infrastructure.database.connection import db_session
from src.infrastructure.scraping.middleware import ScrapingManager

scraping_bp = Blueprint("scraping", __name__)
scraping_manager = ScrapingManager()


@scraping_bp.route("/scrape/rankings", methods=["POST"])
def scrape_rankings():
    try:
        data = scraping_manager.scrape_rankings(ranking_type="all")
        return jsonify({
            "status": "success",
            "data": {
                "items_scraped": len(data),
                "message": f"Scraping completado: {len(data)} rankings obtenidos",
            },
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@scraping_bp.route("/scrape/weather", methods=["POST"])
def scrape_weather():
    body = request.get_json()
    if not body or "city" not in body or "date" not in body:
        return jsonify({"status": "error", "error": "Se requieren city y date"}), 400

    data = scraping_manager.scrape_weather(body["city"], body["date"])
    return jsonify({"status": "success", "data": data or {}})


@scraping_bp.route("/scrape/status", methods=["GET"])
def scrape_status():
    db = db_session()
    recent = db.query(ScrapingLogModel).order_by(ScrapingLogModel.created_at.desc()).limit(20).all()
    db.close()

    return jsonify({
        "status": "success",
        "data": [
            {
                "source": log.source,
                "data_type": log.data_type,
                "status": log.status,
                "items_count": log.items_count,
                "error_message": log.error_message,
                "duration_ms": log.duration_ms,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in recent
        ],
    })


@scraping_bp.route("/db/init", methods=["POST"])
def init_database():
    try:
        from src.infrastructure.database.connection import init_db
        init_db()
        return jsonify({"status": "success", "message": "Base de datos inicializada correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@scraping_bp.route("/scrape/logs", methods=["GET"])
def scrape_logs():
    db = db_session()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    total = db.query(ScrapingLogModel).count()
    logs = (
        db.query(ScrapingLogModel)
        .order_by(ScrapingLogModel.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    db.close()

    return jsonify({
        "status": "success",
        "data": [
            {
                "id": log.id,
                "source": log.source,
                "data_type": log.data_type,
                "status": log.status,
                "items_count": log.items_count,
                "error_message": log.error_message,
                "duration_ms": log.duration_ms,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
        },
    })
