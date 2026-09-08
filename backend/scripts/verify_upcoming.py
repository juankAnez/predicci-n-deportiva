import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from src.api.app import create_app

app = create_app()
client = app.test_client()

print("--- 1. Testing GET /api/v1/matches?status=upcoming&league=PL ---")
res = client.get("/api/v1/matches?status=upcoming&league=PL")
assert res.status_code == 200, res.data
data = res.get_json()["data"]
print(f"Loaded {len(data)} Premier League upcoming matches:")
for m in data:
    print(f"  [{m['league']}] {m['date']} {m['time']} -> {m['home_team_name']} vs {m['away_team_name']} (Odds: {m['odds']})")
    assert m["league"] == "Premier League"
    assert m["home_score"] is None

print("\n--- 2. Testing GET /api/v1/matches?status=upcoming&league=PD ---")
res = client.get("/api/v1/matches?status=upcoming&league=PD")
assert res.status_code == 200, res.data
data = res.get_json()["data"]
print(f"Loaded {len(data)} La Liga upcoming matches:")
for m in data:
    print(f"  [{m['league']}] {m['date']} {m['time']} -> {m['home_team_name']} vs {m['away_team_name']} (Odds: {m['odds']})")
    assert m["league"] == "La Liga"
    assert m["home_score"] is None

print("\n--- 3. Testing Prediction on upcoming match (Tottenham vs Arsenal) ---")
tot_ars = next(m for m in data if m["home_team_name"] == "Betis" or m["home_team_name"] == "Tottenham")
pred_res = client.get(f"/api/v1/predictions/{tot_ars['id']}?h_odds=2.90&d_odds=3.60&a_odds=2.35")
assert pred_res.status_code == 200, pred_res.data
pred = pred_res.get_json()["data"]
print("Prediction Result:", pred["result"])
print("Expected Goals:", pred["goals"])
print("Market Value Opportunities:", len(pred["market_analysis"]["opportunities"]))
print("Best Bet:", pred["market_analysis"]["best_bet"])

print("\n--- 4. Testing GET /api/v1/teams?league=PL and league=PD ---")
teams_pl = client.get("/api/v1/teams?league=PL").get_json()["data"]
teams_pd = client.get("/api/v1/teams?league=PD").get_json()["data"]
assert all(t["country"] == "England" for t in teams_pl)
assert all(t["country"] == "Spain" for t in teams_pd)
print(f"PL teams: {len(teams_pl)} (all England)")
print(f"PD teams: {len(teams_pd)} (all Spain)")

print("\nAll verifications PASSED successfully!")
