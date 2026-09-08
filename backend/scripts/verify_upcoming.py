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

print("\n--- 3. Testing Prediction on upcoming match (Real Madrid vs Rayo Vallecano) ---")
rm_rv = next(m for m in data if m["home_team_name"] == "Real Madrid" and m["away_team_name"] == "Vallecano")
print(f"Testing match: {rm_rv['home_team_name']} vs {rm_rv['away_team_name']} on {rm_rv['date']} at {rm_rv['venue']}")
pred_res = client.get(f"/api/v1/predictions/{rm_rv['id']}?h_odds=1.22&d_odds=6.50&a_odds=12.00")
assert pred_res.status_code == 200, pred_res.data
pred = pred_res.get_json()["data"]
print("Prediction Result:", pred["result"])
print("Expected Goals:", pred["goals"])
print("Market Value Opportunities:", len(pred["market_analysis"]["opportunities"]))
print("Best Bet:", pred["market_analysis"]["best_bet"])

print("\n--- 4. Checking Osasuna match ---")
osa_esp = next(m for m in data if m["home_team_name"] == "Osasuna")
print(f"Osasuna fixture: {osa_esp['home_team_name']} vs {osa_esp['away_team_name']} on {osa_esp['date']} at {osa_esp['venue']}")
assert osa_esp["away_team_name"] == "Espanol"
assert osa_esp["date"] == "2026-09-14"

print("\n--- 5. Testing GET /api/v1/teams?league=PL and league=PD ---")
teams_pl = client.get("/api/v1/teams?league=PL").get_json()["data"]
teams_pd = client.get("/api/v1/teams?league=PD").get_json()["data"]
assert all(t["country"] == "England" for t in teams_pl)
assert all(t["country"] == "Spain" for t in teams_pd)
print(f"PL teams: {len(teams_pl)} (all England)")
print(f"PD teams: {len(teams_pd)} (all Spain)")

print("\nAll verifications PASSED successfully!")

