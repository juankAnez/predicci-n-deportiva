import type {
  ApiResponse,
  OverviewStats,
  Team,
  MatchesResponse,
  PredictionResult,
  ModelRecord,
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

export async function fetchTeams(): Promise<Team[]> {
  const res = await fetch(`${API_BASE_URL}/teams`);
  return handleResponse<Team[]>(res);
}

export async function fetchMatches(
  page: number = 1,
  perPage: number = 15,
  competitionId?: number,
  teamId?: number
): Promise<MatchesResponse> {
  const params = new URLSearchParams();
  params.set('page', page.toString());
  params.set('per_page', perPage.toString());
  if (competitionId) params.set('competition_id', competitionId.toString());
  if (teamId) params.set('team_id', teamId.toString());

  const res = await fetch(`${API_BASE_URL}/matches?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar partidos');
  return res.json();
}

export async function fetchPrediction(
  matchId: number,
  odds?: { h_odds?: number; d_odds?: number; a_odds?: number }
): Promise<PredictionResult> {
  const params = new URLSearchParams();
  if (odds?.h_odds && odds?.d_odds && odds?.a_odds) {
    params.set('h_odds', odds.h_odds.toString());
    params.set('d_odds', odds.d_odds.toString());
    params.set('a_odds', odds.a_odds.toString());
  }
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${API_BASE_URL}/predictions/${matchId}${query}`);
  return handleResponse<PredictionResult>(res);
}

export async function simulateMatch(
  homeTeamId: number,
  awayTeamId: number,
  odds?: { h_odds?: number; d_odds?: number; a_odds?: number }
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

  const res = await fetch(`${API_BASE_URL}/predictions/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse<PredictionResult>(res);
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
