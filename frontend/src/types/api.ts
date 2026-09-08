export interface ApiResponse<T> {
  status: string;
  data: T;
  error?: string;
}

export interface OverviewStats {
  total_matches: number;
  total_teams: number;
  finished_matches: number;
  upcoming_matches?: number;
  models_active: number;
  supported_leagues: {
    id: string | number;
    name: string;
    country: string;
    code: string;
  }[];
}

export interface Team {
  id: number;
  name: string;
  full_name?: string;
  short_name?: string;
  country?: string;
  league?: string;
  league_code?: string;
  confederation?: string;
  competition_id?: number;
  competitions?: string[];
  is_ucl?: boolean;
  is_uel?: boolean;
}

export interface Match {
  id: number;
  date: string | null;
  time?: string | null;
  home_team_id: number;
  away_team_id: number;
  home_team_name: string;
  away_team_name: string;
  home_score: number | null;
  away_score: number | null;
  stage: string | null;
  competition_id: number;
  league?: string;
  league_code?: string;
  country?: string;
  venue?: string | null;
  stadium?: string | null;
  is_finished: boolean;
  odds?: {
    h: number;
    d: number;
    a: number;
  };
}

export interface MatchesResponse {
  status: string;
  data: Match[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface BettingOpportunity {
  outcome: 'H' | 'D' | 'A';
  label: string;
  odds: number;
  model_prob_pct: number;
  market_implied_prob_pct: number;
  fair_prob_pct: number;
  ev_pct: number;
  has_value: boolean;
  suggested_stake_bankroll_pct: number;
}

export interface BestBet {
  outcome: 'H' | 'D' | 'A';
  label: string;
  odds: number;
  ev_pct: number;
  suggested_stake_bankroll_pct: number;
  model_prob_pct: number;
  fair_prob_pct: number;
  market_implied_prob_pct: number;
  has_value: boolean;
}

export interface MarketAnalysis {
  bookmaker: string;
  margin_percentage: number;
  market_fair_probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
  };
  opportunities: BettingOpportunity[];
  best_bet: BestBet | null;
}

export interface Player {
  id: number;
  name: string;
  full_name?: string;
  team_id: number;
  position: 'GK' | 'DF' | 'MF' | 'FW' | string;
  shirt_number?: number;
  age?: number;
  nationality?: string;
  market_value_eur: number;
  rating: number;
  goals: number;
  assists: number;
  xg?: number;
  xa?: number;
  tackles?: number;
  passing_accuracy?: number;
}

export interface SquadAnalysis {
  home_squad: Player[];
  away_squad: Player[];
  home_avg_rating: number;
  away_avg_rating: number;
  rating_diff: number;
}

export interface PredictionResult {
  match_id: number;
  prediction_date: string;
  teams: {
    home: string;
    away: string;
  };
  result: {
    home_win: { probability: number; label: string };
    draw: { probability: number; label: string };
    away_win: { probability: number; label: string };
    predicted: 'H' | 'D' | 'A';
    confidence: number;
  };
  goals: {
    home_expected: number;
    away_expected: number;
    total_expected: number;
    most_likely_score: string | null;
    most_likely_score_probability: number;
    exact_scores: Record<string, number>;
  };
  over_under: {
    [key: string]: number;
  };
  explanation: {
    top_features: ([string, number] | { name: string; importance: number })[];
    method: string;
    summary: string;
  };
  model_info: {
    models_used: number;
    agreement: number;
    std_dev: number;
  };
  market_analysis?: MarketAnalysis | null;
  squad_analysis?: SquadAnalysis | null;
}

export interface ModelRecord {
  id: number;
  model_name: string;
  version: string;
  model_type: string;
  status: string;
  is_ensemble: boolean;
  feature_count: number;
  training_date: string | null;
  f1_score: number | null;
  log_loss: number | null;
  accuracy: number | null;
}
