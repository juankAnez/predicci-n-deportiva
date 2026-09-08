from typing import Any, Dict, List, Optional

from src.config import settings
from src.infrastructure.scraping.scrapers import (
    FifaRankingSpider,
    EloRankingSpider,
    UnderstatSpider,
    TransfermarktSpider,
    WeatherSpider,
)


class ScrapingManager:
    def __init__(self):
        self.spiders = {
            "fifa_ranking": FifaRankingSpider(),
            "elo_ranking": EloRankingSpider(),
            "understat": UnderstatSpider(),
            "transfermarkt": TransfermarktSpider(),
            "weather": WeatherSpider(),
        }

    def scrape_rankings(self, ranking_type: str = "all") -> List[Dict[str, Any]]:
        results = []
        if ranking_type in ("all", "fifa"):
            fifa_data = self.spiders["fifa_ranking"].scrape()
            results.extend(fifa_data)
        if ranking_type in ("all", "elo"):
            elo_data = self.spiders["elo_ranking"].scrape()
            results.extend(elo_data)
        return results

    def scrape_team_squad(self, team_name: str) -> List[Dict[str, Any]]:
        return self.spiders["transfermarkt"].scrape(team_name=team_name)

    def scrape_xg_data(self) -> List[Dict[str, Any]]:
        return self.spiders["understat"].scrape()

    def scrape_weather(self, city: str, date: str) -> Optional[Dict[str, Any]]:
        return self.spiders["weather"].scrape(city=city, date=date)

    def close_all(self):
        for spider in self.spiders.values():
            pass
