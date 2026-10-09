from psycopg2 import pool

from project.utils.config import settings

_pool: pool.ThreadedConnectionPool | None = None


# создаёт пул (набор заранее открытых соединений с PG), если он ещё не создан
def init_db_pool():
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(1, 10, dsn=settings.database_url)


# берёт соединение из пула
def get_connection():
    if _pool is None:
        raise RuntimeError("DB pool is not initialized")
    return _pool.getconn()


# возвращает соединение в пул
def release_connection(conn):
    _pool.putconn(conn)
