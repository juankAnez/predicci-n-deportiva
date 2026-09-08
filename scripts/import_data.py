#!/usr/bin/env python
"""Script to import historical football data and initialize rankings"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.etl.dataset_importer import DatasetImporter
from src.infrastructure.database.connection import init_db


def main():
    print("=" * 60)
    print("  PREDICCIÓN DEPORTIVA - Importación de Datos Reales")
    print("=" * 60)

    print("\n[1/3] Inicializando tablas de base de datos...")
    init_db()

    print("\n[2/3] Descargando e importando ligas principales...")
    importer = DatasetImporter()
    # Import La Liga and Premier League recent seasons
    results = importer.import_all(
        leagues=["la-liga", "premier-league"],
        seasons=["2223", "2324", "2425"]
    )

    total = sum(results.values())
    print("\n[3/3] Resumen de importación:")
    for league, count in results.items():
        print(f"  - {league}: {count} partidos")
    print(f"\n[OK] Total partidos cargados: {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
