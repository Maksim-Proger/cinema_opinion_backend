from app.core.database import get_connection, release_connection

class CollectionRepository:

    @staticmethod
    def existing_codes(kind: str) -> set[str]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT code FROM collections WHERE kind = %s", (kind,))
                return {row[0] for row in cur.fetchall()}
        finally:
            release_connection(conn)

    @staticmethod
    def save_collection(code: str, kind: str, title: str, items: list[dict]) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO collections (code, kind, title, items_count, updated_at)
                    VALUES (%s, %s, %s, %s, now())
                    ON CONFLICT (code) DO UPDATE SET
                        kind = EXCLUDED.kind,
                        title = EXCLUDED.title,
                        items_count = EXCLUDED.items_count,
                        updated_at = now()
                    RETURNING id
                    """,
                    (code, kind, title, len(items))
                )
                collection_id = cur.fetchone()[0]

                cur.execute(
                    "DELETE FROM collection_items WHERE collection_id = %s",
                    (collection_id,)
                )

                if items:
                    cur.executemany(
                        """
                        INSERT INTO collection_items (
                            collection_id, position, kp_id, title_ru, title_en,
                            year, type, rating_kp, rating_imdb, length_min,
                            premiere_ru, genres, countries,
                            poster_url, poster_preview, raw
                        )
                        VALUES (
                            %(collection_id)s, %(position)s, %(kp_id)s, %(title_ru)s, %(title_en)s,
                            %(year)s, %(type)s, %(rating_kp)s, %(rating_imdb)s, %(length_min)s,
                            %(premiere_ru)s, %(genres)s, %(countries)s,
                            %(poster_url)s, %(poster_preview)s, %(raw)s
                        )
                        """,
                        [{**item, "collection_id": collection_id} for item in items]
                    )
            conn.commit()
            return collection_id
        except Exception:
            conn.rollback()
            raise
        finally:
            release_connection(conn)