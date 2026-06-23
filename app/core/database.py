from psycopg2 import pool
from app.core.config import settings

_pool: pool.SimpleConnectionPool | None = None


def init_db_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(1, 10, dsn=settings.database_url)


def get_connection():
    if _pool is None:
        raise RuntimeError("DB pool is not initialized")
    return _pool.getconn()


def release_connection(conn):
    _pool.putconn(conn)
