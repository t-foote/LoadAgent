-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- loads table
CREATE TABLE IF NOT EXISTS loads (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin_city   TEXT NOT NULL,
  origin_state  TEXT,
  dest_city     TEXT NOT NULL,
  dest_state    TEXT,
  equipment     TEXT NOT NULL,
  pickup_ts     TIMESTAMPTZ NOT NULL,
  distance_mi   NUMERIC NOT NULL,
  offer_rate    NUMERIC NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- materialized view for selecting the best load by RPM per lane
CREATE MATERIALIZED VIEW IF NOT EXISTS best_load AS
SELECT
  id,
  origin_city,
  origin_state,
  dest_city,
  dest_state,
  equipment,
  pickup_ts,
  distance_mi,
  offer_rate,
  (offer_rate / NULLIF(distance_mi, 0)) AS rpm,
  ROW_NUMBER() OVER (
    PARTITION BY origin_city, dest_city, equipment
    ORDER BY (offer_rate / NULLIF(distance_mi, 0)) DESC, pickup_ts
  ) AS rank
FROM loads;

-- calls table
CREATE TABLE IF NOT EXISTS calls (
  id               BIGSERIAL PRIMARY KEY,
  mc_number        TEXT NOT NULL,
  load_id          UUID REFERENCES loads(id) ON DELETE CASCADE,
  status           TEXT NOT NULL CHECK (status IN ('BOOKED','NO DEAL','NOT ELIGIBLE')),
  negotiated_rate  NUMERIC,
  sentiment        TEXT,
  recorded_at      TIMESTAMPTZ DEFAULT now()
);
