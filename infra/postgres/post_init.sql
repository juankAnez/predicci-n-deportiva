-- Ejecutar DESPUÉS de que SQLAlchemy haya creado las tablas:
--   docker exec -i predicci-n-deportiva-postgres-1 psql -U prediccion_user -d prediccion_deportiva < infra/postgres/post_init.sql

CREATE INDEX IF NOT EXISTS idx_matches_team_date ON matches(home_team_id, match_date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_away_team_date ON matches(away_team_id, match_date DESC);
CREATE INDEX IF NOT EXISTS idx_team_stats_team_date ON team_stats(team_id, match_id DESC);
CREATE INDEX IF NOT EXISTS idx_rankings_latest ON rankings(ranking_type, rank_date DESC, rank ASC);

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.team_form AS
SELECT
    team_id,
    COUNT(*) as games_played,
    AVG(CASE WHEN is_home THEN goals ELSE NULL END) as home_goals_avg,
    AVG(CASE WHEN NOT is_home THEN goals ELSE NULL END) as away_goals_avg,
    AVG(possession) as avg_possession,
    AVG(xg) as avg_xg,
    AVG(passing_accuracy) as avg_passing_accuracy,
    AVG(corners) as avg_corners,
    AVG(ppda) as avg_ppda
FROM team_stats
GROUP BY team_id;

CREATE INDEX IF NOT EXISTS idx_team_form_team ON analytics.team_form(team_id);

CREATE OR REPLACE FUNCTION refresh_team_form()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.team_form;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS refresh_team_form_trigger ON team_stats;
CREATE TRIGGER refresh_team_form_trigger
AFTER INSERT OR UPDATE ON team_stats
EXECUTE FUNCTION refresh_team_form();
