CREATE TABLE IF NOT EXISTS collections (
    id  SERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    kind        TEXT NOT NULL,
    title       TEXT,
    items_count INTEGER NOT NULL DEFAULT 0,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS collection_items (
    id             BIGSERIAL PRIMARY KEY,
    collection_id  INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    position       INTEGER NOT NULL,
    kp_id          INTEGER,
    title_ru       TEXT,
    title_en       TEXT,
    year           INTEGER,
    type           TEXT,
    rating_kp      NUMERIC(3,1),
    rating_imdb    NUMERIC(3,1),
    length_min     INTEGER,
    premiere_ru    DATE,
    genres         TEXT[],
    countries      TEXT[],
    poster_url     TEXT,
    poster_preview TEXT,
    description    TEXT,
    raw            JSONB,
    fetch_status   TEXT NOT NULL DEFAULT 'stub',
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (collection_id, position)
);

CREATE INDEX IF NOT EXISTS collection_items_kp_id_idx
    ON collection_items (kp_id);

CREATE INDEX IF NOT EXISTS collection_items_collection_idx
    ON collection_items (collection_id, position);

