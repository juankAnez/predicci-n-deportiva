import pytest
from src.api.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_overview_endpoint(client):
    res = client.get("/api/v1/stats/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "total_matches" in data["data"]
    assert data["data"]["total_matches"] > 0
    assert "total_teams" in data["data"]


def test_api_teams_endpoint(client):
    res = client.get("/api/v1/teams")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0
    assert "id" in data["data"][0]
    assert "name" in data["data"][0]


def test_api_matches_endpoint(client):
    res = client.get("/api/v1/matches?per_page=5")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) == 5
    first = data["data"][0]
    assert "home_team_name" in first
    assert "away_team_name" in first


def test_api_prediction_with_odds(client):
    # Match 100 has real data in sqlite
    res = client.get("/api/v1/predictions/100?h_odds=2.20&d_odds=3.40&a_odds=3.30")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    pred = data["data"]
    assert "result" in pred
    assert "home_win" in pred["result"]
    assert "market_analysis" in pred
    assert pred["market_analysis"] is not None
    assert "best_bet" in pred["market_analysis"]


def test_api_simulate_endpoint(client):
    res = client.get("/api/v1/predictions/simulate?home_team_id=1&away_team_id=2&h_odds=2.10&d_odds=3.20&a_odds=3.50")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    pred = data["data"]
    assert "teams" in pred
    assert "result" in pred
    assert "market_analysis" in pred

