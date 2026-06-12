from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import settings
from src.infrastructure.database.connection import db_session
from src.infrastructure.database.models import ScrapingLogModel


class BaseSpider(ABC):
    BASE_URL = ""
    SOURCE_NAME = "base"

    def __init__(self):
        self.session = self._create_session()
        self.db = db_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        return session

    def fetch(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            self.log_error(f"Error fetching {url}: {e}")
            return None

    def fetch_json(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            self.log_error(f"Error fetching JSON from {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        pass

    def log_start(self, url: str, data_type: str) -> datetime:
        log = ScrapingLogModel(
            source=self.SOURCE_NAME,
            url=url,
            data_type=data_type,
            status="started",
            started_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
        return log.created_at

    def log_success(self, url: str, data_type: str, items_count: int, start_time: datetime):
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        log = ScrapingLogModel(
            source=self.SOURCE_NAME,
            url=url,
            data_type=data_type,
            status="success",
            items_count=items_count,
            started_at=start_time,
            finished_at=datetime.utcnow(),
            duration_ms=int(duration),
        )
        self.db.add(log)
        self.db.commit()

    def log_error(self, message: str):
        print(f"[{self.SOURCE_NAME}] ERROR: {message}")

    def __del__(self):
        if self.db:
            self.db.close()
