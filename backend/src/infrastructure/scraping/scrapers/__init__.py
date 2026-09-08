from datetime import datetime
from typing import Any, Dict, List, Optional

from src.config import settings
from src.infrastructure.scraping.base_spider import BaseSpider


class FifaRankingSpider(BaseSpider):
    SOURCE_NAME = "fifa_ranking"
    BASE_URL = "https://api.fifa.com/api/v3/ranking"

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/men"
        data = self.fetch_json(url)
        if not data:
            return []

        rankings = []
        results = data.get("results", [])
        for entry in results:
            rankings.append({
                "rank": entry.get("rank"),
                "previous_rank": entry.get("previousRank"),
                "team_name": entry.get("name", ""),
                "team_code": entry.get("abbreviation", ""),
                "country": entry.get("countryName", ""),
                "confederation": entry.get("confederationName", ""),
                "points": entry.get("totalPoints"),
                "rank_date": datetime.now().strftime("%Y-%m-%d"),
                "ranking_type": "fifa",
            })

        return rankings


class EloRankingSpider(BaseSpider):
    SOURCE_NAME = "elo_ranking"
    BASE_URL = "https://www.eloratings.net"

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/world.json"
        data = self.fetch_json(url)
        if not data:
            return []

        rankings = []
        for entry in data:
            rankings.append({
                "rank": entry.get("rank", 0),
                "previous_rank": entry.get("prevRank"),
                "team_name": entry.get("country", ""),
                "team_code": entry.get("code", ""),
                "points": entry.get("elo", 0),
                "change_points": entry.get("change", 0),
                "rank_date": datetime.now().strftime("%Y-%m-%d"),
                "ranking_type": "elo",
            })

        return rankings


class UnderstatSpider(BaseSpider):
    SOURCE_NAME = "understat"
    BASE_URL = "https://understat.com"

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        # Understat no tiene API pública, scrapeamos datos de xG
        # Nota: Understat bloquea scraping; usar con precaución
        return []


class TransfermarktSpider(BaseSpider):
    SOURCE_NAME = "transfermarkt"
    BASE_URL = "https://www.transfermarkt.com"

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        # Transfermarkt requiere headers específicos
        # Se implementa bajo demanda para equipos específicos
        return []


class WeatherSpider(BaseSpider):
    SOURCE_NAME = "weather_api"
    BASE_URL = "https://api.weatherapi.com/v1"

    def scrape(self, city: str, date: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not settings.WEATHER_API_KEY:
            return None
        url = f"{self.BASE_URL}/history.json"
        params = {
            "key": settings.WEATHER_API_KEY,
            "q": city,
            "dt": date,
        }
        data = self.fetch_json(url, params=params)
        if not data or "forecast" not in data:
            return None

        forecast = data["forecast"]["forecastday"][0]["day"]
        return {
            "temperature_celsius": forecast.get("avgtemp_c"),
            "humidity": forecast.get("avghumidity"),
            "condition": forecast.get("condition", {}).get("text", ""),
        }
