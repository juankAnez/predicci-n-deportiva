import pytest


@pytest.fixture(scope="session")
def sample_teams():
    return ["Brasil", "Argentina", "Alemania", "Francia"]


@pytest.fixture(scope="session")
def sample_match_data():
    return {
        "home_team_id": 1,
        "away_team_id": 2,
        "home_score": 2,
        "away_score": 1,
        "match_date": "2024-01-15",
    }
