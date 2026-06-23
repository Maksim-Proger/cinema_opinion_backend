CREATE TABLE IF NOT EXISTS avatars (
    avatar_id    UUID NOT NULL,
    user_id      TEXT NOT NULL UNIQUE,
    file_name    TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes   INTEGER NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (avatar_id)
);
