import type {
  ApiResponse,
  OverviewStats,
  Team,
  MatchesResponse,
  PredictionResult,
  ModelRecord,
  Player,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `Error HTTP ${res.status}: ${res.statusText}`;
    try {
      const json = await res.json();
      if (json && json.error) errorMsg = json.error;
    } catch {
      // no json error body
    }
    throw new Error(errorMsg);
  }
  const json: ApiResponse<T> = await res.json();
  return json.data;
}

export async function fetchOverview(): Promise<OverviewStats> {
  const res = await fetch(`${API_BASE_URL}/stats/overview`);
  return handleResponse<OverviewStats>(res);
}

export async function fetchTeams(league?: string): Promise<Team[]> {
  const params = new URLSearchParams();
  if (league) params.set('league', league);
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${API_BASE_URL}/teams${query}`);
  return handleResponse<Team[]>(res);
}

export async function fetchMatches(
  page: number = 1,
  perPage: number = 12,
  league?: string,
  teamId?: number,
  status?: string
): Promise<MatchesResponse> {
  const params = new URLSearchParams();
  params.set('page', page.toString());
  params.set('per_page', perPage.toString());
  if (league) params.set('league', league);
  if (teamId) params.set('team_id', teamId.toString());
  if (status) params.set('status', status);

  const res = await fetch(`${API_BASE_URL}/matches?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar partidos');
  return res.json();
}

export async function fetchTeamPlayers(teamId: number): Promise<Player[]> {
  const res = await fetch(`${API_BASE_URL}/players/team/${teamId}`);
  return handleResponse<Player[]>(res);
}

export async function fetchPrediction(
  matchId: number,
  odds?: { h_odds?: number; d_odds?: number; a_odds?: number },
  benchedHome?: number[],
  benchedAway?: number[]
): Promise<PredictionResult> {
  const params = new URLSearchParams();
  if (odds?.h_odds && odds?.d_odds && odds?.a_odds) {
    params.set('h_odds', odds.h_odds.toString());
    params.set('d_odds', odds.d_odds.toString());
    params.set('a_odds', odds.a_odds.toString());
  }
  if (benchedHome && benchedHome.length > 0) {
    params.set('benched_home', benchedHome.join(','));
  }
  if (benchedAway && benchedAway.length > 0) {
    params.set('benched_away', benchedAway.join(','));
  }
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${API_BASE_URL}/predictions/${matchId}${query}`);
  return handleResponse<PredictionResult>(res);
}

export async function simulateMatch(
  homeTeamId: number,
  awayTeamId: number,
  odds?: { h_odds?: number; d_odds?: number; a_odds?: number },
  benchedHome?: number[],
  benchedAway?: number[]
): Promise<PredictionResult> {
  const body: Record<string, any> = {
    home_team_id: homeTeamId,
    away_team_id: awayTeamId,
  };
  if (odds?.h_odds && odds?.d_odds && odds?.a_odds) {
    body.h_odds = odds.h_odds;
    body.d_odds = odds.d_odds;
    body.a_odds = odds.a_odds;
  }
  if (benchedHome && benchedHome.length > 0) {
    body.benched_home = benchedHome;
  }
  if (benchedAway && benchedAway.length > 0) {
    body.benched_away = benchedAway;
  }

  const res = await fetch(`${API_BASE_URL}/predictions/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse<PredictionResult>(res);
}

export async function submitMatchResult(
  matchId: number,
  homeScore: number,
  awayScore: number
): Promise<{ match_id: number; home_score: number; away_score: number; is_finished: boolean }> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/result`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ home_score: homeScore, away_score: awayScore }),
  });
  return handleResponse(res);
}

export async function recordPlayerMatchStats(
  playerId: number,
  matchId: number,
  stats: {
    team_id: number;
    position?: string;
    rating: number;
    goals?: number;
    assists?: number;
    xg?: number;
    xa?: number;
    passes_total?: number;
    passing_accuracy?: number;
    tackles?: number;
  }
): Promise<{ player_id: number; new_overall_rating: number }> {
  const res = await fetch(`${API_BASE_URL}/players/${playerId}/stats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ match_id: matchId, ...stats }),
  });
  return handleResponse(res);
}

export async function fetchModels(): Promise<ModelRecord[]> {
  const res = await fetch(`${API_BASE_URL}/models`);
  return handleResponse<ModelRecord[]>(res);
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/stats/overview`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}
