import logging
import sys
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from src.config import settings


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    app.secret_key = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    CORS(app)

    # Configure logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.NullHandler(),
        ],
    )

    # Register error handlers
    from src.api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    # Register routes
    from src.api.routes.prediction_routes import prediction_bp
    from src.api.routes.match_routes import match_bp
    from src.api.routes.team_routes import team_bp
    from src.api.routes.player_routes import player_bp
    from src.api.routes.ranking_routes import ranking_bp
    from src.api.routes.stats_routes import stats_bp
    from src.api.routes.scraping_routes import scraping_bp
    from src.api.routes.model_routes import model_bp

    app.register_blueprint(prediction_bp, url_prefix="/api/v1/predictions")
    app.register_blueprint(match_bp, url_prefix="/api/v1/matches")
    app.register_blueprint(team_bp, url_prefix="/api/v1/teams")
    app.register_blueprint(player_bp, url_prefix="/api/v1/players")
    app.register_blueprint(ranking_bp, url_prefix="/api/v1/rankings")
    app.register_blueprint(stats_bp, url_prefix="/api/v1/stats")
    app.register_blueprint(scraping_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(model_bp, url_prefix="/api/v1/models")

    # Frontend routes (serve HTML pages)
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        from flask import render_template
        return render_template("dashboard.html")

    @app.route("/prediction/<int:match_id>")
    def prediction_page(match_id: int):
        from flask import render_template
        return render_template("prediction.html", match_id=match_id)

    @app.route("/compare")
    def compare():
        from flask import render_template
        return render_template("compare.html")

    @app.route("/admin")
    def admin():
        from flask import render_template
        return render_template("admin.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.DEBUG,
    )
