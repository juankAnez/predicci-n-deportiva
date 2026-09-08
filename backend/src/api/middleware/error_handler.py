import traceback
from flask import Flask, jsonify


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv["error"] = self.message
        rv["status"] = "error"
        return rv


def register_error_handlers(app: Flask):
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Recurso no encontrado",
            "status": "error",
            "status_code": 404,
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Error interno del servidor",
            "status": "error",
            "status_code": 500,
            "detail": traceback.format_exc() if app.debug else None,
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Solicitud inválida",
            "status": "error",
            "status_code": 400,
        }), 400

    @app.errorhandler(429)
    def rate_limit(error):
        return jsonify({
            "error": "Demasiadas solicitudes. Intente nuevamente.",
            "status": "error",
            "status_code": 429,
        }), 429
