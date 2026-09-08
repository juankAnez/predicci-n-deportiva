#!/usr/bin/env python
"""Runner script to launch the Predicción Deportiva API Server."""
import sys
from pathlib import Path

# Add backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.api.app import app
from src.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("  INICIANDO SERVIDOR BACKEND - PREDICCIÓN DEPORTIVA")
    print("=" * 60)
    print(f"  API Server activo en: http://localhost:{settings.API_PORT}")
    print(f"  Endpoint de prueba:  http://localhost:{settings.API_PORT}/api/v1/stats/overview")
    print("=" * 60)
    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.DEBUG,
    )

