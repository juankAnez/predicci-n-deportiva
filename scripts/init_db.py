#!/usr/bin/env python
"""Initialize database tables"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.infrastructure.database.connection import engine, init_db
from src.infrastructure.database.models import Base


def main():
    print(f"Inicializando base de datos: {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    main()
