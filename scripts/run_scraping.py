#!/usr/bin/env python
"""Run the scraping process for all data sources"""

from src.infrastructure.scraping.middleware import ScrapingManager


def main():
    print("=" * 60)
    print("  PREDICCIÓN DEPORTIVA - Scraping Manager")
    print("=" * 60)

    manager = ScrapingManager()

    print("\n[1/2] Scraping rankings...")
    rankings = manager.scrape_rankings("all")
    print(f"  → {len(rankings)} rankings obtenidos")

    print("\n[2/2] Scraping completado.")

    manager.close_all()
    print("\n✓ Proceso finalizado.")


if __name__ == "__main__":
    main()
