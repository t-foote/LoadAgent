-- db/schema.sql

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS loads (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin_city   TEXT,
  origin_state  TEXT,
  dest_city     TEXT,
  dest_state    TEXT,
  equipment     TEXT,
  pickup_ts     TIMESTAMPTZ,
  distance_mi   NUMERIC,
  offer_rate    NUMERIC,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- materialized view 
CREATE MATERIALIZED VIEW IF NOT EXISTS best_load AS
  SELECT
    id,
    origin_city,
    dest_city,
    equipment,
    pickup_ts,
    distance_mi,
    offer_rate,
    (offer_rate / distance_mi) AS rpm,
    ROW_NUMBER() OVER (
      PARTITION BY origin_city, dest_city
      ORDER BY (offer_rate / distance_mi) DESC, pickup_ts
    ) AS rank
  FROM loads;

-- calls table
CREATE TABLE IF NOT EXISTS calls (
  id               BIGSERIAL PRIMARY KEY,
  mc_number        TEXT,
  load_id          UUID REFERENCES loads(id),
  status           TEXT CHECK (status IN ('BOOKED','NO DEAL','NOT ELIGIBLE')),
  negotiated_rate  NUMERIC,
  sentiment        TEXT,
  recorded_at      TIMESTAMPTZ DEFAULT now()
);
